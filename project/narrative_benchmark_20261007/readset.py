import bpy
sc=bpy.context.scene
print('ENGINE',sc.render.engine, sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage, sc.render.film_transparent)
dsp=sc.display
print('light_direction',tuple(dsp.light_direction),'shadow_shift',dsp.shadow_shift,'shadow_focus',dsp.shadow_focus)
sh=dsp.shading
for k in ['light','studio_light','color_type','show_shadows','shadow_intensity','show_cavity','cavity_type','cavity_ridge_factor','cavity_valley_factor','curvature_ridge_factor','curvature_valley_factor','show_object_outline','object_outline_color','show_specular_highlight','studiolight_rotate_z','use_dof','show_xray']:
    try: print(k,getattr(sh,k))
    except Exception as e: print(k,'ERR',e)
cam=sc.camera
print('CAM',cam.name, tuple(cam.matrix_world.to_euler()), tuple(cam.location), cam.data.type, cam.data.ortho_scale)
print('VT',sc.view_settings.view_transform, sc.view_settings.look, sc.view_settings.exposure, sc.view_settings.gamma)
for c in bpy.data.collections: print('COLL',c.name, c.hide_render, len(c.objects))
vl=bpy.context.view_layer
print('VL', [l.name for l in sc.view_layers])
def walk(lc,dep=0):
    print('  '*dep,'LC',lc.name,'exclude',lc.exclude,'holdout',lc.holdout,'indirect',lc.indirect_only)
    for ch in lc.children: walk(ch,dep+1)
walk(vl.layer_collection)
