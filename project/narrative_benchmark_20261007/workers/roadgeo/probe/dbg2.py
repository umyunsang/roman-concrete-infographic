import bpy, runpy, numpy as np, math
G = runpy.run_path('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/roadgeo/step.py', run_name='lib')
S = G['Screen'](); land = G['need']('T_land'); me = land.data
rep = {}; G['clip_bed_to_kerb'](rep); G['junction_fill'](rep)
LW = G['world_verts'](land); P = S.project(LW)
name, objs, box = G['REGIONS'][1]
tris = np.concatenate([G['up_faces'](G['need'](o), S, box)[0] for o in objs])
CELL = G['CELL']; R = G['SHOULDER'] + G['MAX_DROP'] / G['SLOPE']
xa, xb = tris[:, :, 0].min() - R - CELL, tris[:, :, 0].max() + R + CELL
ya, yb = tris[:, :, 1].min() - R - CELL, tris[:, :, 1].max() + R + CELL
nx = int(math.ceil((xb - xa) / CELL)) + 1; ny = int(math.ceil((yb - ya) / CELL)) + 1
top = G['rasterize_max'](tris, xa, ya, nx, ny)
target = np.where(np.isfinite(top), top - G['D_BELOW'], np.inf)
cap = G['cone_cap'](target)
sel = np.nonzero((P[:, 0] > 115) & (P[:, 0] < 160) & (P[:, 1] > 1380) & (P[:, 1] < 1410))[0]
c = G['bilinear'](cap, xa, ya, LW[sel, :2])
fn = np.empty(len(me.polygons) * 3); me.polygons.foreach_get('normal', fn); fn = fn.reshape(-1, 3)
steep = np.zeros(len(LW), bool)
for p in me.polygons:
    if abs(fn[p.index, 2]) < 0.7:
        for v in p.vertices: steep[v] = True
for i, ci in zip(sel, c):
    if LW[i, 2] - ci > 0.0 or steep[i]:
        print(i, 'scr', P[i].round(1), 'z %.3f cap %.3f need %.3f steep %d' % (LW[i, 2], ci, max(0, LW[i, 2] - ci), steep[i]))
