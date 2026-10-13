"""Screen-silhouette gaps from <prefix>_tris.npz (written by measure_export.py).
Run: uv run -q --no-project --with pillow --with numpy --with scipy python -I measure.py <prefix> <out.json>
Each object's projected triangles are filled at S px/pt; gap(A,B) = (min EDT from A over B pixels - 1px)/S, i.e. a
conservative edge-to-edge gap in pt at 0.25pt resolution; 0 with 'overlap_px' > 0 when the silhouettes share pixels."""
import sys, json
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt

pre, outp = sys.argv[1], sys.argv[2]
S = 4.0
X0, X1, Y0, Y1 = 100, 1100, 300, 1150
Wd, Hd = int((X1 - X0) * S), int((Y1 - Y0) * S)
Z = np.load(pre + '_tris.npz')
names = list(Z.keys())


def raster(tri, clip=None):
    im = Image.new('1', (Wd, Hd), 0); dr = ImageDraw.Draw(im)
    T = (tri - np.array((X0, Y0))) * S
    for t in T:
        dr.polygon([tuple(p) for p in t], fill=1, outline=1)
    m = np.array(im, bool)
    if clip is not None:
        x0, x1, y0, y1 = clip
        yy, xx = np.mgrid[0:Hd, 0:Wd]; px = X0 + (xx + 0.5) / S; py = Y0 + (yy + 0.5) / S
        m &= (px >= x0) & (px <= x1) & (py >= y0) & (py <= y1)
    return m


masks = {n: raster(Z[n]) for n in names}
def union(*ns):
    m = np.zeros((Hd, Wd), bool)
    for n in ns:
        if n in masks: m |= masks[n]
    return m
road = masks['R_core_road']
yy, xx = np.mgrid[0:Hd, 0:Wd]; PX = X0 + (xx + 0.5) / S; PY = Y0 + (yy + 0.5) / S
south = road & (PX >= 330) & (PX <= 800) & (PY >= 880)
groups = {'COL': masks['COL_ruined'], 'POD': masks['R3_colosseum_podium'], 'ARENA': masks['R4_arena_skin'],
          'COLG': union('COL_ruined', 'R3_colosseum_podium', 'R4_arena_skin'), 'PAN': masks['R8_pantheon']}
edt = {g: distance_transform_edt(~m) for g, m in groups.items()}


def gap(g, m):
    if not m.any(): return None
    ov = int((groups[g] & m).sum())
    d = float(edt[g][m].min())
    return {'gap_pt': round(max(0.0, (d - 1) / S), 2), 'overlap_px': ov}


def where(g, m):
    """screen point of B closest to group g."""
    e = np.where(m, edt[g], np.inf); i = np.unravel_index(np.argmin(e), e.shape)
    return [round(float(PX[i]), 1), round(float(PY[i]), 1)]


res = {'resolution_pt': 1 / S}
res['south_road'] = {g: dict(gap(g, south), at=where(g, south)) for g in ('COL', 'POD', 'COLG')}
near = {}
for n in names:
    if n in ('COL_ruined', 'R3_colosseum_podium', 'R4_arena_skin'): continue
    r = gap('COLG', masks[n])
    if r and r['gap_pt'] < 25:
        r['at'] = where('COLG', masks[n]); r['col_only'] = gap('COL', masks[n])['gap_pt']; r['podium_only'] = gap('POD', masks[n])['gap_pt']
        near[n] = r
res['colosseum_group_neighbours'] = dict(sorted(near.items(), key=lambda kv: kv[1]['gap_pt']))
named = {}
for n in ['F_centuriatio', 'L05_aqua_claudia', 'T_cypress', 'MS1_core1_to_2', 'MS2_core2_to_34', 'MS3_core34_to_5',
          'NB_modern_building', 'R8_pantheon', 'R_via_appia', 'R_via_ostiensis', 'L02_tiber', 'B_pons1', 'B_pons2']:
    if n in masks:
        r = gap('COLG', masks[n]); r['col_only'] = gap('COL', masks[n]); r['podium_only'] = gap('POD', masks[n]); named[n] = r
trees = [n for n in names if n.startswith('T_')]
if trees:
    m_ = union(*trees); named['trees_all(' + ','.join(trees) + ')'] = gap('COLG', m_)
res['colosseum_group_named'] = named
pn = {}
for n in names:
    if n == 'R8_pantheon': continue
    r = gap('PAN', masks[n])
    if r and r['gap_pt'] < 25:
        r['at'] = where('PAN', masks[n]); pn[n] = r
res['pantheon_neighbours'] = dict(sorted(pn.items(), key=lambda kv: kv[1]['gap_pt']))
res['pantheon_named'] = {n: gap('PAN', masks[n]) for n in ('MS1_core1_to_2', 'R_core_road', 'F_centuriatio', 'COL_ruined', 'NB_modern_building') if n in masks}
roadm = masks['R_core_road']; nwm = roadm & (PY < 700) & (PX < 560)
eroad = distance_transform_edt(~nwm)
res['nw_road_named'] = {n: round(max(0.0, (float(eroad[masks[n]].min()) - 1) / S), 2) for n in ('F_centuriatio', 'COL_ruined', 'R8_pantheon', 'MS1_core1_to_2', 'L02_tiber', 'R3_colosseum_podium') if n in masks and masks[n].any()}
ys, xs = np.nonzero(groups['PAN'])
res['pantheon_box_pt'] = [round(float(X0 + xs.min() / S), 2), round(float(X0 + (xs.max() + 1) / S), 2),
                          round(float(Y0 + ys.min() / S), 2), round(float(Y0 + (ys.max() + 1) / S), 2)]
ys, xs = np.nonzero(groups['COL'])
res['colosseum_box_pt'] = [round(float(X0 + xs.min() / S), 2), round(float(X0 + (xs.max() + 1) / S), 2),
                           round(float(Y0 + ys.min() / S), 2), round(float(Y0 + (ys.max() + 1) / S), 2)]
# per 10pt column: south road top vs building bottom / podium bottom (screen)
cols = []
for x0 in range(330, 800, 10):
    c = (PX[0] >= x0) & (PX[0] < x0 + 10)
    def ext(m, f):
        r = np.nonzero(m[:, c].any(1))[0]; return None if len(r) == 0 else round(float(Y0 + f(r) / S), 1)
    cols.append([x0, ext(south, np.min), ext(groups['COL'], np.max), ext(groups['POD'], np.max)])
res['south_columns_x_roadtop_colbottom_podbottom'] = cols
Path = __import__('pathlib').Path
Path(outp).write_text(json.dumps(res, ensure_ascii=False, indent=1))
np.savez_compressed(outp.replace('.json', '_masks.npz'), COL=groups['COL'], POD=groups['POD'], PAN=groups['PAN'],
                    ROAD=road, origin=np.array((X0, Y0, S)))
print(json.dumps({k: res[k] for k in ('south_road', 'pantheon_box_pt', 'colosseum_box_pt')}, ensure_ascii=False))
