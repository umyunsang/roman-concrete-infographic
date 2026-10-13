import bpy, sys, json, numpy as np, math
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts, Terrain
S = Screen()
T = Terrain(bpy.data.objects['T_land'])
p = bpy.data.objects['R3_colosseum_podium']
W = world_verts(p)
print('podium z hist', np.histogram(W[:, 2], bins=12))
me = p.data
nrm = np.empty(len(me.polygons) * 3); me.polygons.foreach_get('normal', nrm); nrm = nrm.reshape(-1, 3)
cen = np.empty(len(me.polygons) * 3); me.polygons.foreach_get('center', cen); cen = cen.reshape(-1, 3)
print('podium face normal z classes', np.histogram(nrm[:, 2], bins=[-1.01, -0.5, 0.2, 0.9, 1.01]))
print('podium top faces z', np.percentile(cen[np.abs(nrm[:, 2]) > 0.9, 2], [0, 50, 100]), 'side faces', (np.abs(nrm[:, 2]) < 0.5).sum())
# radial structure: verts per ring?
print('n verts', len(W), 'unique z', np.unique(W[:, 2].round(3))[:20])
# terrain heights around podium outer edge
xy = W[W[:, 2] < 0.1][:, :2]
tz = np.array([T.z(x, y) for x, y in xy[::5]])
print('terrain at podium outer verts: pct', np.percentile(tz, [0, 10, 50, 90, 100]).round(3))
# kiln terrain
k = bpy.data.objects['D2_lime_kiln']
c = k.location
zs = [[round(T.z(c.x + dx, c.y + dy), 3) for dx in np.arange(-5, 5.1, 1.25)] for dy in np.arange(-5, 5.1, 1.25)]
print('kiln terrain grid', json.dumps(zs))
print('kiln base center screen', S.to_pt(c), 'world per pt', S.world_per_pt(c.copy()))
Wk = world_verts(k)
print('kiln lowest verts z', np.sort(Wk[:, 2])[:5], 'bbox', Wk.min(0), Wk.max(0))
# objects near kiln (screen)
for o in bpy.data.objects:
    if o.type != 'MESH' or o.hide_render: continue
    try:
        Wo = world_verts(o)
    except Exception:
        continue
    if len(Wo) == 0: continue
    P = S.project(Wo[:: max(1, len(Wo) // 2000)])
    if P[:, 0].min() < 230 and P[:, 0].max() > 20 and P[:, 1].min() < 760 and P[:, 1].max() > 600:
        print('near kiln', o.name, [o.users_collection[0].name], P[:, 0].min().round(1), P[:, 0].max().round(1), P[:, 1].min().round(1), P[:, 1].max().round(1))
for n in ['L03_forum_temple', 'L03_forum_vesta']:
    o = bpy.data.objects.get(n)
    if o: print(n, 'hide_render', o.hide_render, [c.name for c in o.users_collection], [c.hide_render for c in o.users_collection])
