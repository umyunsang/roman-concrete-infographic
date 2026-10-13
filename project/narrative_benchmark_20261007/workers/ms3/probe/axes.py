import bpy, sys
import numpy as np
from mathutils import Vector
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts, Terrain, need
S = Screen()
p = Vector((31.86, -4.99, 0.5))
for d in ((1,0,0),(0,1,0),(0,0,1)):
    print(d, (S.to_pt(p + Vector(d)) - S.to_pt(p)).round(2))
print('world per pt', S.world_per_pt(p))
print('cam loc', S.origin[:], 'cam rot', S.cam.rotation_euler[:], S.cam.data.type, S.cam.data.ortho_scale if S.cam.data.type=='ORTHO' else S.cam.data.lens)
# MS1/MS2 plinth vs terrain
land = need('T_land'); T = Terrain(land)
for n in ('MS1_core1_to_2', 'MS2_core2_to_34', 'MS3_core34_to_5'):
    o = need(n); W = world_verts(o); zmin = W[:,2].min(); bot = W[W[:,2] < zmin + 0.02]
    r = np.array([q[2]-T.z(q[0], q[1]) for q in bot[::3]])
    print(n, 'bottom z', round(zmin,3), 'bottom-terrain min/med/max', r.min().round(3), np.median(r).round(3), r.max().round(3), 'rotz deg', round(np.degrees(o.rotation_euler.z),2))
