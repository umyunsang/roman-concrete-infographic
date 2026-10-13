import bpy, sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from welib import *
S = Screen(); L = Land()
np.set_printoptions(suppress=True, precision=3, linewidth=220)
o = bpy.data.objects['B_pons1']
W, lab, flab, ls, lt, lv = face_islands(o)
for k in (0, 1, 4):
    idx = np.nonzero(lab == k)[0]
    print('island', k)
    for i in idx:
        print('  v', i, W[i], 'T', round(L.z(*W[i, :2]), 3), 'pt', S.project(W[i:i+1])[0].round(1))
    for f in np.nonzero(flab == k)[0]:
        print('  f', f, lv[ls[f]:ls[f]+lt[f]].tolist(), 'n', np.round(o.data.polygons[f].normal[:], 2))
