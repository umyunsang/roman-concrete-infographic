"""NW road centreline as line - arc(left) - line - arc(right) - line - arc - line on the ground: starts straight off the
B_pons1 deck along its axis, ends at the R1_road_landing1 centre. Radii >= RMIN. Screen clearances as penalties."""
import sys, json
import numpy as np
from scipy.optimize import minimize
from scipy.interpolate import RegularGridInterpolator
from scipy.ndimage import distance_transform_edt, map_coordinates

D = np.load(sys.argv[1]); RMIN = float(sys.argv[2]); OUT = sys.argv[3]
M = D['M']; tzf = RegularGridInterpolator((D['ty'], D['tx']), D['tz'], bounds_error=False, fill_value=None)
def tz(P): return tzf(np.c_[P[:, 1], P[:, 0]])
def proj(W):
    H = np.c_[W, np.ones(len(W))] @ M.T; n = H[:, :2] / H[:, 3:4]
    return np.c_[(n[:, 0] + 1) / 2 * 1191, (1 - (n[:, 1] + 1) / 2) * 1684]
ax = D['bridge_axis']; bend = D['bridge_c'] + ax * D['bridge_proj_max']
TUCK, HALF, DS = 0.6, 1.97, 0.05
P0 = bend - ax * TUCK; th0 = float(np.arctan2(ax[1], ax[0])); P1 = D['landing_c'][:2]
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
NEED = {'COL_ruined': 7.5, 'R8_pantheon': 9.0, 'F_centuriatio': 4.0, 'MS1_core1_to_2': 6.0, 'L01_gennaro': 4.0,
        'R3_colosseum_podium': 6.0, 'L02_tiber': 3.0, 'W_water_marks': 3.0}
def softplus(x): return np.log1p(np.exp(-np.abs(x))) + np.maximum(x, 0)
def segs(x):
    """x = [a, al1, r1, b, al2, r2, c, al3, r3, d]: straight a, arc al1 (left +) radius RMIN+softplus(r1), ..."""
    a, al1, r1, b, al2, r2, c, al3, r3, d = x
    out = [(max(a, 1.6), 0.0), (abs(al1) * (RMIN + softplus(r1)), al1 / (abs(al1) * (RMIN + softplus(r1)) + 1e-9)),
           (max(b, 0.0), 0.0), (abs(al2) * (RMIN + softplus(r2)), al2 / (abs(al2) * (RMIN + softplus(r2)) + 1e-9)),
           (max(c, 0.0), 0.0), (abs(al3) * (RMIN + softplus(r3)), al3 / (abs(al3) * (RMIN + softplus(r3)) + 1e-9)),
           (max(d, 0.0), 0.0)]
    return out
def path(x):
    th = th0; P = [P0.copy()]; ths = [th]; kap = [0.0]; p = P0.copy()
    for L, k in segs(x):
        n = int(round(L / DS))
        for _ in range(n):
            th_mid = th + k * DS / 2
            p = p + DS * np.array((np.cos(th_mid), np.sin(th_mid))); th += k * DS
            P.append(p.copy()); ths.append(th); kap.append(k)
    return np.array(P), np.array(ths), np.array(kap)
def clear(P, th, step=5):
    N = np.c_[-np.sin(th), np.cos(th)]; res = {}
    s = np.arange(len(P)) * DS
    E = [P[::step] + N[::step] * l for l in (-HALF, -1.0, 0.0, 1.0, HALF)]
    Q = [proj(np.c_[e, tz(e) + 0.13]) for e in E]
    for n, need in NEED.items():
        d = np.min([F[n].query(q) for q in Q], axis=0)
        if n in ('L02_tiber', 'W_water_marks'): d = np.where(s[::step] < 3.0, 99, d)
        res[n] = d
    return res, Q
def cost(x):
    P, th, kap = path(x)
    if len(P) < 10: return 1e9
    c = 3000 * np.sum((P[-1] - P1) ** 2)
    cl, _ = clear(P, th)
    for n, d in cl.items():
        c += 80 * np.sum(np.clip(NEED[n] - d, 0, None) ** 2) + 0.3 * np.sum(np.clip(NEED[n] + 2.5 - d, 0, None) ** 2)
    c += 0.05 * np.sum(kap ** 2) * DS * 100
    return c
inits = []
rng = np.random.default_rng(int(sys.argv[4]) if len(sys.argv) > 4 else 0)
base = np.array([2.0, np.radians(35), 1.0, 6.0, np.radians(-70), 1.0, 10.0, np.radians(10), 1.0, 10.0])
best = None
for i in range(int(sys.argv[5]) if len(sys.argv) > 5 else 12):
    x0 = base + rng.normal(0, 1, len(base)) * np.array([0.5, 0.25, 1.0, 3.0, 0.3, 1.0, 4.0, 0.2, 1.0, 4.0])
    r = minimize(cost, x0, method='Powell', options={'maxiter': 20000, 'xtol': 1e-4, 'ftol': 1e-9})
    print(i, round(r.fun, 4), flush=True)
    if best is None or r.fun < best.fun: best = r
x = best.x; P, th, kap = path(x); cl, Q = clear(P, th)
scr = proj(np.c_[P, tz(P)])
segl = [(round(float(L), 3), (round(float(1 / k), 3) if abs(k) > 1e-9 else None)) for L, k in segs(x)]
out = {'RMIN': RMIN, 'x': x.tolist(), 'segments_len_radius': segl, 'P0': P0.tolist(), 'th0': th0, 'cost': float(best.fun),
       'end_err': float(np.linalg.norm(P[-1] - P1)), 'length': round(len(P) * DS, 3),
       'clear_min': {n: round(float(d.min()), 2) for n, d in cl.items()},
       'clear_at': {n: scr[::5][int(np.argmin(d))].round(1).tolist() for n, d in cl.items()},
       'screen_path': scr[::20].round(1).tolist()}
print(json.dumps(out)); json.dump(out, open(OUT, 'w'))
