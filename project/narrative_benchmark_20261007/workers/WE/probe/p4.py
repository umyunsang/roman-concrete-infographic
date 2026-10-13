import bpy, sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from welib import *
S = Screen(); L = Land()
np.set_printoptions(suppress=True, precision=3, linewidth=220)
land = bpy.data.objects['T_land']
W, ls, lt, lv, E = mesh_arrays(land)
el = np.linalg.norm(W[E[:, 0]] - W[E[:, 1]], axis=1)
print('T_land edge len pct', np.percentile(el, [5, 25, 50, 75, 95, 99]).round(3))
# boundary edges
me = land.data
import bmesh
bm = bmesh.new(); bm.from_mesh(me)
bnd = [e for e in bm.edges if len(e.link_faces) == 1]
print('boundary edges', len(bnd))
bm.free()
# lab bench
b = bpy.data.objects['R1_lab_bench']; BW = world_verts(b)
print('bench verts', BW.round(3))
# C5
c = bpy.data.objects['C5_researchers']; CW = world_verts(c)
low = CW[CW[:, 2] < CW[:, 2].min() + 0.15]
print('C5 low verts', len(low), 'xy min', low[:, :2].min(0), 'max', low[:, :2].max(0), 'z', low[:, 2].min(), low[:, 2].max())
for (x, y) in [(61.9, -22.4), (58, -26), (66, -19), (55, -28), (68, -17), (57, -18), (67, -27), (52, -30), (70, -14)]:
    print('  T at', x, y, round(L.z(x, y), 3))
# aqueduct islands
a = bpy.data.objects['L05_aqua_claudia']
AW, lab, flab, ls2, lt2, lv2 = face_islands(a)
n = lab.max() + 1
zmin = np.array([AW[lab == k, 2].min() for k in range(n)]); zmax = np.array([AW[lab == k, 2].max() for k in range(n)])
print('aqueduct islands', n, 'zmin hist', np.histogram(zmin, bins=[-1, 0, 0.5, 1, 2, 4, 8])[0], 'zmax', np.percentile(zmax, [0, 50, 100]))
# fields islands
f = bpy.data.objects['F_centuriatio']
FW, flab_v, fflab, ls3, lt3, lv3 = face_islands(f)
n = flab_v.max() + 1
nf = np.bincount(fflab, minlength=n)
print('field islands', n, 'faces per island hist', np.unique(nf, return_counts=True))
