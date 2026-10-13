import bpy, json, sys, collections
import numpy as np
from mathutils import Vector
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts, Terrain
S = Screen(); O = bpy.data.objects
cam = bpy.context.scene.camera
print('cam loc', tuple(round(v,2) for v in cam.matrix_world.translation), 'fwd', tuple(round(v,3) for v in (-cam.matrix_world.col[2].xyz)), 'lens', cam.data.lens, cam.data.sensor_width, cam.data.sensor_fit)
T = Terrain(O['T_land'])
road = O['R_core_road']; me = road.data; W = world_verts(road); P = S.project(W)
parent = list(range(len(me.vertices)))
def find(a):
    while parent[a] != a:
        parent[a] = parent[parent[a]]; a = parent[a]
    return a
for e in me.edges:
    a, b = find(e.vertices[0]), find(e.vertices[1])
    if a != b: parent[a] = b
roots = np.array([find(i) for i in range(len(me.vertices))])
fc = collections.Counter(roots[p.vertices[0]] for p in me.polygons)
groups = collections.defaultdict(list)
for i, r in enumerate(roots): groups[r].append(i)
# kerbs near region
for r, vs in groups.items():
    if fc[r] >= 40:
        pv = P[vs]; m = (pv[:,0] > 540) & (pv[:,0] < 700) & (pv[:,1] > 990) & (pv[:,1] < 1035)
        if m.any():
            w = W[vs][m]
            tz = np.array([T.z(x, y) for x, y, z in w])
            print('KERB', fc[r], 'n', int(m.sum()), 'zmin', round(float(w[:,2].min()),3), 'zmax', round(float(w[:,2].max()),3), 'scr y', round(float(pv[m][:,1].min()),1), round(float(pv[m][:,1].max()),1), 'terrain under (min/max)', round(float(tz.min()),3), round(float(tz.max()),3))
            # per x bins: top z of kerb vs terrain
            xs = pv[m][:,0]
            for x0 in range(540, 700, 10):
                k = (xs >= x0) & (xs < x0+10)
                if k.any():
                    print('   x', x0, 'kerb z max', round(float(w[k][:,2].max()),3), 'min', round(float(w[k][:,2].min()),3), 'terrain', round(float(tz[k].min()),3), round(float(tz[k].max()),3), 'y', round(float(pv[m][k][:,1].min()),1), round(float(pv[m][k][:,1].max()),1))
# cross-section near screen x=600: pavers whose centroid within 6 pt of x 600, sorted by y
for X in (575, 600, 625, 650):
    print('--- X', X)
    rows = []
    for r, vs in groups.items():
        if fc[r] >= 40: continue
        c = P[vs].mean(0)
        if abs(c[0] - X) < 3 and 985 < c[1] < 1030:
            w = W[vs]; cxy = w[:, :2].mean(0)
            rows.append((round(float(c[1]),1), round(float(c[0]),1), fc[r], round(float(w[:,2].max()),3), round(float(w[:,2].min()),3), round(T.z(*cxy),3), [round(float(v),2) for v in cxy]))
    for t in sorted(rows): print(t)
