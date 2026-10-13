"""Offline design of the NW road centreline: heading integrated from a bounded curvature profile (R >= RMIN),
starting straight off the B_pons1 deck along its axis and ending at the R1_road_landing1 centre, with screen
clearances to the Colosseum, Pantheon, fields, milestone and river as penalties."""
import sys, json
import numpy as np
from scipy.spatial import cKDTree
from scipy.optimize import minimize
from scipy.interpolate import RegularGridInterpolator

D = np.load(sys.argv[1]); RMIN = float(sys.argv[2]) if len(sys.argv) > 2 else 4.0
M = D['M']; tzf = RegularGridInterpolator((D['ty'], D['tx']), D['tz'])
def tz(P): return tzf(np.c_[P[:, 1], P[:, 0]])
def proj(W):
    H = np.c_[W, np.ones(len(W))] @ M.T; n = H[:, :2] / H[:, 3:4]
    return np.c_[(n[:, 0] + 1) / 2 * 1191, (1 - (n[:, 1] + 1) / 2) * 1684]
ax = D['bridge_axis']; bend = D['bridge_c'] + ax * D['bridge_proj_max']
TUCK, LEAD, HALF, DS = 0.6, 1.6, 1.97, 0.05
P0 = bend - ax * TUCK; th0 = np.arctan2(ax[1], ax[0])
P1 = D['landing_c'][:2]
TREES = {k[4:]: cKDTree(D[k]) for k in D.files if k.startswith('obs_')}
NEED = {'COL_ruined': 7.5, 'R8_pantheon': 9.0, 'F_centuriatio': 3.0, 'MS1_core1_to_2': 6.0, 'L01_gennaro': 4.0,
        'R3_colosseum_podium': 6.0, 'L02_tiber': 3.0, 'W_water_marks': 3.0}
K = 12
def path(x):
    u, L = x[:K], x[K]
    s = np.arange(0, L + 1e-9, DS)
    knots = np.linspace(LEAD, L, K)
    kap = np.interp(s, knots, np.tanh(u) / RMIN); kap[s < LEAD] = 0.0
    th = th0 + np.concatenate([[0], np.cumsum(kap[:-1] * DS)])
    P = P0 + np.concatenate([[[0, 0]], np.cumsum(np.c_[np.cos(th[:-1]), np.sin(th[:-1])] * DS, axis=0)])
    return s, P, th, kap
def band(s, P, th, step=5):
    N = np.c_[-np.sin(th), np.cos(th)]
    out = []
    for l in (-HALF, -1.0, 0.0, 1.0, HALF):
        E = P[::step] + N[::step] * l; out.append(np.c_[E, tz(E) + 0.13])
    return out
def clear(s, P, th):
    res = {}
    B = band(s, P, th); sb = s[::5]
    for n, need in NEED.items():
        d = np.min([TREES[n].query(proj(E))[0] for E in B], axis=0)
        if n in ('L02_tiber', 'W_water_marks'): d = np.where(sb < 3.0, 99, d)
        res[n] = d
    return res
def cost(x):
    s, P, th, kap = path(x)
    c = 2000 * np.sum((P[-1] - P1) ** 2)
    for n, d in clear(s, P, th).items():
        c += 50 * np.sum(np.clip(NEED[n] - d, 0, None) ** 2)
    dk = np.diff(np.tanh(x[:K])); c += 2.0 * np.sum(dk ** 2) + 0.2 * np.sum(np.tanh(x[:K]) ** 2)
    return c
# initial guess: fit to the user_v8_13 NEW screen path
NEWS = np.array([(300, 658), (320, 649), (340, 622), (360, 590), (380, 560), (390, 548), (400, 542), (410, 539),
                 (420, 535), (430, 533), (440, 534), (460, 532), (480, 527), (500, 522), (520, 519), (540, 516.5)], float)
x0 = np.r_[np.zeros(K), 44.0]
best = None
for seed in range(int(sys.argv[3]) if len(sys.argv) > 3 else 6):
    rng = np.random.default_rng(seed)
    xi = x0 + np.r_[rng.normal(0, 0.8, K), rng.normal(0, 2)]
    r = minimize(cost, xi, method='Powell', options={'maxiter': 60000, 'xtol': 1e-4, 'ftol': 1e-8})
    if best is None or r.fun < best.fun: best = r
    print('seed', seed, 'cost', round(r.fun, 4))
x = best.x; s, P, th, kap = path(x)
cl = clear(s, P, th)
scr = proj(np.c_[P, tz(P)])
out = {'RMIN': RMIN, 'K': K, 'u': x[:K].round(6).tolist(), 'L': round(float(x[K]), 6), 'P0': P0.tolist(), 'th0': float(th0),
       'end_err': float(np.linalg.norm(P[-1] - P1)), 'cost': float(best.fun),
       'clear_min': {n: round(float(d.min()), 2) for n, d in cl.items()},
       'clear_at': {n: scr[::5][int(np.argmin(d))].round(1).tolist() for n, d in cl.items()},
       'Rmin_actual': round(float(1 / max(np.abs(kap).max(), 1e-9)), 3),
       'screen_path': scr[::20].round(1).tolist()}
print(json.dumps(out))
json.dump(out, open(sys.argv[4] if len(sys.argv) > 4 else 'nw_opt_out.json', 'w'))
