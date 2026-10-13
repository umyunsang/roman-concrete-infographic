import bpy, sys, numpy as np, math
from pathlib import Path
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, Terrain, world_verts, need
from mathutils import Vector
S = Screen(); TER = Terrain(need('T_land'))
def ground(pt):
    h = TER.bvh.ray_cast(*S.ray(pt))[0]; return np.array((h.x, h.y))
OLD = np.array([(300, 658), (320, 652), (340, 642.5), (360, 635), (380, 627), (400, 619), (420, 610), (440, 599.5),
                (460, 583), (480, 565), (500, 544), (520, 527.5), (540, 516.5)], float)
NEW = np.array([(300, 658), (320, 649), (340, 622), (360, 590), (380, 560), (390, 548), (400, 542), (410, 539),
                (420, 535), (430, 533), (440, 534), (460, 532), (480, 527), (500, 522), (520, 519), (540, 516.5)], float)
def densify(P, n=600):
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1); s = np.concatenate([[0], np.cumsum(seg)])
    u = np.linspace(0, s[-1], n); return np.stack([np.interp(u, s, P[:, 0]), np.interp(u, s, P[:, 1])], 1)
def smooth(P, it=3):
    for _ in range(it):
        Q = [P[0]]
        for a, b in zip(P[:-1], P[1:]): Q += [0.75 * a + 0.25 * b, 0.25 * a + 0.75 * b]
        Q.append(P[-1]); P = np.array(Q)
    return P
def curv(C):
    d1 = np.gradient(C, axis=0); d2 = np.gradient(d1, axis=0)
    k = (d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0]) / np.linalg.norm(d1, axis=1) ** 3
    return k
for name, P in (('OLD', OLD), ('NEW', NEW)):
    G = np.array([ground(p) for p in P]); C = densify(smooth(G))
    k = curv(C); s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(C, axis=0), axis=1))])
    i = np.argmax(np.abs(k)); sp = S.project(np.c_[C, np.zeros(len(C))])
    print(name, 'len', round(s[-1], 2), 'min radius', round(1 / np.abs(k).max(), 2), 'at s', round(s[i], 2), 'screen', sp[i].round(1))
    for j in range(0, 600, 30): print('   s %.1f R %.2f pt (%.0f,%.0f)' % (s[j], 1 / max(abs(k[j]), 1e-6), sp[j][0], sp[j][1]))
# bridge axis
B = world_verts(need('B_pons1')); c = B[:, :2].mean(0); U, Sg, Vt = np.linalg.svd(B[:, :2] - c); ax = Vt[0]
print('bridge centre', c.round(2), 'axis', ax.round(3), 'len', round(Sg[0], 2), 'screen centre', S.to_pt(Vector((c[0], c[1], 0))).round(1))
proj = (B[:, :2] - c) @ ax; e1 = c + ax * proj.max(); e0 = c + ax * proj.min()
print('bridge ends', [S.to_pt(Vector((e[0], e[1], 0.6))).round(1) for e in (e0, e1)])
g0 = ground(np.array((300, 658))); g1 = ground(np.array((320, 652)))
d = (g1 - g0) / np.linalg.norm(g1 - g0); print('old road dir at bridge', d.round(3), 'angle vs bridge axis', round(math.degrees(math.acos(abs(d @ ax))), 1))
print('wpp', S.world_per_pt(Vector((g0[0], g0[1], 0))))
