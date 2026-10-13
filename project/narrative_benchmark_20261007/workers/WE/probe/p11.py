import bpy, sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from welib import *
L = Land()
R = np.load(str(Path(__file__).parent / 'win_normals.npy'))
np.set_printoptions(suppress=True, precision=3, linewidth=220)
for n, (x0, x1, y0, y1) in {'cube4': (700, 860, 1160, 1265), 'privn': (1040, 1110, 975, 1005), 'flat': (600, 680, 1100, 1150)}.items():
    m = (R[:, 0] >= x0) & (R[:, 0] < x1) & (R[:, 1] >= y0) & (R[:, 1] < y1)
    Wp = R[m, 2:5][::7]; N = R[m, 5:8][::7]
    fs = np.degrees(np.arccos(N[:, 2]))
    ms = []
    for x, y, z in Wp:
        h = 0.6
        gx = (L.z(x + h, y) - L.z(x - h, y)) / (2 * h); gy = (L.z(x, y + h) - L.z(x, y - h)) / (2 * h)
        ms.append(np.degrees(np.arctan(np.hypot(gx, gy))))
    ms = np.array(ms)
    print(n, 'face slope p50/p90', np.nanpercentile(fs, [50, 90]).round(1), 'macro(1.2u) slope p50/p90', np.nanpercentile(ms, [50, 90]).round(1))
# local mesh: vertices around privn point
land = bpy.data.objects['T_land']; W, ls, lt, lv, E = mesh_arrays(land)
m = (np.abs(W[:, 0] - 51.5) < 1.5) & (np.abs(W[:, 1] - 11.5) < 1.5)
print('verts near privn', m.sum(), W[m][:30])
