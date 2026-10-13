"""measure_obj.py <composite.png> <idmap.npz> <target obj[,obj2]> [--roof SUB] [--wall SUB] [--ppt 2]
Value / colour stats of one asset on the real composite (same pixel grid as idmap):
 mask M = pixels whose first hit is a target object; g = median L* of T_land pixels 2..8pt outside M (ring);
 Cmean = g - mean L*[M]; R = P95-P5; per material: median Lab by face direction (top nz>0.7, F_L / F_R = side faces
 whose normal points to screen left / right); D(0.5 deg) roof-vs-wall (Szafir 2018 ND50 0.5deg: L 6.74 a 9.98 b 13.34)."""
import sys, json, numpy as np
from PIL import Image, ImageFilter

args = sys.argv[1:]
img = np.asarray(Image.open(args[0]).convert('RGB')).astype(float) / 255
d = np.load(args[1])
targets = args[2].split(',')
opt = {args[i]: args[i + 1] for i in range(3, len(args) - 1, 2)}
ppt = float(opt.get('--ppt', 2))
names = list(d['names']); mats = list(d['mats'])
hit = d['hit']; mat = d['mat']; N = d['normal']; right = d['right']
assert img.shape[:2] == hit.shape, (img.shape, hit.shape)


def lin(c): return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lab(rgb):
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = lin(rgb) @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


LAB = lab(img)
M = np.isin(hit, [names.index(t) for t in targets if t in names])


def grow(m, r):
    return np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * r + 1))) > 0


ring = grow(M, int(8 * ppt)) & ~grow(M, int(2 * ppt))
if 'T_land' in names:
    ring &= hit == names.index('T_land')
g = float(np.median(LAB[ring][:, 0]))
Lm = LAB[M][:, 0]
res = {'px': int(M.sum()), 'g': round(g, 2), 'meanL': round(float(Lm.mean()), 2), 'Cmean': round(g - float(Lm.mean()), 2),
       'R': round(float(np.percentile(Lm, 95) - np.percentile(Lm, 5)), 2)}
side = np.abs(N[..., 2]) < 0.5
sx = N @ right
cls = {'top': N[..., 2] > 0.7, 'F_L': side & (sx < -0.2), 'F_R': side & (sx > 0.2)}
inner = ~grow(~M, 1)          # 1px eroded mask to avoid edge AA
per = {}
for k, mn in enumerate(mats):
    sel = M & inner & (mat == k)
    if sel.sum() < 20:
        continue
    e = {'px': int(sel.sum()), 'all_L': round(float(np.median(LAB[sel][:, 0])), 2)}
    for c, cm in cls.items():
        s2 = sel & cm
        if s2.sum() >= 10:
            e[c] = [round(float(v), 2) for v in np.median(LAB[s2], 0)] + [int(s2.sum())]
    per[mn] = e
res['per_material'] = per


def D(a, b, nd=(6.74, 9.98, 13.34)):
    return float(np.sqrt(sum(((a[i] - b[i]) / (2 * nd[i])) ** 2 for i in range(3))))


rsub, wsub = opt.get('--roof'), opt.get('--wall')
if rsub and wsub:
    rk = [k for k, mn in enumerate(mats) if rsub in mn]; wk = [k for k, mn in enumerate(mats) if wsub in mn]
    lit = (N[..., 2] > 0.7) | (side & (sx < -0.2))
    r = M & inner & np.isin(mat, rk) & lit; w = M & inner & np.isin(mat, wk) & lit
    if r.sum() and w.sum():
        ra, wa = np.median(LAB[r], 0), np.median(LAB[w], 0)
        to_hex = lambda m: '#%02X%02X%02X' % tuple(int(round(v * 255)) for v in np.median(img[m], 0))
        res['roof_vs_wall'] = {'roof_lit': [round(float(v), 2) for v in ra], 'wall_lit': [round(float(v), 2) for v in wa],
                               'roof_hex': to_hex(r), 'wall_hex': to_hex(w), 'D_0.5deg': round(D(ra, wa), 3)}
print(json.dumps(res, indent=1))
