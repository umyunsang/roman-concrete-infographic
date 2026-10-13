"""rcrop.py - border two-pass crop renders (map + overlay passes) of a blend, read-only.
Blender -b <blend> --factory-startup --python rcrop.py -- <out_prefix> <scale px/pt> x0,x1,y0,y1 [x0,x1,y0,y1 ...]
Writes <out_prefix>_<i>_map.png and _ovl.png. Composite with comp.py."""
import bpy, sys, math
from pathlib import Path
OVL = {'80_SHAPES', '81_NOSHADOW', '85_HEADER'}
argv = sys.argv[sys.argv.index('--') + 1:]
pref = Path(argv[0]); s = float(argv[1]); boxes = [tuple(map(float, a.split(','))) for a in argv[2:]]
sc = bpy.context.scene; r = sc.render; sh = sc.display.shading
base_x = r.resolution_x; base_y = r.resolution_y
pct = s / (base_x / 1191.0) * 100.0
pct_i = int(round(pct))
winx = base_x * pct_i // 100; winy = base_y * pct_i // 100
sp = winx / 1191.0
saved = {c.name: c.hide_render for c in bpy.data.collections}
for i, (x0, x1, y0, y1) in enumerate(boxes):
    X0, X1, Y0, Y1 = math.floor(x0 * sp), math.ceil(x1 * sp), math.floor(y0 * sp), math.ceil(y1 * sp)
    r.resolution_percentage = pct_i
    r.use_border = True; r.use_crop_to_border = True
    r.border_min_x = (X0 + 0.5) / winx; r.border_max_x = (X1 + 0.5) / winx
    r.border_min_y = (winy - Y1 + 0.5) / winy; r.border_max_y = (winy - Y0 + 0.5) / winy
    for c in bpy.data.collections:
        c.hide_render = saved[c.name] or c.name in OVL
    r.film_transparent = False; sh.show_shadows = True
    r.filepath = str(pref) + f'_{i}_map.png'; bpy.ops.render.render(write_still=True)
    for c in bpy.data.collections:
        c.hide_render = saved[c.name] or c.name not in OVL | {'Collection'}
    r.film_transparent = True; sh.show_shadows = False
    r.filepath = str(pref) + f'_{i}_ovl.png'; bpy.ops.render.render(write_still=True)
    for c in bpy.data.collections:
        c.hide_render = saved[c.name]
    print('RCROP', i, (x0, x1, y0, y1), 'px/pt', sp, 'origin_px', X0, Y0)
