import bpy, sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from welib import *
S = Screen(); L = Land()
sc = bpy.context.scene; dg = bpy.context.evaluated_depsgraph_get()
np.set_printoptions(suppress=True, precision=2, linewidth=250)
cx, cy = 57.0, 4.5
print('rows: azimuth deg (from pad centre); cols: r; value z / visible(1) / screen y')
for az in range(60, 181, 15):
    line = f'az {az:3d}:'
    for r in np.arange(5.0, 11.01, 0.5):
        x = cx + r * np.cos(np.radians(az)); y = cy + r * np.sin(np.radians(az))
        z = L.z(x, y)
        p = Vector((x, y, z))
        pt = S.to_pt(p)
        o, d = S.ray(pt)
        h = sc.ray_cast(dg, o, d)
        vis = h[0] and h[4].name == 'T_land' and (h[1] - p).length < 0.05
        oname = h[4].name[:6] if h[0] else '-'
        line += f' {z:4.2f}{"v" if vis else "."}{oname if not vis else "":6s}{pt[1]:5.0f}|'
    print(line)
