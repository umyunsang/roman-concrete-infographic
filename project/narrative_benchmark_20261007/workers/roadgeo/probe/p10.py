import bpy, json, sys, collections
import numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts, Terrain
S = Screen(); O = bpy.data.objects
o = O['R_via_ostiensis']; me = o.data; W = world_verts(o); P = S.project(W)
CW = W[3960:3960+428].reshape(-1, 4, 3).mean(1); CE = W[4388:4388+428].reshape(-1, 4, 3).mean(1)
print('CW0', CW[0].round(3), 'CE0', CE[0].round(3), 'CW1', CW[1].round(3), 'tangent', (CW[1]-CW[0]).round(3))
mw = o.matrix_world
n = 0
for p in me.polygons:
    if p.vertices[0] >= 3960: continue
    nz = (mw.to_3x3() @ p.normal).normalized().z
    if abs(nz) < 0.8: continue
    V = W[list(p.vertices)]
    e = [np.linalg.norm(V[(i+1)%len(V), :2] - V[i, :2]) for i in range(len(V))]
    c = V.mean(0)
    if np.linalg.norm(c[:2] - (CW[20,:2]+CE[20,:2])/2) < 2.0:
        t = (CW[21,:2]-CW[19,:2]); t /= np.linalg.norm(t); nrm = np.array([-t[1], t[0]])
        rel = c[:2] - (CW[20,:2]+CE[20,:2])/2
        print(p.index, len(p.vertices), 'edges', np.round(e, 3), 'c along %.3f across %.3f z %.3f' % (rel @ t, rel @ nrm, c[2]), 'nz %.2f' % nz)
        n += 1
print('CE-CW across', ((CE[20,:2]-CW[20,:2]) @ np.array([-(CW[21,1]-CW[19,1]), CW[21,0]-CW[19,0]]) / np.linalg.norm(CW[21,:2]-CW[19,:2])))
