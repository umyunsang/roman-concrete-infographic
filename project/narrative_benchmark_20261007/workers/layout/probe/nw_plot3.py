import sys, json, numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, sys.argv[5])
from spline_np import spline_clamped_nak
D = np.load(sys.argv[1]); sol = json.load(open(sys.argv[2])); out = sys.argv[3]
M = D['M']
from scipy.interpolate import RegularGridInterpolator
tzf = RegularGridInterpolator((D['ty'], D['tx']), D['tz'], bounds_error=False, fill_value=None)
def tz(P): return tzf(np.c_[P[:, 1], P[:, 0]])
def proj(W):
    H = np.c_[W, np.ones(len(W))] @ M.T; n = H[:, :2] / H[:, 3:4]
    return np.c_[(n[:, 0] + 1) / 2 * 1191, (1 - (n[:, 1] + 1) / 2) * 1684]
Q = np.array(sol['ctrl']); d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(Q, axis=0), axis=1))]
f = spline_clamped_nak(d, Q, D['bridge_axis']); P = f(np.arange(0, d[-1], 0.025))
T = np.gradient(P, axis=0); T /= np.linalg.norm(T, axis=1)[:, None]; N = np.c_[-T[:, 1], T[:, 0]]
GX0, GY0, SC = 260, 430, 3
im = Image.new('RGB', (int(360 * SC), int(290 * SC)), 'white'); dr = ImageDraw.Draw(im)
cols = {'COL_ruined': (200, 140, 80), 'R8_pantheon': (150, 80, 40), 'F_centuriatio': (90, 160, 90), 'MS1_core1_to_2': (180, 0, 0),
        'L02_tiber': (80, 160, 220), 'W_water_marks': (80, 160, 220), 'R1_road_landing1': (120, 120, 120), 'B_pons1': (100, 100, 100),
        'R3_colosseum_podium': (210, 200, 170)}
for k, c in cols.items():
    for x, y in D['obs_' + k][::7]: dr.point(((x - GX0) * SC, (y - GY0) * SC), fill=c)
for l in (-1.97, 0, 1.97):
    E = P + N * l; q = proj(np.c_[E, tz(E) + 0.13]); dr.line([((a - GX0) * SC, (b - GY0) * SC) for a, b in q], fill=(0, 0, 0), width=1)
for x, y in proj(np.c_[Q, tz(Q)]): dr.ellipse(((x - GX0) * SC - 3, (y - GY0) * SC - 3, (x - GX0) * SC + 3, (y - GY0) * SC + 3), outline=(255, 0, 255))
for gx in range(280, 620, 20): dr.text(((gx - GX0) * SC, 2), str(gx), fill=(0, 0, 0))
for gy in range(440, 720, 20): dr.text((2, (gy - GY0) * SC), str(gy), fill=(0, 0, 0))
im.save(out)
k = (np.gradient(T[:, 0]) * T[:, 1] - np.gradient(T[:, 1]) * T[:, 0]) / 0.025
print('Rmin numpy', 1 / np.abs(k[8:-8]).max())
