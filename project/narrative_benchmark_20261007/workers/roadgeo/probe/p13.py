import bpy, sys, collections
import numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts, Terrain
S = Screen(); O = bpy.data.objects
T = Terrain(O['T_land'])
def isl(o):
    me = o.data; W = world_verts(o)
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
    g = collections.defaultdict(list)
    for i, r in enumerate(roots): g[r].append(i)
    return W, [(sorted(vs), fc[r]) for r, vs in g.items()]
for name in ['R_core_road', 'R_via_ostiensis']:
    W, I = isl(O[name]); P = S.project(W)
    for vs, f in I:
        p = P[vs]; c = p.mean(0)
        if f < 40 and 360 <= c[0] <= 410 and 995 <= c[1] <= 1022:
            w = W[vs]
            print(name, f, 'scr', c.round(1), 'xy', w[:, :2].mean(0).round(2), 'ext', (w[:, :2].max(0) - w[:, :2].min(0)).round(2), 'z', w[:, 2].min().round(3), w[:, 2].max().round(3), 'first', vs[0])
        elif f >= 40:
            m = (p[:, 0] > 360) & (p[:, 0] < 410) & (p[:, 1] > 995) & (p[:, 1] < 1022)
            if m.any():
                print(name, 'KERB', f, 'n', int(m.sum()), 'xy range', W[vs][m][:, :2].min(0).round(2), W[vs][m][:, :2].max(0).round(2), 'z', W[vs][m][:, 2].min().round(3), W[vs][m][:, 2].max().round(3))
