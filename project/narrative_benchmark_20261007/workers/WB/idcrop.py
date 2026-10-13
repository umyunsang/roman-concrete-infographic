"""idcrop.py - read-only object-ID and material-ID passes in a border crop (map + overlay passes).
Blender -b <blend> --factory-startup --python idcrop.py -- <out.npz> <px_per_pt> x0,x1,y0,y1
npz: obj_map, obj_ovl (int codes, 0 = none), mat_map, mat_ovl, names (object list), mats (material list), origin_px, sp
Codes follow inventory.py (ID colour = 2 + 4k per channel, FLAT, AA off, Standard view)."""
import bpy, sys, math, json
import numpy as np
from pathlib import Path
OVL = {'80_SHAPES', '81_NOSHADOW', '85_HEADER'}
argv = sys.argv[sys.argv.index('--') + 1:]
out = Path(argv[0]); s = float(argv[1]); x0, x1, y0, y1 = map(float, argv[2].split(','))
sc = bpy.context.scene; r = sc.render; sh = sc.display.shading; disp = sc.display; vs = sc.view_settings
objs = [o for o in bpy.data.objects if o.type in {'MESH', 'CURVE', 'FONT'}]
mats = list(bpy.data.materials)
def s2l(s):
    return s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4
def code(i):
    return tuple(s2l((2 + 4 * k) / 255.0) for k in (i % 64, (i // 64) % 64, i // 4096))
for i, o in enumerate(objs):
    o.color = (*code(i + 1), 1.0)
for i, m in enumerate(mats):
    m.diffuse_color = (*code(i + 1), 1.0)
pct = int(round(s / (r.resolution_x / 1191.0) * 100.0))
winx = r.resolution_x * pct // 100; winy = r.resolution_y * pct // 100; sp = winx / 1191.0
X0, X1, Y0, Y1 = math.floor(x0 * sp), math.ceil(x1 * sp), math.floor(y0 * sp), math.ceil(y1 * sp)
r.resolution_percentage = pct; r.use_border = True; r.use_crop_to_border = True
r.border_min_x = (X0 + 0.5) / winx; r.border_max_x = (X1 + 0.5) / winx
r.border_min_y = (winy - Y1 + 0.5) / winy; r.border_max_y = (winy - Y0 + 0.5) / winy
r.dither_intensity = 0.0; r.image_settings.file_format = 'PNG'; r.image_settings.color_mode = 'RGBA'; r.image_settings.color_depth = '8'
r.film_transparent = True; sh.light = 'FLAT'
for n in ['show_shadows', 'show_cavity', 'show_object_outline', 'show_specular_highlight', 'show_xray', 'use_dof']:
    setattr(sh, n, False)
disp.render_aa = 'OFF'; vs.view_transform = 'Standard'; vs.look = 'None'; vs.exposure = 0.0; vs.gamma = 1.0; vs.use_curve_mapping = False
saved = {c.name: c.hide_render for c in bpy.data.collections}
res = {}
tmp = out.with_suffix('.tmp.png')
for ct in ('OBJECT', 'MATERIAL'):
    sh.color_type = ct
    for pas in ('map', 'ovl'):
        for c in bpy.data.collections:
            c.hide_render = saved[c.name] or ((c.name in OVL) if pas == 'map' else (c.name not in OVL | {'Collection'}))
        r.filepath = str(tmp); bpy.ops.render.render(write_still=True)
        img = bpy.data.images.load(str(tmp), check_existing=False); w, h = img.size
        px = np.empty(w * h * 4, np.float32); img.pixels.foreach_get(px); bpy.data.images.remove(img)
        px = px.reshape(h, w, 4)[::-1] * 255.0
        k = np.rint((px[..., :3] - 2.0) / 4.0).astype(np.int64)
        c_ = k[..., 0] + 64 * k[..., 1] + 4096 * k[..., 2]
        c_[px[..., 3] <= 127.5] = 0
        res[('obj_' if ct == 'OBJECT' else 'mat_') + pas] = c_.astype(np.int32)
tmp.unlink()
np.savez_compressed(out, **res, names=np.array([''] + [o.name for o in objs]), mats=np.array([''] + [m.name for m in mats]),
                    origin_px=np.array([X0, Y0]), sp=np.array([sp]))
print('IDCROP', out, res['obj_map'].shape, 'sp', sp)
