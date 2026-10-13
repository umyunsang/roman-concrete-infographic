"""Screen gaps of MS3 from <prefix>_tris.npz (verify_export.py), independent of step.py's grid method.
Run: python3 -I verify_measure.py <prefix> <out.json>
Same method as workers/layout/measure.py: filled projected triangles at 4 px/pt (PIL), scipy EDT,
gap = (min EDT from MS3 over the other mask - 1px)/4 pt; overlap in pt2. Text boxes: text_spec_r10.json."""
import sys, json
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt

pre, outp = sys.argv[1], sys.argv[2]
SPEC = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/text_spec_r10.json'
Z = np.load(pre + '_tris.npz'); chk = json.load(open(pre + '_check.json'))
X0, X1, Y0, Y1 = [int(v) for v in chk['box']]
S = 4.0; Wd, Hd = int((X1 - X0) * S), int((Y1 - Y0) * S)


def raster(tri):
    im = Image.new('1', (Wd, Hd), 0); dr = ImageDraw.Draw(im)
    for t in (tri - np.array((X0, Y0))) * S:
        dr.polygon([tuple(p) for p in t], fill=1, outline=1)
    return np.array(im, bool)


ms = raster(Z['MS3_core34_to_5']); arrow = raster(Z['__MS3_arrow'])
edt = distance_transform_edt(~ms)
ROADS = ('R_', 'R1_', 'R4_bridge', 'B_pons')
COLG = ('COL_ruined', 'R3_colosseum_podium', 'R4_arena_skin')
res = {'ms3_box_pt': [round(X0 + np.nonzero(ms.any(0))[0].min() / S, 2), round(X0 + (np.nonzero(ms.any(0))[0].max() + 1) / S, 2),
                      round(Y0 + np.nonzero(ms.any(1))[0].min() / S, 2), round(Y0 + (np.nonzero(ms.any(1))[0].max() + 1) / S, 2)],
       'ms3_area_pt2': round(float(ms.sum()) / S / S, 1), 'arrow_area_pt2': round(float(arrow.sum()) / S / S, 1), 'objects': {}}
for n in Z.files:
    if n in ('MS3_core34_to_5', '__MS3_arrow'): continue
    m = raster(Z[n])
    if not m.any(): continue
    ov = int((m & ms).sum())
    g = max(0.0, (float(edt[m].min()) - 1) / S)
    kind = 'colosseum' if n in COLG else ('road' if n.startswith(ROADS) and n not in COLG else chk['kinds'].get(n, 'map'))
    res['objects'][n] = {'kind': kind, 'gap_pt': round(0.0 if ov else g, 2), 'overlap_pt2': round(ov / S / S, 2)}
txt = json.load(open(SPEC))['texts']; tr = {}
for tid, (x, y, w, h), *_ in txt:
    if x + w < X0 or x > X1 or y + h < Y0 or y > Y1: continue
    m = np.zeros((Hd, Wd), bool)
    m[max(int((y - Y0) * S), 0):max(int(np.ceil((y + h - Y0) * S)), 0), max(int((x - X0) * S), 0):max(int(np.ceil((x + w - X0) * S)), 0)] = True
    if not m.any(): continue
    ov = int((m & ms).sum()); tr[tid] = {'gap_pt': round(0.0 if ov else max(0.0, (float(edt[m].min()) - 1) / S), 2), 'overlap_pt2': round(ov / S / S, 2)}
res['texts'] = tr
by = {}
for n, r in res['objects'].items():
    k = r['kind']
    if k not in by or r['gap_pt'] < by[k]['gap_pt']: by[k] = {'gap_pt': r['gap_pt'], 'object': n, 'overlap_pt2': r['overlap_pt2']}
if tr:
    k = min(tr, key=lambda t: tr[t]['gap_pt']); by['text'] = {'gap_pt': tr[k]['gap_pt'], 'object': k}
res['min_by_kind'] = by
open(outp, 'w').write(json.dumps(res, ensure_ascii=False, indent=1))
print(json.dumps(by, ensure_ascii=False))
