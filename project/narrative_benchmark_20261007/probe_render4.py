import bpy
OUT = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/oc_b5_r11/rtest/'
sc = bpy.context.scene; r = sc.render; sh = sc.display.shading
keep = {n for n in bpy.data.objects.keys() if n.startswith('S_sect') or n.startswith('S_lead') or n.startswith('S_pin_pompeii') or n.startswith('S_pin_harbor')}
for o in bpy.data.objects:
    if o.type in ('MESH', 'CURVE', 'FONT', 'SURFACE', 'META'):
        o.hide_render = o.name not in keep
r.film_transparent = True; r.resolution_percentage = 72; r.use_border = True; r.use_crop_to_border = True
r.image_settings.file_format = 'PNG'; r.image_settings.color_mode = 'RGBA'
FW, FH = 1191.0, 1684.0
regions = {'sect': (302.6, 430.4, 1208.7, 1327.8), 'pomp': (710.3, 737.7, 1480.3, 1557.0), 'harb': (184.3, 234.1, 1483.3, 1529.8)}
def go(name, reg):
    x0, x1, y0, y1 = regions[reg]
    r.border_min_x = x0 / FW; r.border_max_x = x1 / FW; r.border_min_y = 1 - y1 / FH; r.border_max_y = 1 - y0 / FH
    r.filepath = OUT + name; bpy.ops.render.render(write_still=True)
sh.show_cavity = False; sh.show_object_outline = False
for reg in regions: go(f'{reg}_flat.png', reg)
sh.show_cavity = True; sh.show_object_outline = True
go('harb_asis.png', 'harb')
print('RDONE4')
