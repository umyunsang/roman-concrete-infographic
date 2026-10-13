import bpy, json, sys, collections
import numpy as np
from mathutils.kdtree import KDTree
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
    return W, g, fc
for name in ['R_core_road', 'R_via_ostiensis', 'R_via_appia']:
    W, g, fc = isl(O[name]); P = S.project(W)
    pav = [(r, vs) for r, vs in g.items() if fc[r] < 40]
    C = np.array([W[vs].mean(0) for r, vs in pav]); top = np.array([W[vs][:, 2].max() for r, vs in pav])
    kd = KDTree(len(C))
    for i, c in enumerate(C): kd.insert((c[0], c[1], 0), i)
    kd.balance()
    pairs = []
    for i, c in enumerate(C):
        for (co, j, d) in kd.find_range((c[0], c[1], 0), 0.3):
            if j > i: pairs.append((i, j, d))
    fcs = collections.Counter(fc[r] for r, vs in pav)
    print(name, 'paver islands', len(pav), 'face-count hist', dict(fcs), 'close pairs (<0.3)', len(pairs))
    if pairs:
        sp = np.array([P[pav[i][1]].mean(0) for i, j, d in pairs])
        print('  pair screen x range', sp[:, 0].min().round(1), sp[:, 0].max().round(1), 'y', sp[:, 1].min().round(1), sp[:, 1].max().round(1))
        # histogram by screen x 50pt bins
        h = collections.Counter((int(x // 50) * 50, int(y // 50) * 50) for x, y in sp)
        print('  bins', sorted(h.items()))
        lowtop = [min(top[i], top[j]) for i, j, d in pairs]
        ter = [T.z(*C[i][:2]) for i, j, d in pairs]
        print('  lower-of-pair top minus terrain: min', round(float(np.min(np.array(lowtop) - ter)), 3), 'max', round(float(np.max(np.array(lowtop) - ter)), 3))
