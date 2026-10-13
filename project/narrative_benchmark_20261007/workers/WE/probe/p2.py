import bpy, sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from welib import *
S = Screen(); L = Land()
np.set_printoptions(suppress=True, precision=3, linewidth=200)
for bn in ['B_pons1', 'B_pons2']:
    o = bpy.data.objects[bn]
    W, lab, flab, ls, lt, lv = face_islands(o)
    print(bn, 'islands', lab.max() + 1)
    for k in range(lab.max() + 1):
        w = W[lab == k]
        print('  isl', k, 'nv', len(w), 'min', w.min(0), 'max', w.max(0), 'nf', int((flab == k).sum()))
    low = np.nonzero(W[:, 2] < -0.7)[0]
    tz = L.zs(W[low, :2])
    P = S.project(W[low])
    for i, t, p in zip(low, tz, P):
        print('   low v', i, W[i].round(3), 'terrain', round(t, 3), 'pt', p.round(1))
    print('  k pt/unit', S.world_per_pt(Vector(W.mean(0))) ** -1)
