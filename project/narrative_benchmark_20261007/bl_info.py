import bpy
sc=bpy.context.scene; sh=sc.display.shading
for a in ['light','studio_light','color_type','show_cavity','cavity_type','cavity_ridge_factor','cavity_valley_factor','curvature_ridge_factor','curvature_valley_factor','show_shadows','shadow_intensity','show_object_outline','object_outline_color','show_specular_highlight']:
    try: print('SH', a, getattr(sh,a) if not hasattr(getattr(sh,a),'__len__') or isinstance(getattr(sh,a),str) else tuple(getattr(sh,a)))
    except Exception as e: print('SH', a, 'ERR', e)
print('VS', sc.view_settings.view_transform, sc.view_settings.look, sc.view_settings.exposure, sc.display.render_aa)
