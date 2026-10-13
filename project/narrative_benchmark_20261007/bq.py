import bpy, json, mathutils
sc=bpy.context.scene
cam=sc.camera
print('CAM', cam.name, cam.data.type, cam.data.ortho_scale if cam.data.type=='ORTHO' else cam.data.lens, tuple(round(v,4) for v in cam.matrix_world.translation), tuple(round(v,4) for v in cam.matrix_world.to_euler()))
print('ENGINE', sc.render.engine)
sh=sc.display.shading
try:
    print('SHADING light', sh.light, 'color_type', sh.color_type, 'cavity', sh.show_cavity, 'shadow', sh.show_shadows, 'specular', sh.show_specular_highlight, 'studio', sh.studio_light)
except Exception as e: print('shading err', e)
cdir = cam.matrix_world.to_quaternion() @ mathutils.Vector((0,0,-1))
print('CAMDIR', tuple(round(v,4) for v in cdir))
names=[o.name for o in bpy.data.objects if o.name.startswith(('S_core','S_lead','S_sect','S_pin_harbor','S_pin_pompeii'))]
for n in sorted(names):
    o=bpy.data.objects[n]; me=o.data
    mw=o.matrix_world
    vs=[mw @ v.co for v in me.vertices]
    depths=[ (v - cam.matrix_world.translation).dot(cdir) for v in vs]
    nrm=[]
    for p in me.polygons:
        nw=(mw.to_3x3() @ p.normal).normalized()
        nrm.append(round(nw.dot(cdir),4))
    sm=[p.use_smooth for p in me.polygons]
    print(n, 'loc',tuple(round(x,4) for x in mw.translation), 'rot', tuple(round(x,4) for x in o.rotation_euler), 'scale', tuple(round(x,4) for x in o.scale),
          'depth[min,max]=%.5f,%.5f'%(min(depths),max(depths)), 'nfaces',len(me.polygons),'n.cdir set',sorted(set(nrm)), 'smooth', set(sm), 'hide_render', o.hide_render)
