import bpy, bmesh, sys, json, numpy as np, math
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, bvh_of, map_visible_objects
from mathutils import Vector
S = Screen()
o = bpy.data.objects['COL_ruined']
me = o.data
objs = map_visible_objects()
bvh, owner = bvh_of(objs)
# polygon offsets per object in the combined bvh
offs = {}; k = 0
for ob in objs:
    offs[ob.name] = k
    k += sum(1 for _ in ob.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.polygons)
co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
cen = np.empty(len(me.polygons) * 3); me.polygons.foreach_get('center', cen); cen = cen.reshape(-1, 3)
area = np.empty(len(me.polygons)); me.polygons.foreach_get('area', area)
nrm = np.empty(len(me.polygons) * 3); me.polygons.foreach_get('normal', nrm); nrm = nrm.reshape(-1, 3)
mi = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', mi)
rho = np.sqrt(((cen[:, 0] + 0.004) / 31.98) ** 2 + ((cen[:, 1] - 0.349) / 24.53) ** 2)
print('wall faces', (mi == 0).sum(), 'wall rho<0.88', ((mi == 0) & (rho < 0.88)).sum(), 'interior', (mi == 1).sum(), 'arena', (mi == 2).sum())
print('interior rho max', rho[mi == 1].max(), 'pct', np.percentile(rho[mi == 1], [50, 90, 99]))
print('wall rho pct', np.percentile(rho[mi == 0], [1, 5, 25, 50, 75]))
mw = o.matrix_world
ang = np.degrees(np.arctan2(cen[:, 1] - 0.349, cen[:, 0] + 0.004)) % 360
sc = (np.array(mw.to_3x3().to_scale()))
area_w = area * sc[0] * sc[1]


def hits(box, step=0.25):
    x0, x1, y0, y1 = box
    res = {}
    for x in np.arange(x0, x1, step):
        for y in np.arange(y0, y1, step):
            org, d = S.ray((x, y))
            loc, n, idx, dist = bvh.ray_cast(org, d)
            if idx is None:
                continue
            ob = owner[idx]
            res.setdefault(ob, []).append(idx - offs[ob])
    return res


for nm, box in [('wfin', (384, 396, 849, 860)), ('efin', (748, 764, 898, 928)), ('hole', (700, 717, 931, 940))]:
    h = hits(box)
    print('==', nm, {k: len(v) for k, v in h.items()})
    f = np.unique(h.get('COL_ruined', []))
    if len(f):
        print(' faces', len(f), 'area<0.002', (area[f] < 0.002).sum())
        for fi in f[np.argsort(area[f])][:40]:
            print('  f', fi, 'a %.5f' % area[fi], 'rho %.3f' % rho[fi], 'ang %.1f' % ang[fi], 'z %.2f' % cen[fi, 2], 'n', nrm[fi].round(2), 'm', mi[fi])
    if 'T_land' in h:
        # where terrain seen
        pass
for fi in (137919, 186006):
    print('named', fi, area[fi], rho[fi], ang[fi], cen[fi])
