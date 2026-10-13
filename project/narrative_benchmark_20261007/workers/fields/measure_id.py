"""ID pass for measurement only (never saved): every RC.v12_13.field_* material gets a unique flat colour, all
other materials black, same camera / resolution / visible collections as the map pass of render_two_pass.
Run: Blender -b fields_test.blend --factory-startup --python measure_id.py -- <out_id.png> <out_ids.json>"""
import bpy, sys, json
from pathlib import Path
argv = sys.argv[sys.argv.index('--') + 1:]
out_png, out_json = Path(argv[0]), Path(argv[1])
OVERLAY = {'80_SHAPES', '81_NOSHADOW', '85_HEADER'}
sc = bpy.context.scene; sh = sc.display.shading
ids = {}
k = 0
def to_lin(c): return ((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92
for m in sorted(bpy.data.materials, key=lambda m: m.name):
    if m.name.startswith('RC.v12_13.field_') or m.name == 'RC.v12.base_field':
        k += 1
        rgb = ((k * 37) % 7 * 36 + 20, (k * 53) % 5 * 50 + 20, (k // 7) * 90 + 40)
        ids[m.name] = rgb
        m.diffuse_color = (*(to_lin(c / 255) for c in rgb), 1)
    else:
        m.diffuse_color = (0, 0, 0, 1)
for o in bpy.data.objects:
    if o.type == 'MESH' and not o.material_slots:
        o.color = (0, 0, 0, 1)
sh.light = 'FLAT'; sh.color_type = 'MATERIAL'; sh.show_shadows = False; sh.show_cavity = False
sh.show_object_outline = False; sh.show_specular_highlight = False
sc.display.render_aa = 'OFF'
sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'; sc.view_settings.exposure = 0; sc.view_settings.gamma = 1
sc.render.dither_intensity = 0
saved = {c.name: c.hide_render for c in bpy.data.collections}
for c in bpy.data.collections: c.hide_render = saved[c.name] or c.name in OVERLAY
sc.render.film_transparent = True; sc.render.use_border = False; sc.render.resolution_percentage = 48
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'
sc.render.filepath = str(out_png)
bpy.ops.render.render(write_still=True)
out_json.write_text(json.dumps(ids, indent=1))
print('IDS', json.dumps(ids))
