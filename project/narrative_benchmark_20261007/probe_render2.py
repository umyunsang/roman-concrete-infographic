import bpy, json, os
OUT = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/oc_b5_r11/rtest/'
sc = bpy.context.scene; r = sc.render; sh = sc.display.shading
print('SINFO ' + json.dumps(dict(outline=sh.show_object_outline, outline_color=list(sh.object_outline_color), xray=sh.show_xray,
      bf=sh.show_backface_culling, aa=sc.display.render_aa, shadow_int=sh.shadow_intensity, cav_type=sh.cavity_type,
      wcav=(sh.cavity_ridge_factor, sh.cavity_valley_factor), scav=(sh.curvature_ridge_factor, sh.curvature_valley_factor))))
keep = {'S_core1_badge', 'S_core1_underline'}
for o in bpy.data.objects:
    if o.type in ('MESH', 'CURVE', 'FONT', 'SURFACE', 'META'):
        o.hide_render = o.name not in keep
r.film_transparent = True; r.resolution_percentage = 72; r.use_border = True; r.use_crop_to_border = True
r.image_settings.file_format = 'PNG'; r.image_settings.color_mode = 'RGBA'
FW, FH = 1191.0, 1684.0
x0, x1, y0, y1 = (516.0, 650.4, 373.0, 446.8)
r.border_min_x = x0 / FW; r.border_max_x = x1 / FW; r.border_min_y = 1 - y1 / FH; r.border_max_y = 1 - y0 / FH
def go(name):
    r.filepath = OUT + name; bpy.ops.render.render(write_still=True)
# 1) cavity off + outline off
sh.show_cavity = False; sh.show_object_outline = False; go('core1_nocav_noout.png')
# 2) cavity WORLD only, SCREEN only
sh.show_cavity = True; sh.cavity_type = 'WORLD'; go('core1_world.png')
sh.cavity_type = 'SCREEN'; go('core1_screen.png')
sh.cavity_type = 'BOTH'
# 3) cavity on, underline-only darker diffuse (in-memory copy material)
ul = bpy.data.objects['S_core1_underline']
m0 = ul.active_material
m1 = m0.copy(); m1.name = 'TMP_ul_test'
for hexv in ['#923218', '#8A3016', '#80301A', '#7A2C16']:
    h = hexv.lstrip('#'); srgb = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]
    m1.diffuse_color = (lin[0], lin[1], lin[2], 1.0)
    ul.material_slots[0].material = m1
    go(f'core1_ul_{h}.png')
ul.material_slots[0].material = m0
print('RDONE2')
