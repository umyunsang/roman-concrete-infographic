import bpy, sys, json, numpy as np, math
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, Terrain, world_verts, need
from mathutils import Vector
from mathutils.kdtree import KDTree
import importlib.util
S = Screen(); TER = Terrain(need('T_land'))
spec = importlib.util.spec_from_file_location('c2', '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout/common.py')
from common import sample_tris, screen_tris
def ground(pt):
    h = TER.bvh.ray_cast(*S.ray(pt))[0]; return np.array((h.x, h.y))
ROI = (280, 600, 440, 720)
KDs = {}
for n in ['COL_ruined', 'R8_pantheon', 'F_centuriatio', 'MS1_core1_to_2', 'L02_tiber', 'W_water_marks', 'R3_colosseum_podium']:
    P, T = screen_tris(need(n), S); pts = sample_tris(P, T, ROI, 0.5)
    if len(pts) == 0: continue
    kd = KDTree(len(pts))
    for i, p in enumerate(pts): kd.insert(Vector((p[0], p[1], 0)), i)
    kd.balance(); KDs[n] = kd
B = world_verts(need('B_pons1')); c = B[:, :2].mean(0); U, Sg, Vt = np.linalg.svd(B[:, :2] - c); ax = Vt[0]
if ax[1] < 0: ax = -ax
def catmull(P, n=40):
    out = []
    P = np.vstack([2 * P[0] - P[1], P, 2 * P[-1] - P[-2]])
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(P[-2]); return np.array(out)
def resample(C, step=0.05):
    s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(C, axis=0), axis=1))])
    u = np.arange(0, s[-1], step); u = np.append(u, s[-1])
    return np.stack([np.interp(u, s, C[:, 0]), np.interp(u, s, C[:, 1])], 1)
def lap(C, it, fix0, fix1):
    C = C.copy()
    for _ in range(it):
        C[fix0:-fix1] = 0.5 * C[fix0:-fix1] + 0.25 * (C[fix0 - 1:-fix1 - 1] + C[fix0 + 1:len(C) - fix1 + 1])
    return C
def curvR(C):
    d1 = np.gradient(C, axis=0); d2 = np.gradient(d1, axis=0)
    k = (d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0]) / np.linalg.norm(d1, axis=1) ** 3
    return k
def build(WP, lead=2.0, it=300, tuck=0.0):
    G = np.array([ground(np.array(p, float)) for p in WP])
    g0 = G[0] - ax * tuck
    G = np.vstack([g0, g0 + ax * lead, G[1:]])
    C = resample(catmull(G), 0.05)
    fix0 = int(lead / 0.05 * 0.6) + 1
    C = lap(C, it, fix0, 8)
    C = resample(C, 0.05)
    return C
HALF = 1.97
def evaluate(C):
    k = curvR(C); i = int(np.argmax(np.abs(k)))
    T = np.gradient(C, axis=0); T /= np.linalg.norm(T, axis=1)[:, None]; N = np.stack([-T[:, 1], T[:, 0]], 1)
    res = {'len': round(float(np.sum(np.linalg.norm(np.diff(C, axis=0), axis=1))), 2), 'Rmin': round(float(1 / np.abs(k).max()), 2),
           'Rmin_at': S.project(np.c_[C[i], 0][None] if False else np.array([[C[i][0], C[i][1], 0]]))[0].round(1).tolist()}
    gaps = {}
    for l in np.linspace(-HALF, HALF, 9):
        E = C + N * l; Z = np.array([TER.z(x, y) + 0.1 for x, y in E]); P = S.project(np.c_[E, Z])
        for n, kd in KDs.items():
            d = min(kd.find(Vector((p[0], p[1], 0)))[1:] for p in P[::2])  # (index, dist) min by index? fix below
    for n, kd in KDs.items():
        best = (1e9, None)
        for l in np.linspace(-HALF, HALF, 9):
            E = C + N * l; Z = np.array([TER.z(x, y) + 0.1 for x, y in E]); P = S.project(np.c_[E, Z])
            for p in P[::2]:
                d = kd.find(Vector((p[0], p[1], 0)))[2]
                if d < best[0]: best = (d, p)
        gaps[n] = [round(best[0], 2), best[1].round(1).tolist()]
    res['gaps'] = gaps
    # radius profile in screen
    prof = []
    for j in range(0, len(C), 40):
        prof.append([S.project(np.array([[C[j][0], C[j][1], 0]]))[0].round(0).tolist(), round(float(1 / max(abs(k[j]), 1e-6)), 1)])
    res['profile'] = prof
    return res
CANDS = json.loads(open(sys.argv[sys.argv.index('--') + 1]).read())
for name, cfg in CANDS.items():
    C = build(cfg['wp'], cfg.get('lead', 2.0), cfg.get('it', 300), cfg.get('tuck', 0.0))
    r = evaluate(C)
    print('CAND', name, json.dumps({k: v for k, v in r.items() if k != 'profile'}))
    print('   PROFILE', r['profile'])
