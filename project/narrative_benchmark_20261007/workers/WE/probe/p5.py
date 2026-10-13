import bpy, sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from welib import *
S = Screen(); L = Land()
np.set_printoptions(suppress=True, precision=2, linewidth=250)
def grid(x0, x1, y0, y1, st):
    xs = np.arange(x0, x1 + 1e-6, st); ys = np.arange(y1, y0 - 1e-6, -st)
    G = np.array([[L.z(x, y) for x in xs] for y in ys])
    print('x:', xs.round(1)); 
    for y, row in zip(ys, G): print(f'{y:7.1f}', row)
print('C5 area'); grid(50, 74, -34, -10, 1.0)
print('bench area'); grid(12, 34, 37, 58, 1.0)
c = bpy.data.objects['C5_researchers']; CW = world_verts(c)
# C5 vertices: bottom profile: for xy cells, min z of C5 verts
H, xe, ye = np.histogram2d(CW[:,0], CW[:,1], bins=[np.arange(56,68,1.0), np.arange(-27,-17,1.0)])
mins = np.full(H.shape, np.nan)
ix = np.digitize(CW[:,0], xe)-1; iy = np.digitize(CW[:,1], ye)-1
for i in range(H.shape[0]):
    for j in range(H.shape[1]):
        m = (ix==i)&(iy==j)
        if m.any(): mins[i,j] = CW[m,2].min()
print('C5 min z by cell (rows x 56..67, cols y -27..-18)'); print(mins)
