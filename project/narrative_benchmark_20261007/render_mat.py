import bpy, json, os, colorsys
OUT='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/ov_b1/bl/out'
IDX=json.load(open('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/assets_index.json'))
mine=['support_breakwater_block','support_harbor','support_pompeii_site','support_privernum','support_ruin_observers','landmark_pompeii_town','landmark_vesuvius','landmark_lime_kiln','landmark_apennines','landmark_aqueduct']
sc=bpy.context.scene; r=sc.render
r.engine='BLENDER_EEVEE'
r.resolution_percentage=72; r.film_transparent=True
r.image_settings.file_format='PNG'; r.image_settings.color_mode='RGBA'; r.image_settings.color_depth='8'
sc.view_settings.view_transform='Raw'; sc.view_settings.exposure=0; sc.view_settings.gamma=1; sc.view_settings.look='None'
try: sc.eevee.taa_render_samples=1
except: pass
try: r.filter_size=0.0
except: pass
mats=sorted({sl.material.name for o in bpy.data.objects if o.type=='MESH' for sl in o.material_slots if sl.material})
cmap={}
for i,mn in enumerate(mats):
    col=((i*37)%251/255.0,((i*91)%241)/255.0,((i*53)%239)/255.0)
    m=bpy.data.materials.new('ID_'+mn); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    em=nt.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value=(*col,1); em.inputs['Strength'].default_value=1
    o=nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(em.outputs[0],o.inputs['Surface'])
    cmap[mn]=(m,[int(round(c*255)) for c in col])
json.dump({k:v[1] for k,v in cmap.items()},open(OUT+'/matcolors.json','w'))
FW,FH=1191.0,1684.0
for a in IDX['assets']:
    if a['id'] not in mine: continue
    names=set(a['objects'])
    for o in bpy.data.objects:
        if o.type in ('MESH','CURVE','FONT','SURFACE','META'):
            o.hide_render = o.name not in names
    for o in bpy.data.objects:
        if o.name in names and o.type=='MESH':
            for sl in o.material_slots:
                if sl.material and not sl.material.name.startswith('ID_'):
                    nm=sl.material.name; sl.link='OBJECT'; sl.material=cmap[nm][0]
    c2=json.load(open(f'{OUT}/{a["id"]}_crop2.json'))['crop2']
    r.use_border=True; r.use_crop_to_border=True
    r.border_min_x=c2[0]/FW; r.border_max_x=c2[1]/FW; r.border_min_y=1-c2[3]/FH; r.border_max_y=1-c2[2]/FH
    r.filepath=f'{OUT}/{a["id"]}_mat.png'
    bpy.ops.render.render(write_still=True)
print('DONE')
