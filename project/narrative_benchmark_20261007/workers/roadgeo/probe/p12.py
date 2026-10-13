import bpy, sys, collections
import numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts, Terrain
S = Screen(); O = bpy.data.objects
b = O['R1_road5_bed']; Wb = world_verts(b)
print('bed verts'); 
for i, (w, p) in enumerate(zip(Wb, S.project(Wb))): print(i, w.round(3), p.round(1))
print('bed faces', [list(p.vertices) for p in b.data.polygons])
r = O['R_core_road']; W = world_verts(r); P = S.project(W)
for k0, n in ((19723, 578), (20313, 602)):
    seg = W[k0:k0+n]; ps = P[k0:k0+n]
    m = (ps[:,0] > 900) & (ps[:,1] > 860)
    print('kerb', k0, 'pts near land5', int(m.sum()), 'last verts:')
    for i in range(n-12, n): print('  ', k0+i, W[k0+i].round(3), P[k0+i].round(1))
d = O['R1_road_landing5']; Wd = world_verts(d); print('disc center', Wd.mean(0).round(3), 'r', np.linalg.norm(Wd[:,:2]-Wd[:,:2].mean(0),axis=1).max().round(3))
