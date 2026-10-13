"""디버그: 화면 pt 상자를 원래 해상도 100%로 테두리 렌더(지도 패스 설정 그대로) → renders/_zoom.png. 설정은 되돌림."""
import bpy, json
ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_A/'
BOXZ = globals().get('ZBOX', None) or tuple(json.load(open(ROOT + 'renders/_zoombox.json')))
sc = bpy.context.scene; r = sc.render; vs = sc.view_settings
st = (r.use_border, r.use_crop_to_border, r.border_min_x, r.border_max_x, r.border_min_y, r.border_max_y, r.resolution_percentage, r.filepath, vs.exposure)
hid = {}
for n in ('80_SHAPES', '85_HEADER', '81_NOSHADOW'):
    c = bpy.data.collections.get(n)
    if c:
        hid[n] = c.hide_render; c.hide_render = True
r.use_border = True; r.use_crop_to_border = True
r.border_min_x = BOXZ[0] / 1191; r.border_max_x = BOXZ[2] / 1191
r.border_min_y = 1 - BOXZ[3] / 1684; r.border_max_y = 1 - BOXZ[1] / 1684
r.resolution_percentage = 100; vs.exposure = float(sc.get('map_exposure', vs.exposure))
r.filepath = ROOT + 'renders/_zoom.png'
bpy.ops.render.render(write_still=True)
(r.use_border, r.use_crop_to_border, r.border_min_x, r.border_max_x, r.border_min_y, r.border_max_y, r.resolution_percentage, r.filepath, vs.exposure) = st
for n, v in hid.items():
    bpy.data.collections[n].hide_render = v
print('zoom render', BOXZ)
