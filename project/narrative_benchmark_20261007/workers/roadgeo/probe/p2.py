import bpy, bmesh, json, sys
import numpy as np
from mathutils import Vector
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts, Terrain, bvh_of
S = Screen(); O = bpy.data.objects
land = O['T_land']; T = Terrain(land)
road = O['R_core_road']; me = road.data
W = world_verts(road)
bm = bmesh.new(); bm.from_mesh(me)
bm.verts.ensure_lookup_table()
# islands by vertex connectivity
import collections
parent = list(range(len(me.vertices)))
def find(a):
    while parent[a] != a:
        parent[a] = parent[parent[a]]; a = parent[a]
    return a
for e in me.edges:
    a, b = find(e.vertices[0]), find(e.vertices[1])
    if a != b: parent[a] = b
roots = np.array([find(i) for i in range(len(me.vertices))])
fcount = collections.Counter()
for p in me.polygons: fcount[roots[p.vertices[0]]] += 1
P = S.project(W)
groups = collections.defaultdict(list)
for i, r in enumerate(roots): groups[r].append(i)
rows = []
for r, vs in groups.items():
    c = P[vs].mean(0)
    if 540 <= c[0] <= 700 and 995 <= c[1] <= 1035:
        w = W[vs]; top = w[:, 2].max(); bot = w[:, 2].min()
        xy = w[:, :2]
        tz = [T.z(x, y) for x, y in xy]
        rows.append((round(float(c[0]),1), round(float(c[1]),1), fcount[r], len(vs), round(float(top),3), round(float(bot),3), round(float(max(tz)),3), round(float(top - max(tz)),3), [round(float(v),2) for v in w.mean(0)]))
rows.sort(key=lambda t: (t[1], t[0]))
for t in rows: print(t)
print(len(rows))
