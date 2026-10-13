import bpy, json, sys, collections
import numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts, Terrain
S = Screen(); O = bpy.data.objects
T = Terrain(O['T_land'])
o = O['R_via_ostiensis']; me = o.data; W = world_verts(o); P = S.project(W)
# print first 3 sections of first kerb
k0 = 3960
for i in range(k0, k0 + 12): print(i, W[i].round(3))
print('faces of kerb (first 6):')
cnt = 0
for p in me.polygons:
    if p.vertices[0] >= k0 and p.vertices[0] < k0 + 428:
        print(list(p.vertices), (o.matrix_world.to_3x3() @ p.normal).normalized()[:]); cnt += 1
        if cnt > 5: break
