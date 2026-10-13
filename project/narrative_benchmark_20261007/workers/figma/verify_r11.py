"""r11 Figma check: label glyph gaps on the exported poster, 1x downscale, 3x crops around the two moved labels.
Run: uv run -q --no-project --with pillow --with numpy --with scipy python -I verify_r11.py <poster_2x.png> <map_2x.png> <masks.npz> <out_dir>
- glyphs = poster_2x vs map_2x differ by > 40 in any channel, inside the label box (+2pt pad)
- map ink = map_2x pixels whose RGB distance to the paper colour (mode) exceeds 20 (same rule as measure_labels.py)
- Pantheon / Colosseum silhouettes from the layout worker's masks (origin X0, Y0, 4 px per pt)"""
import sys, json
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt

poster_p, map_p, masks_p, out_dir = sys.argv[1:5]
S2 = 2.0
P = Image.open(poster_p).convert('RGB')
M = Image.open(map_p).convert('RGB')
assert P.size == (2382, 3368) and M.size == (2382, 3368), (P.size, M.size)
P.resize((1191, 1684), Image.Resampling.LANCZOS).save(out_dir + '/poster_1x.png')
po = np.asarray(P).astype(float); mo = np.asarray(M).astype(float)
sub = mo[::7, ::7].reshape(-1, 3).round().astype(int); v, c = np.unique(sub, axis=0, return_counts=True)
paper = v[np.argmax(c)].astype(float)
ink = np.linalg.norm(mo - paper, axis=2) > 20
txt = np.abs(po - mo).max(2) > 40
MK = np.load(masks_p); X0, Y0, S4 = MK['origin']
H2, W2 = ink.shape


def mask_to_2x(m):
    ys, xs = np.nonzero(m)
    q = np.round(np.c_[X0 + (xs + 0.5) / S4, Y0 + (ys + 0.5) / S4] * S2 - 0.5).astype(int)
    ok = (q[:, 0] >= 0) & (q[:, 0] < W2) & (q[:, 1] >= 0) & (q[:, 1] < H2)
    out = np.zeros_like(ink); out[q[ok, 1], q[ok, 0]] = True
    return out


pan = mask_to_2x(MK['PAN']); col = mask_to_2x(MK['COL'])
d_ink = distance_transform_edt(~ink) / S2
d_nonpan = distance_transform_edt(~(ink & ~pan)) / S2
d_pan = distance_transform_edt(~pan) / S2
d_col = distance_transform_edt(~col) / S2


def glyph_mask(box, pad=2):
    x, y, w, h = box
    x0, y0 = int((x - pad) * S2), int((y - pad) * S2); x1, y1 = int((x + w + pad) * S2), int((y + h + pad) * S2)
    g = np.zeros_like(txt); g[y0:y1, x0:x1] = txt[y0:y1, x0:x1]
    return g


res = {'paper_rgb': paper.tolist(), 'pantheon_left_pt': float(np.nonzero(pan)[1].min() / S2)}
labels = {'802:78': [729.653, 620.55, 51.1, 29.5], '797:79': [294.5, 472.8, 84, 11]}
for tid, box in labels.items():
    g = glyph_mask(box)
    ys, xs = np.nonzero(g)
    r = {'box': box, 'glyph_px': int(g.sum()),
         'glyph_bbox_pt': [round(xs.min() / S2, 2), round(ys.min() / S2, 2), round((xs.max() + 1) / S2, 2), round((ys.max() + 1) / S2, 2)],
         'gap_map_ink_all_pt': round(float(d_ink[g].min()), 2),
         'glyph_on_ink_px': int((g & ink).sum())}
    if tid == '797:79':
        r['gap_map_ink_other_than_pantheon_pt'] = round(float(d_nonpan[g].min()), 2)
        r['gap_pantheon_pt'] = round(float(d_pan[g].min()), 2)
        r['pantheon_left_minus_glyph_right_pt'] = round(res['pantheon_left_pt'] - (xs.max() + 1) / S2, 2)
    else:
        r['gap_colosseum_pt'] = round(float(d_col[g].min()), 2)
    res[tid] = r
    # 3x crop (3 px per pt) around the label, 40pt margin, with the box outline in a second copy
    x, y, w, h = box
    cx0, cy0, cx1, cy1 = max(0, x - 40), max(0, y - 40), min(1191, x + w + 40), min(1684, y + h + 40)
    crop = P.crop((int(cx0 * S2), int(cy0 * S2), int(cx1 * S2), int(cy1 * S2)))
    crop = crop.resize((int((cx1 - cx0) * 3), int((cy1 - cy0) * 3)), Image.Resampling.LANCZOS)
    crop.save(f"{out_dir}/crop3x_{tid.replace(':', '_')}.png")
json.dump(res, open(out_dir + '/label_gaps_r11.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
