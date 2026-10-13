"""Flat ID mask render (not saved): paving material -> green, kerb material -> blue, milestone arrow plate -> red,
everything else black. Same camera / resolution as render_two_pass map pass (48%), overlay collections hidden.
Usage: Blender -b roads_test.blend --factory-startup --python mask_render.py -- <out.png>"""
import bpy, sys
from pathlib import Path
out = sys.argv[sys.argv.index('--') + 1:][0]
sc = bpy.context.scene; sh = sc.display.shading
OVER = {'80_SHAPES', '81_NOSHADOW', '85_HEADER'}
for c in bpy.data.collections:
    if c.name in OVER: c.hide_render = True
col = {'RC.road.selce_basalt': (0, 1, 0, 1), 'RC.road.umbo_limestone': (0, 0, 1, 1), 'RC.v12_1.direction_arrow': (1, 0, 0, 1)}
for m in bpy.data.materials:
    m.diffuse_color = col.get(m.name, (0, 0, 0, 1))
sh.light = 'FLAT'; sh.color_type = 'MATERIAL'; sh.show_shadows = False; sh.show_cavity = False
sh.show_object_outline = False; sh.show_specular_highlight = False
try: sh.show_xray = False
except Exception: pass
sc.display.render_aa = 'OFF'
sh.background_type = 'VIEWPORT'; sh.background_color = (0, 0, 0)
if sc.world: sc.world.color = (0, 0, 0)
sc.view_settings.view_transform = 'Standard'; sc.view_settings.exposure = 0; sc.view_settings.gamma = 1; sc.view_settings.look = 'None'
sc.render.resolution_percentage = 48; sc.render.film_transparent = False; sc.render.use_border = False
sc.render.image_settings.file_format = 'PNG'; sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print('MASK', out, sc.render.resolution_x, sc.render.resolution_y)
