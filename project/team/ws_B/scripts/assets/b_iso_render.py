"""시험: B_ISO 물체만 보이게 부분 렌더(되돌림)"""
import os, bpy
sc = bpy.context.scene; r = sc.render
keep = set(os.environ.get('B_ISO', 'L07_vesuvius').split(','))
inv = os.environ.get('B_ISO_INV') == '1'
box = [float(x) for x in os.environ.get('BT_BOX', '880,1220,1191,1560').split(',')]
st = {o.name: o.hide_render for o in bpy.data.objects}
for o in bpy.data.objects:
    if o.type == 'MESH':
        o.hide_render = (o.name in keep) if inv else (o.name not in keep)
W, H = 1191.0, 1684.0
r.use_border = True; r.use_crop_to_border = True
r.border_min_x = box[0] / W; r.border_max_x = box[2] / W; r.border_min_y = 1 - box[3] / H; r.border_max_y = 1 - box[1] / H
r.resolution_percentage = 72
r.filepath = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_B/renders/_test_iso.png'
bpy.ops.render.render(write_still=True)
for n, v in st.items():
    bpy.data.objects[n].hide_render = v
r.use_border = False; r.use_crop_to_border = False; r.resolution_percentage = 48
