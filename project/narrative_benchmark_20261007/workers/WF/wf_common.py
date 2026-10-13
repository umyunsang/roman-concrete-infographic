"""WF (Figma label worker) shared measurement data, all on the 2x grid (2 px per pt, 2382 x 3368).
- map ink   = map_only_2x pixels whose RGB distance to the paper colour (mode) > 20  (same rule as measure_labels.py / verify_r11.py)
- glyphs    = poster_2x vs map_only_2x differ by > 40 in any channel (Figma text layer)
- object ID = r11 ID pass (v8_14, 1.9992 px/pt), final = overlay id if present else map id; ids = inventory objects order + 1
"""
import json
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt

NB = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work'
RL = NB + '/review_loop'
S2 = 2.0
W2, H2 = 2382, 3368


def load_ids():
    inv = json.load(open(RL + '/obj_r11/inventory.json'))
    objs = [o['name'] for o in inv['objects']]
    pxpt = inv['id_pass']['id_px_per_pt']

    def dec(p):
        a = np.asarray(Image.open(p).convert('RGBA')).astype(np.int64)
        k = np.rint((a[..., :3] - 2) / 4).astype(np.int64)
        code = k[..., 0] + 64 * k[..., 1] + 4096 * k[..., 2]
        code[a[..., 3] < 128] = 0
        return code
    m = dec(inv['id_pass']['map_png']); o = dec(inv['id_pass']['overlay_png'])
    final = np.where(o > 0, o, m)
    # resample to the 2x grid (nearest)
    X = ((np.arange(W2) + 0.5) / S2 * pxpt).astype(int).clip(0, final.shape[1] - 1)
    Y = ((np.arange(H2) + 0.5) / S2 * pxpt).astype(int).clip(0, final.shape[0] - 1)
    f2 = final[Y][:, X]
    assets = {a['id']: a['objects'] for a in inv['assets']}
    name2id = {n: i + 1 for i, n in enumerate(objs)}
    return inv, objs, name2id, final, pxpt, f2, assets


def load_maps(poster_p=RL + '/r11/poster_2x.png', map_p=RL + '/r11/map_only_2x.png'):
    po = np.asarray(Image.open(poster_p).convert('RGB')).astype(float)
    mo = np.asarray(Image.open(map_p).convert('RGB')).astype(float)
    assert po.shape == (H2, W2, 3) and mo.shape == (H2, W2, 3)
    sub = mo[::7, ::7].reshape(-1, 3).round().astype(int); v, c = np.unique(sub, axis=0, return_counts=True)
    paper = v[np.argmax(c)].astype(float)
    ink = np.linalg.norm(mo - paper, axis=2) > 20
    txt = np.abs(po - mo).max(2) > 40
    return po, mo, paper, ink, txt


def asset_mask(f2, name2id, assets, aid):
    ids = [name2id[n] for n in assets[aid] if n in name2id]
    return np.isin(f2, ids)


def dist(mask):
    return distance_transform_edt(~mask) / S2


def glyph_pts(txt, box, pad=2.0):
    x, y, w, h = box
    x0, y0 = int((x - pad) * S2), int((y - pad) * S2); x1, y1 = int(np.ceil((x + w + pad) * S2)), int(np.ceil((y + h + pad) * S2))
    ys, xs = np.nonzero(txt[y0:y1, x0:x1])
    return np.c_[xs + x0, ys + y0]          # pixel coords on 2x grid


def min_d(D, G, shift=(0.0, 0.0)):
    q = G + np.round(np.array(shift) * S2).astype(int)
    ok = (q[:, 0] >= 0) & (q[:, 0] < W2) & (q[:, 1] >= 0) & (q[:, 1] < H2)
    if not ok.all():
        return -1.0
    return float(D[q[:, 1], q[:, 0]].min())


def ink_bbox_pt(G, shift=(0.0, 0.0)):
    q = G + np.round(np.array(shift) * S2).astype(int)
    return [round(q[:, 0].min() / S2, 2), round(q[:, 1].min() / S2, 2), round((q[:, 0].max() + 1) / S2, 2), round((q[:, 1].max() + 1) / S2, 2)]
