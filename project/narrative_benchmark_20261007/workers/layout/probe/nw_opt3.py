"""NW road centreline: smooth spline through ground control points. Start = B_pons1 deck end (tucked 0.6 under it)
with the first 1.6 units along the bridge axis; end = landing centre. Penalties: curvature radius < RMIN, screen
clearances to Colosseum/Pantheon/fields/milestone/river, and a weak pull toward the user_v8_13 line (cn_orig)."""
import sys, json
import numpy as np
from scipy.optimize import minimize
from scipy.interpolate import RegularGridInterpolator, CubicSpline
from scipy.ndimage import distance_transform_edt, map_coordinates

D = np.load(sys.argv[1]); ORIG = np.load(sys.argv[2])['Cn']; RMIN = float(sys.argv[3]); OUT = sys.argv[4]
NCP = int(sys.argv[5]) if len(sys.argv) > 5 else 14
M = D['M']; tzf = RegularGridInterpolator((D['ty'], D['tx']), D['tz'], bounds_error=False, fill_value=None)
def tz(P): return tzf(np.c_[P[:, 1], P[:, 0]])
def proj(W):
    H = np.c_[W, np.ones(len(W))] @ M.T; n = H[:, :2] / H[:, 3:4]
    return np.c_[(n[:, 0] + 1) / 2 * 1191, (1 - (n[:, 1] + 1) / 2) * 1684]
ax = D['bridge_axis']; bend = D['bridge_c'] + ax * D['bridge_proj_max']
TUCK, LEAD, HALF, DS = 0.6, 1.6, 1.97, 0.05
P0 = bend - ax * TUCK; P0b = P0 + ax * LEAD; P1 = D['landing_c'][:2]
GX0, GX1, GY0, GY1, GS = 260.0, 620.0, 430.0, 720.0, 4.0
class Field:
    def __init__(self, pts):
        m = np.zeros((int((GY1 - GY0) * GS), int((GX1 - GX0) * GS)), bool)
        ij = np.floor((pts - (GX0, GY0)) * GS).astype(int)
        ok = (ij[:, 0] >= 0) & (ij[:, 0] < m.shape[1]) & (ij[:, 1] >= 0) & (ij[:, 1] < m.shape[0])
        m[ij[ok, 1], ij[ok, 0]] = True
        self.d = distance_transform_edt(~m) / GS
    def query(self, q):
        c = np.vstack([(q[:, 1] - GY0) * GS - 0.5, (q[:, 0] - GX0) * GS - 0.5])
        return map_coordinates(self.d, c, order=1, mode='nearest')
F = {k[4:]: Field(D[k]) for k in D.files if k.startswith('obs_')}
NEED = {'COL_ruined': 7.0, 'R8_pantheon': 9.5, 'F_centuriatio': 4.5, 'MS1_core1_to_2': 6.0, 'L01_gennaro': 4.0,
        'R3_colosseum_podium': 6.0, 'L02_tiber': 3.0, 'W_water_marks': 3.0}
# initial control points: the user_v8_13 centreline resampled by arc length
so = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(ORIG, axis=0), axis=1))])
def at_s(C, s_arr, s):
    return np.c_[np.interp(s, s_arr, C[:, 0]), np.interp(s, s_arr, C[:, 1])]
mid = at_s(ORIG, so, np.linspace(so[-1] * 0.12, so[-1] * 0.93, NCP))
def curve(z):
    Q = np.vstack([P0, P0b, z.reshape(-1, 2), P1])
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(Q, axis=0), axis=1))]
    cs = CubicSpline(d, Q, bc_type=((1, ax), 'not-a-knot'))
    t = np.arange(0, d[-1], DS / 2); P = cs(t)
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    u = np.arange(0, s[-1], DS); P = at_s(P, s, u)
    return P
def geom(P):
    d1 = np.gradient(P, axis=0); d2 = np.gradient(d1, axis=0)
    k = (d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0]) / np.maximum(np.linalg.norm(d1, axis=1), 1e-9) ** 3
    T = d1 / np.maximum(np.linalg.norm(d1, axis=1), 1e-9)[:, None]; N = np.c_[-T[:, 1], T[:, 0]]
    return k, N
def clear(P, N, step=5):
    s = np.arange(len(P)) * DS; res = {}
    Q = [proj(np.c_[e, tz(e) + 0.13]) for e in (P[::step] + N[::step] * l for l in (-HALF, -1.0, 0.0, 1.0, HALF))]
    for n in NEED:
        d = np.min([F[n].query(q) for q in Q], axis=0)
        if n in ('L02_tiber', 'W_water_marks'): d = np.where(s[::step] < 3.0, 99, d)
        res[n] = d
    return res, Q
def cost(z, verbose=False):
    P = curve(z); k, N = geom(P)
    c = 400 * np.sum(np.clip(np.abs(k[4:-4]) - 1 / RMIN, 0, None) ** 2) * DS * 100
    cl, _ = clear(P, N)
    for n, d in cl.items():
        c += 60 * np.sum(np.clip(NEED[n] - d, 0, None) ** 2) + 0.4 * np.sum(np.clip(NEED[n] + 2.0 - d, 0, None) ** 2)
    dk = np.diff(k[4:-4]); c += 30 * np.sum(dk ** 2)
    c += 0.02 * np.sum((z.reshape(-1, 2) - mid) ** 2)
    return c
z0 = mid.ravel().copy()
best = None
rng = np.random.default_rng(0)
for trial in range(int(sys.argv[6]) if len(sys.argv) > 6 else 3):
    zi = z0 + (rng.normal(0, 0.5, z0.shape) if trial else 0)
    r = minimize(cost, zi, method='Powell', options={'maxiter': 40000, 'xtol': 1e-4, 'ftol': 1e-10})
    r = minimize(cost, r.x, method='Powell', options={'maxiter': 40000, 'xtol': 1e-5, 'ftol': 1e-12})
    print('trial', trial, round(r.fun, 4), flush=True)
    if best is None or r.fun < best.fun: best = r
z = best.x; P = curve(z); k, N = geom(P); cl, Q = clear(P, N)
scr = proj(np.c_[P, tz(P)])
i = int(np.argmax(np.abs(k[4:-4]))) + 4
out = {'RMIN': RMIN, 'NCP': NCP, 'ctrl': np.vstack([P0, P0b, z.reshape(-1, 2), P1]).round(5).tolist(), 'cost': float(best.fun),
       'length': round(len(P) * DS, 3), 'Rmin_actual': round(float(1 / np.abs(k[4:-4]).max()), 3), 'Rmin_at': scr[i].round(1).tolist(),
       'clear_min': {n: round(float(d.min()), 2) for n, d in cl.items()},
       'clear_at': {n: scr[::5][int(np.argmin(d))].round(1).tolist() for n, d in cl.items()},
       'screen_path': scr[::20].round(1).tolist()}
print(json.dumps(out)); json.dump(out, open(OUT, 'w'))
