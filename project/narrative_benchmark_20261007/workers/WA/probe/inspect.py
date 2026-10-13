import bpy, sys, json, runpy
import numpy as np
W='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work'
sys.path.insert(0, W+'/workers/layout')
from common import Screen, world_verts
S=Screen()
sc=bpy.context.scene
cam=sc.camera
print('CAM', cam.name, cam.data.type, cam.data.ortho_scale, tuple(round(v,3) for v in cam.matrix_world.translation), tuple(round(v,4) for v in cam.matrix_world.to_euler()))
sh=sc.display.shading
print('SHADING', sc.render.engine, sh.light, sh.color_type, sh.studio_light, sh.show_cavity, sh.cavity_type, sh.cavity_ridge_factor, sh.cavity_valley_factor, sh.curvature_ridge_factor, sh.show_object_outline, tuple(sh.object_outline_color), sh.show_specular_highlight, sh.show_shadows, sh.shadow_intensity, sh.use_world_space_lighting, sh.studiolight_rotate_z)
print('LIGHTDIR', tuple(sc.display.light_direction), sc.display.shadow_shift, sc.display.shadow_focus)
print('VIEW', sc.view_settings.view_transform, sc.view_settings.look, sc.view_settings.exposure, sc.view_settings.gamma)
print('RENDER', sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage)
# material users
users={}
for o in bpy.data.objects:
    for s in o.material_slots:
        if s.material: users.setdefault(s.material.name,set()).add(o.name)
names=sorted(o.name for o in bpy.data.objects if o.name.startswith(('H_','S_')))
def hexc(m):
    c=m.diffuse_color
    def l2s(x): return 12.92*x if x<=0.0031308 else 1.055*x**(1/2.4)-0.055
    return '#%02X%02X%02X'%tuple(round(max(0,min(1,l2s(c[i])))*255) for i in range(3))
for n in names:
    o=bpy.data.objects[n]
    cols=[c.name for c in o.users_collection]
    info=dict(type=o.type, parent=o.parent.name if o.parent else None, cols=cols,
      loc=[round(v,4) for v in o.location], rot=[round(np.degrees(v),2) for v in o.rotation_euler], scl=[round(v,4) for v in o.scale],
      dims=[round(v,4) for v in o.dimensions], hide_render=o.hide_render)
    if o.type=='MESH':
        info['nv']=len(o.data.vertices); info['nf']=len(o.data.polygons)
        info['mods']=[(m.type, getattr(m,'width',None)) for m in o.modifiers]
        info['mats']=[(s.material.name, hexc(s.material), sorted(users[s.material.name]-set(names))[:5], len(users[s.material.name]-set(names))) for s in o.material_slots if s.material]
        wv=world_verts(o); P=S.project(wv)
        info['pt_bbox']=[round(P[:,0].min(),2),round(P[:,0].max(),2),round(P[:,1].min(),2),round(P[:,1].max(),2)]
        info['wz']=[round(wv[:,2].min(),4), round(wv[:,2].max(),4)]
        info['data_users']=o.data.users
    print(n, json.dumps(info, ensure_ascii=False))
