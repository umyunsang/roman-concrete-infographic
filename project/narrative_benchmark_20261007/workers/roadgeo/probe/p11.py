import bpy, json, sys, collections
import numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts, Terrain
S = Screen(); O = bpy.data.objects
T = Terrain(O['T_land'])
o = O['R_via_ostiensis']; me = o.data; W = world_verts(o)
for p in me.polygons:
    if p.index in (430, 450, 475):
        vs = list(p.vertices)
        # island verts: find verts within the island by bmesh-free approach: neighbors indices close
        print(p.index, vs, W[vs].round(3).tolist())
# assume island verts contiguous block of 8 around
for base in (430,):
    pass
# list verts 0..20 (first islands)
for i in range(0, 24): print(i, W[i].round(3))
for n in ['R1_road_landing1', 'R1_road_landing5', 'R1_road5_bed', 'R4_bridge_west_bed']:
    ob = O[n]; Wv = world_verts(ob); P = S.project(Wv)
    print(n, 'nv', len(Wv), 'nf', len(ob.data.polygons), 'z', Wv[:, 2].min().round(3), Wv[:, 2].max().round(3), 'terrain under max', max(T.z(x, y) for x, y, z in Wv).__round__(3), 'scr', P.min(0).round(1), P.max(0).round(1))
    for p in ob.data.polygons[:3]:
        print('   face', len(p.vertices), 'area', round(p.area, 3), 'n', [round(v, 2) for v in p.normal])
