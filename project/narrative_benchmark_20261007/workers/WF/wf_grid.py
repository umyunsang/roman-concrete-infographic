"""Full grid table for one label: every 0.5pt shift with ink/own/other/pantheon numbers (numpy-vectorised over glyph points).
Run: uv run ... python -I wf_grid.py <WF dir> <tid> <own asset> <x0 x1 y0 y1> <out.npz>"""
import sys, json; sys.path.insert(0, sys.argv[1])
from wf_common import *
tid, own = sys.argv[2], sys.argv[3]; x0, x1, y0, y1 = map(float, sys.argv[4:8]); out = sys.argv[8]
inv, objs, name2id, final, pxpt, f2, assets = load_ids()
po, mo, paper, ink, txt = load_maps()
spec = {t[0]: t for t in json.load(open(RL + '/text_spec_r11.json'))['texts']}
masks = {a: asset_mask(f2, name2id, assets, a) for a in assets}
masks['water_tiber'], masks['water_sea'] = water_masks(f2, name2id)
ink_all, ink_obj, ink_sh = map_ink_obj(f2, name2id, mo, paper)
NAMED = [a for a in assets if not (a.startswith('fields_') or a.startswith('tree') or a.startswith('road_core') or a.startswith('shape_')
                                   or a in ('ground_land', 'header_gate', 'road_ostiensis', own))]
oth = np.zeros_like(ink)
for a in NAMED: oth |= masks[a]
G = {k: glyph_pts(txt, t[1], 1.0) for k, t in spec.items()}
tm = np.zeros_like(ink)
for k, g in G.items():
    if k != tid and len(g): tm[g[:, 1], g[:, 0]] = True
maps = {'ink': dist(ink_all), 'ink_nonown': dist(ink_all & ~masks[own]), 'ink_px': dist(ink), 'own': dist(masks[own]),
        'other': dist(oth), 'text': dist(tm), 'pantheon': dist(masks['landmark_pantheon'])}
g = G[tid]
xs = np.arange(x0, x1 + 0.01, 0.5); ys = np.arange(y0, y1 + 0.01, 0.5)
res = {k: np.zeros((len(ys), len(xs))) for k in maps}
for j, dy in enumerate(ys):
    for i, dx in enumerate(xs):
        q = g + np.round(np.array((dx, dy)) * 2).astype(int)
        for k, Dm in maps.items():
            res[k][j, i] = Dm[q[:, 1], q[:, 0]].min()
np.savez(out, xs=xs, ys=ys, **res)
print('saved', out)
