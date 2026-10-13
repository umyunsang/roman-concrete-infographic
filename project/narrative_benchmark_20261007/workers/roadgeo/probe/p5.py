import bpy, json, sys, collections
import numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts, Terrain
S = Screen(); O = bpy.data.objects
T = Terrain(O['T_land'])
o = O['R_via_ostiensis']; me = o.data; W = world_verts(o); P = S.project(W)
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
for r, vs in g.items():
    if fc[r] >= 40:
        w = W[vs]; p = P[vs]
        tz = np.array([T.z(x, y) for x, y, z in w])
        print('KERB faces', fc[r], 'verts', len(vs), 'scr x', p[:,0].min().round(1), p[:,0].max().round(1), 'y', p[:,1].min().round(1), p[:,1].max().round(1), 'z', w[:,2].min().round(3), w[:,2].max().round(3))
        # along screen y bins: kerb top z vs terrain
        for y0 in range(1000, 1470, 20):
            k = (p[:,1] >= y0) & (p[:,1] < y0 + 20)
            if k.any():
                print('   y', y0, 'x', p[k][:,0].mean().round(1), 'kerb zmax', w[k][:,2].max().round(3), 'terrain max', tz[k].max().round(3), 'diff', (w[k][:,2].max() - tz[k].max()).round(3))
# pavers: per y bin, the east-most paver: top z vs terrain at its footprint
pav = [(r, vs) for r, vs in g.items() if fc[r] < 40]
C = np.array([P[vs].mean(0) for r, vs in pav])
for y0 in range(1000, 1470, 20):
    k = np.nonzero((C[:,1] >= y0) & (C[:,1] < y0 + 20))[0]
    if not len(k): continue
    diffs = []
    for i in k:
        w = W[pav[i][1]]; tz = max(T.z(x, y) for x, y, z in w); diffs.append(w[:,2].max() - tz)
    diffs = np.array(diffs)
    print('PAV y', y0, 'n', len(k), 'top-terrain min', diffs.min().round(3), 'n<0.03', int((diffs < 0.03).sum()), 'n<0', int((diffs < 0).sum()))
print('mats', [m.name for m in me.materials])
