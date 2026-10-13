import bpy, sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from welib import *
S = Screen()
out = Path(sys.argv[sys.argv.index('--') + 1])
sc = bpy.context.scene; dg = bpy.context.evaluated_depsgraph_get()
print('light', sc.display.shading.light, sc.display.shading.studio_light, sc.display.shading.use_world_space_lighting, sc.display.shading.studiolight_rotate_z, tuple(sc.display.light_direction), sc.display.shadow_shift, sc.display.shadow_focus, sc.display.shading.shadow_intensity)
land = bpy.data.objects['T_land']
bvh, _ = bvh_of([land])
rows = []
boxes = {'cube4': (690, 870, 1140, 1275), 'privn': (1000, 1150, 950, 1040), 'flat': (560, 690, 1090, 1160), 'hill': (860, 1000, 1040, 1130)}
for n, (x0, x1, y0, y1) in boxes.items():
    for y in np.arange(y0, y1, 1.0):
        for x in np.arange(x0, x1, 1.0):
            o, d = S.ray((x, y))
            r = sc.ray_cast(dg, o, d)
            if not r[0] or r[4].name != 'T_land':
                continue
            h = bvh.ray_cast(o, d)
            nrm = h[1]
            rows.append((x, y, *r[1][:], *nrm[:], ['cube4', 'privn', 'flat', 'hill'].index(n)))
np.save(out, np.array(rows))
print('rows', len(rows))
