import bpy, bmesh, numpy as np, collections
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; cam=sc.camera; O=bpy.data.objects
o=O['F_centuriatio']; me=o.data; mw=o.matrix_world
print('modifiers',[ (m.name,m.type) for m in o.modifiers])
print('mw',[list(r) for r in mw])
print('attrs',[(a.name,a.domain,a.data_type) for a in me.attributes])
print('has custom normals', me.has_custom_normals, 'polys',len(me.polygons),'verts',len(me.vertices))
print('smooth count', sum(p.use_smooth for p in me.polygons))
print('uv layers',[u.name for u in me.uv_layers])
sh=sc.display.shading
print('shading', sh.light, sh.color_type, sh.studio_light, sh.show_shadows, sh.show_cavity, getattr(sh,'cavity_type',None), sh.show_object_outline, sh.show_specular_highlight)
print('engine', sc.render.engine, sc.display.light_direction[:], sc.display.shadow_shift, sc.display.shadow_focus, sh.shadow_intensity)
print('cavity', sh.cavity_ridge_factor, sh.cavity_valley_factor, sh.curvature_ridge_factor, sh.curvature_valley_factor)
print('view transform', sc.view_settings.view_transform, sc.view_settings.look, sc.view_settings.exposure, sc.view_settings.gamma, sc.display_settings.display_device)
m=bpy.data.materials['RC.v12.base_field']; print('mat', m.diffuse_color[:], m.roughness, m.metallic, m.use_nodes)
