import bpy, json, sys, collections
import numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts
S = Screen(); O = bpy.data.objects
land = O['T_land']; me = land.data; W = world_verts(land); P = S.project(W)
E = np.empty(len(me.edges) * 2, np.int32); me.edges.foreach_get('vertices', E); E = E.reshape(-1, 2)
L = np.linalg.norm(W[E[:, 0], :2] - W[E[:, 1], :2], axis=1)
mid = (P[E[:, 0]] + P[E[:, 1]]) / 2
for name, box in [('A', (540, 700, 990, 1035)), ('ost_mid', (180, 320, 1100, 1300)), ('ost_low', (90, 200, 1300, 1460)), ('land1', (495, 580, 490, 545)), ('land5', (880, 970, 850, 945))]:
    x0, x1, y0, y1 = box
    k = (mid[:, 0] > x0) & (mid[:, 0] < x1) & (mid[:, 1] > y0) & (mid[:, 1] < y1)
    vk = (P[:, 0] > x0) & (P[:, 0] < x1) & (P[:, 1] > y0) & (P[:, 1] < y1)
    print(name, 'edges', int(k.sum()), 'len xy p10/50/90', np.percentile(L[k], [10, 50, 90]).round(3), 'verts', int(vk.sum()), 'z range', W[vk, 2].min().round(3), W[vk, 2].max().round(3))
print('land world bbox', W.min(0).round(2), W.max(0).round(2))
# vertex attributes / shape keys / uv
print('attrs', [(a.name, a.domain, a.data_type) for a in me.attributes], 'shape keys', me.shape_keys is not None, 'uv', [u.name for u in me.uv_layers])
print('smooth?', sum(p.use_smooth for p in me.polygons[:1000]))
