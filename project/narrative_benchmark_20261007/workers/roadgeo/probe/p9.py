import bpy, json, sys, collections
import numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts, Terrain
S = Screen(); O = bpy.data.objects
T = Terrain(O['T_land'])
o = O['R_via_ostiensis']; me = o.data; W = world_verts(o); P = S.project(W)
def polyline(k0, n):
    return W[k0:k0 + n].reshape(-1, 4, 3).mean(1)
CW = polyline(3960, 428); CE = polyline(4388, 428)
print('kerb sep', np.linalg.norm(CW[:, :2] - CE[:, :2], axis=1).round(3)[::10])
def proj(C, q):
    # nearest point on polyline: returns (s_index_float, signed dist, tangent)
    A = C[:-1, :2]; B = C[1:, :2]; AB = B - A; L2 = (AB ** 2).sum(1)
    t = np.clip(((q[None] - A) * AB).sum(1) / L2, 0, 1); X = A + AB * t[:, None]
    d = np.linalg.norm(q[None] - X, axis=1); i = int(d.argmin())
    tang = AB[i] / np.sqrt(L2[i]); nrm = np.array([-tang[1], tang[0]])
    return i + t[i], float(((q - X[i]) * nrm).sum()), d[i]
# islands
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
pav = [vs for r, vs in g.items() if fc[r] < 40]
rows = []
for vs in pav:
    w = W[vs]; top = w[w[:, 2] >= w[:, 2].max() - 0.03]
    dE = [proj(CE, q[:2]) for q in top]; dW = [proj(CW, q[:2]) for q in top]
    mE = min(d[2] for d in dE); mW = min(d[2] for d in dW)
    sE = np.mean([d[0] for d in dE])
    tz = max(T.z(x, y) for x, y, z in w)
    rows.append((sE, mE, mW, len(vs), w[:, 2].max() - tz, P[vs].mean(0)))
rows.sort(key=lambda r: r[0])
# east edge pavers: mE < 0.6
east = [r for r in rows if r[1] < 0.6]
print('east-edge pavers', len(east))
for r in east[:400:3]:
    print('s %.2f gapE %.3f gapW %.3f nv %d top-ter %.3f scr %s' % (r[0], r[1] - 0.1, r[2] - 0.1, r[3], r[4], r[5].round(1)))
west = [r for r in rows if r[2] < 0.6]
print('west-edge pavers', len(west), 'gap hist', np.histogram([r[2] - 0.1 for r in west], bins=[-1, 0, 0.03, 0.06, 0.1, 0.2, 0.3, 0.5])[0])
print('east gap hist', np.histogram([r[1] - 0.1 for r in east], bins=[-1, 0, 0.03, 0.06, 0.1, 0.2, 0.3, 0.5])[0])
