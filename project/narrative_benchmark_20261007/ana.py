import json, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
Image.MAX_IMAGE_PIXELS = None
B = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/'
R = B + 'nb_work/review_loop/'
O = B + 'opb2/'
S = 3  # px per pt in analysis windows
IDX = json.load(open(R + 'obj_r11/assets_index.json'))
INV = json.load(open(R + 'obj_r11/inventory.json'))
NAMES = [o['name'] for o in INV['objects']]
ASSET = {a['id']: a for a in IDX['assets']}
OBJ_ASSETS = {}
for a in IDX['assets']:
    for n in a['objects']:
        OBJ_ASSETS.setdefault(n, []).append(a['id'])
PXPT_ID = INV['id_pass']['id_px_per_pt']

def decode(path):
    a = np.asarray(Image.open(path).convert('RGBA')).astype(np.int64)
    k = np.rint((a[..., :3] - 2) / 4).astype(np.int64)
    code = k[..., 0] + 64 * k[..., 1] + 4096 * k[..., 2]
    code[a[..., 3] < 128] = 0
    return code
_cache = {}
def ids():
    if 'ids' not in _cache:
        m = decode(R + 'obj_r11/idpass/id_id_map.png'); o = decode(R + 'obj_r11/idpass/id_id_overlay.png')
        _cache['ids'] = (m, o, np.where(o > 0, o, m))
    return _cache['ids']

def oid(name):
    return NAMES.index(name) + 1

class Win:
    def __init__(self, x0, x1, y0, y1):
        self.x0, self.y0 = float(np.floor(x0)), float(np.floor(y0))
        self.W = int(np.ceil((x1 - self.x0) * S)); self.H = int(np.ceil((y1 - self.y0) * S))
        self.ptx = self.x0 + (np.arange(self.W) + 0.5) / S
        self.pty = self.y0 + (np.arange(self.H) + 0.5) / S
    def sample(self, img, pxpt):
        xi = np.clip((self.ptx * pxpt).astype(int), 0, img.shape[1] - 1)
        yi = np.clip((self.pty * pxpt).astype(int), 0, img.shape[0] - 1)
        return img[yi][:, xi]
    def topix(self, xy):
        xy = np.asarray(xy, float)
        return np.stack([(xy[..., 0] - self.x0) * S, (xy[..., 1] - self.y0) * S], -1)
    def raster_tris(self, tris):
        im = Image.new('L', (self.W, self.H), 0); d = ImageDraw.Draw(im)
        T = self.topix(tris)
        for t in T:
            if (t[:, 0].max() < 0) or (t[:, 1].max() < 0) or (t[:, 0].min() > self.W) or (t[:, 1].min() > self.H):
                continue
            d.polygon([tuple(p) for p in t], fill=255)
        return np.asarray(im) > 0
    def raster_poly(self, poly):
        im = Image.new('L', (self.W, self.H), 0); d = ImageDraw.Draw(im)
        d.polygon([tuple(p) for p in self.topix(poly)], fill=255)
        return np.asarray(im) > 0

def win_for(aid, margin=25):
    c = ASSET[aid]['crop_pt']
    return Win(c[0] - margin, c[1] + margin, c[2] - margin, c[3] + margin)

def iso_alpha(aid, w):
    """M_A full silhouette from isolated_rgba resampled into window"""
    a = ASSET[aid]; c = a['crop_pt']
    al = np.asarray(Image.open(a['files']['isolated_rgba']))[..., 3]
    out = np.zeros((w.H, w.W), bool)
    xi = ((w.ptx - c[0]) * 3).astype(int); yi = ((w.pty - c[2]) * 3).astype(int)
    okx = (xi >= 0) & (xi < al.shape[1]) & (w.ptx >= c[0]); oky = (yi >= 0) & (yi < al.shape[0]) & (w.pty >= c[2])
    sub = al[np.clip(yi, 0, al.shape[0] - 1)][:, np.clip(xi, 0, al.shape[1] - 1)] >= 128
    out[np.ix_(oky, okx)] = sub[np.ix_(oky, okx)]
    return out

def vis_mask(w, names, which='final'):
    m, o, f = ids()
    img = {'final': f, 'map': m, 'overlay': o}[which]
    sub = w.sample(img, PXPT_ID)
    return np.isin(sub, [oid(n) for n in names])

def asset_of_code(code):
    if code == 0: return None
    return OBJ_ASSETS.get(NAMES[code - 1], ['?'])[0]

def tris(name):
    return np.load(O + f'tri_{name}.npy')

def edt_dist(mask):
    """distance (pt) from each pixel to nearest True pixel of mask"""
    if not mask.any():
        return np.full(mask.shape, np.inf)
    return ndi.distance_transform_edt(~mask) / S

def gap(a, b):
    if not a.any() or not b.any(): return None
    return float(edt_dist(b)[a].min())

def overlap_thick(a, b):
    ov = a & b
    if not ov.any(): return 0.0
    return float(ndi.distance_transform_edt(ov).max() / S * 2)

def signed_gap(a, b):
    ov = a & b
    if ov.any():
        return -overlap_thick(a, b)
    return gap(a, b)

# --- text ink
TS = json.load(open(R + 'text_spec_r11.json'))
def text_ink(w, pad=3, ids_only=None):
    """ink mask of Figma text inside window: poster vs map-only difference + ink criterion; returns mask and per-text id masks"""
    if 'post' not in _cache:
        _cache['post'] = np.asarray(Image.open(R + 'r11/poster_2x.png').convert('RGB')).astype(np.int16)
        _cache['mapo'] = np.asarray(Image.open(R + 'r11/map_only_2x.png').convert('RGB')).astype(np.int16)
    P = w.sample(_cache['post'], 2.0); M = w.sample(_cache['mapo'], 2.0)
    L = 0.299 * P[..., 0] + 0.587 * P[..., 1] + 0.114 * P[..., 2]
    red = (P[..., 0] - P[..., 1] > 40) & (P[..., 0] > 100) & (L < 170)
    diff = np.abs(P - M).sum(-1) > 30
    ink = ((L < 140) | red) & diff
    per = {}
    for t in TS['texts']:
        tid, (x, y, ww, hh) = t[0], t[1]
        if ids_only and tid not in ids_only: continue
        bx = np.zeros_like(ink)
        xs = (w.ptx >= x - pad) & (w.ptx <= x + ww + pad); ys = (w.pty >= y - pad) & (w.pty <= y + hh + pad)
        if not xs.any() or not ys.any(): continue
        bx[np.ix_(ys, xs)] = True
        m = ink & bx
        if m.any():
            per[tid] = m
    allm = np.zeros_like(ink)
    for m in per.values(): allm |= m
    return allm, per

def text_str(tid):
    for t in TS['texts']:
        if t[0] == tid: return ''.join(s[0] for s in t[4]).replace('\n', '/')
