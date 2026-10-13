import bpy, sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from welib import *
S = Screen()
np.set_printoptions(suppress=True, precision=3, linewidth=220)
road = bpy.data.objects['R_core_road']
W, lab, flab, ls, lt, lv = face_islands(road)
n = lab.max() + 1; nf = np.bincount(flab, minlength=n)
for ln in ('R1_road_landing1', 'R1_road_landing5'):
    l = bpy.data.objects[ln]; Wl = world_verts(l); c = Wl[:, :2].mean(0); r = np.linalg.norm(Wl[:, :2] - c, axis=1).max()
    print(ln, 'c', c, 'r', r, 'z', Wl[:, 2].min(), Wl[:, 2].max())
    near = []
    for k in range(n):
        w = W[lab == k]; cc = w[:, :2].mean(0); d = np.linalg.norm(cc - c)
        if nf[k] < 40 and d < r + 1.5:
            near.append((k, nf[k], round(d, 2), S.project(w.mean(0)[None])[0].round(1), round(w[:, 2].max(), 3)))
    # paving centroids within 4 -> axis
    cs = np.array([W[lab == k, :2].mean(0) for k in range(n) if nf[k] < 40 and 1.5 < np.linalg.norm(W[lab == k, :2].mean(0) - c) < 5])
    ax = (c - cs.mean(0)); ax /= np.linalg.norm(ax)
    print(' road axis toward dead end', ax)
    for k, f, d, p, zt in near:
        t = (W[lab == k, :2].mean(0) - c) @ ax
        if d > r - 0.1: print('  outside-ish', k, f, d, 't', round(t, 2), 'pt', p, 'ztop', zt)
    # kerb faces near
    for k in range(n):
        if nf[k] < 40: continue
        fs = np.nonzero(flab == k)[0]
        fc = np.array([W[lv[ls[f]:ls[f] + lt[f]]].mean(0) for f in fs])
        d = np.linalg.norm(fc[:, :2] - c, axis=1)
        m = d < r + 1.0
        if m.any():
            t = (fc[m, :2] - c) @ ax
            print('  kerb', k, 'faces near', m.sum(), 'beyond disc (d>r & t>0)', int(((d[m] > r) & (t > 0)).sum()), 'pt', S.project(fc[m][(d[m] > r) & (t > 0)]).round(1)[:6].tolist())
