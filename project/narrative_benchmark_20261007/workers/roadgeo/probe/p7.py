import bpy, json, sys, collections
import numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts, Terrain
S = Screen(); O = bpy.data.objects
def islands(o):
    me = o.data
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
    return [(sorted(vs), fc[r]) for r, vs in g.items()]
for name in ['R_via_ostiensis', 'R_core_road']:
    o = O[name]; W = world_verts(o); P = S.project(W)
    for vs, f in islands(o):
        if f < 40: continue
        vs = np.array(vs); w = W[vs]
        contiguous = vs[-1] - vs[0] + 1 == len(vs)
        d01 = np.linalg.norm(w[0::4, :2] - w[1::4, :2], axis=1) if len(vs) % 4 == 0 else None
        dz02 = (w[0::4, 2] - w[2::4, 2]) if len(vs) % 4 == 0 else None
        print(name, 'kerb faces', f, 'nv', len(vs), 'contig', contiguous, 'first', vs[0], 'scr0', P[vs[0]].round(1), 'scrN', P[vs[-1]].round(1),
              'd01', None if d01 is None else (d01.min().round(3), d01.max().round(3)), 'dz02', None if dz02 is None else (dz02.min().round(3), dz02.max().round(3)))
        # polygon pattern: first few polys
    pav = [(vs, f) for vs, f in islands(o) if f < 40]
    print(name, 'paver islands', len(pav), 'vert counts', collections.Counter(len(vs) for vs, f in pav).most_common(6))
