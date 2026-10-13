import bpy, runpy, numpy as np, math
from mathutils import Vector
G = runpy.run_path('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/roadgeo/step.py', run_name='lib')
S = G['Screen'](); land = G['need']('T_land'); me = land.data
LW = G['world_verts'](land); P = S.project(LW)
# boundary vertices of T_land
ec = {}
for p in me.polygons:
    for k in p.edge_keys: ec[k] = ec.get(k, 0) + 1
bnd = set()
for k, c in ec.items():
    if c == 1: bnd.update(k)
sel = np.nonzero((P[:, 0] > 115) & (P[:, 0] < 170) & (P[:, 1] > 1375) & (P[:, 1] < 1415))[0]
print('boundary verts in box', sum(1 for i in sel if i in bnd), 'of', len(sel))
for i in sel:
    if i in bnd: print('  bnd', i, P[i].round(1), LW[i].round(3))
# which objects lie under/near
dg = bpy.context.evaluated_depsgraph_get()
x0, x1 = LW[sel, 0].min() - 1, LW[sel, 0].max() + 1; y0, y1 = LW[sel, 1].min() - 1, LW[sel, 1].max() + 1
for o in G['map_visible_objects']():
    if o.name == 'T_land': continue
    W = G['world_verts'](o) if o.type == 'MESH' else None
    if W is None or not len(W): continue
    m = (W[:, 0] > x0) & (W[:, 0] < x1) & (W[:, 1] > y0) & (W[:, 1] < y1)
    if m.any(): print('obj near', o.name, int(m.sum()), 'z', W[m, 2].min().round(3), W[m, 2].max().round(3))
