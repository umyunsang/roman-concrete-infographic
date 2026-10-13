import bpy, json, os
OUT='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/ov_b1/bl/out'
IDX=json.load(open('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/assets_index.json'))
mine=['support_breakwater_block','support_harbor','support_pompeii_site','support_privernum','support_ruin_observers','landmark_pompeii_town','landmark_vesuvius','landmark_lime_kiln','landmark_apennines','landmark_aqueduct']
sc=bpy.context.scene
r=sc.render
try: r.engine='BLENDER_EEVEE'
except TypeError as e:
    print('ENG',e); r.engine='BLENDER_EEVEE_NEXT'
print('engine',r.engine)
r.resolution_percentage=72
r.film_transparent=True
r.image_settings.file_format='PNG'; r.image_settings.color_mode='RGBA'; r.image_settings.color_depth='16'
sc.view_settings.view_transform='Raw'; sc.view_settings.exposure=0; sc.view_settings.gamma=1; sc.view_settings.look='None'
try: sc.eevee.taa_render_samples=4
except: pass
cam=sc.camera
print('CAMMAT',[list(row) for row in cam.matrix_world.to_3x3()])
# normal material
mat=bpy.data.materials.new('NRM_CAM'); mat.use_nodes=True
nt=mat.node_tree; nt.nodes.clear()
geo=nt.nodes.new('ShaderNodeNewGeometry')
vt=nt.nodes.new('ShaderNodeVectorTransform'); vt.vector_type='NORMAL'; vt.convert_from='WORLD'; vt.convert_to='CAMERA'
mul=nt.nodes.new('ShaderNodeVectorMath'); mul.operation='MULTIPLY_ADD'; mul.inputs[1].default_value=(0.5,0.5,0.5); mul.inputs[2].default_value=(0.5,0.5,0.5)
em=nt.nodes.new('ShaderNodeEmission'); em.inputs['Strength'].default_value=1.0
out=nt.nodes.new('ShaderNodeOutputMaterial')
nt.links.new(geo.outputs['Normal'],vt.inputs['Vector']); nt.links.new(vt.outputs['Vector'],mul.inputs[0]); nt.links.new(mul.outputs['Vector'],em.inputs['Color']); nt.links.new(em.outputs['Emission'],out.inputs['Surface'])
FW,FH=1191.0,1684.0
for a in IDX['assets']:
    if a['id'] not in mine: continue
    names=set(a['objects'])
    for o in bpy.data.objects:
        if o.type in ('MESH','CURVE','FONT','SURFACE','META'):
            o.hide_render = o.name not in names
    for o in bpy.data.objects:
        if o.name in names and o.type=='MESH':
            if len(o.material_slots)==0: o.data.materials.append(mat)
            for sl in o.material_slots:
                sl.link='OBJECT'; sl.material=mat
    c2=json.load(open(f'{OUT}/{a["id"]}_crop2.json'))['crop2']
    r.use_border=True; r.use_crop_to_border=True
    r.border_min_x=c2[0]/FW; r.border_max_x=c2[1]/FW; r.border_min_y=1-c2[3]/FH; r.border_max_y=1-c2[2]/FH
    r.filepath=f'{OUT}/{a["id"]}_Ncam.png'
    bpy.ops.render.render(write_still=True)
print('DONE')
