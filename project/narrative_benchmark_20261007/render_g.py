import bpy, json, sys, os
OUT='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/ov_b1/bl/out'
os.makedirs(OUT,exist_ok=True)
IDX=json.load(open('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/assets_index.json'))
mine=['support_breakwater_block','support_harbor','support_pompeii_site','support_privernum','support_ruin_observers','landmark_pompeii_town','landmark_vesuvius','landmark_lime_kiln','landmark_apennines','landmark_aqueduct']
GROUND=['T_land','L02_tiber','L10_sea']
sc=bpy.context.scene
r=sc.render
r.resolution_percentage=72
r.film_transparent=False
r.image_settings.file_format='PNG'
r.image_settings.color_mode='RGBA'
orig={o.name:o.hide_render for o in bpy.data.objects}
def setvis(names):
    for o in bpy.data.objects:
        if o.type in ('MESH','CURVE','FONT','SURFACE','META','GPENCIL','GREASEPENCIL','CURVES','POINTCLOUD','VOLUME'):
            o.hide_render = o.name not in names
FW,FH=1191.0,1684.0
def border(crop):
    x0,x1,y0,y1=crop
    r.use_border=True; r.use_crop_to_border=True
    r.border_min_x=x0/FW; r.border_max_x=x1/FW
    r.border_min_y=1-y1/FH; r.border_max_y=1-y0/FH
for a in IDX['assets']:
    if a['id'] not in mine: continue
    crop=a['crop_pt']
    # enlarge crop by 30pt for shadow context
    c2=[max(0,crop[0]-30),min(FW,crop[1]+30),max(0,crop[2]-30),min(FH,crop[3]+30)]
    border(c2)
    for tag,names in (('G0',GROUND),('Ig',GROUND+a['objects'])):
        setvis(set(names))
        r.filepath=f'{OUT}/{a["id"]}_{tag}.png'
        bpy.ops.render.render(write_still=True)
    json.dump({'crop2':c2},open(f'{OUT}/{a["id"]}_crop2.json','w'))
print('DONE')
