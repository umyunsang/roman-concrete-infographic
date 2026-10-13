import bpy, sys, json, numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/WD2')
from common import Screen, world_verts, need
from wd2_lib import islands, bvh_world, ray_down_z
S = Screen()
o = need('R_via_ostiensis'); me = o.data; Wv = world_verts(o)
land = bvh_world([need('T_land')])
P0 = np.array([28.17, -83.36]); d = np.array([0.3905, -0.9206]); n = np.array([0.9206, 0.3905])
isl = islands(me)
kind = np.zeros(len(Wv), np.int32)  # 0 paver, 1 kerb
for fs in isl:
    vs = {v for f in fs for v in me.polygons[f].vertices}
    if len(fs) >= 40:
        kind[list(vs)] = 1
rel = Wv[:, :2] - P0; s = rel @ d; t = rel @ n
rows = []
for s0 in np.arange(-9, 9.01, 0.5):
    m = np.abs(s - s0) < 0.25
    if not m.any(): continue
    k = m & (kind == 1); p = m & (kind == 0)
    row = {'s': float(s0)}
    for side, sel in (('W', k & (t < np.median(t[m]))), ('E', k & (t >= np.median(t[m])))):
        if sel.any():
            row[side] = [round(float(t[sel].min() if side=='W' else t[sel].max()), 3), round(float(Wv[sel, 2].min()), 3), round(float(Wv[sel, 2].max()), 3)]
    if p.any():
        row['pav'] = [round(float(t[p].min()),3), round(float(t[p].max()),3), round(float(Wv[p,2].min()),3), round(float(Wv[p,2].max()),3)]
    c = P0 + s0 * d
    row['landW'] = ray_down_z(land, *(c - 1.3 * n)); row['landC'] = ray_down_z(land, *c); row['landE'] = ray_down_z(land, *(c + 1.3 * n))
    row['pt'] = [round(float(v), 1) for v in S.project([[c[0], c[1], 0]])[0]]
    rows.append(row)
for r in rows: print(r)
