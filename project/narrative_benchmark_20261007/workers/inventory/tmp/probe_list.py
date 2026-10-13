import bpy, numpy as np, json, sys
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; cam=sc.camera
r=sc.render
print('RES', r.resolution_x, r.resolution_y, r.resolution_percentage, r.engine, sc.display.shading.light, sc.display.shading.color_type, sc.display.render_aa, sc.view_settings.view_transform, sc.view_settings.look, r.dither_intensity, cam.data.type)
print('WORLD', sc.world.color[:] if sc.world else None)
from collections import Counter
print('TYPES', Counter(o.type for o in bpy.data.objects))
def walk(c, d=0):
    print('  '*d+'COLL', c.name, 'hide_render=',c.hide_render, 'n_obj=',len(c.objects))
    for ch in c.children: walk(ch, d+1)
walk(sc.collection)
# view layer exclusion
def walk_lc(lc, d=0):
    print('  '*d+'LC', lc.name, 'exclude=',lc.exclude, 'holdout', lc.holdout, 'indirect', lc.indirect_only)
    for ch in lc.children: walk_lc(ch, d+1)
walk_lc(bpy.context.view_layer.layer_collection)
dg=bpy.context.evaluated_depsgraph_get()
inst=Counter()
for i in dg.object_instances:
    if i.is_instance: inst[(i.parent.name if i.parent else None, i.object.name)]+=1
print('INSTANCES', list(inst.items())[:40], len(inst))
W,H=1191,1684
rows=[]
for o in sorted(bpy.data.objects, key=lambda o:o.name):
    cols=[c.name for c in o.users_collection]
    mods=[m.type for m in o.modifiers]
    if o.type=='MESH':
        ev=o.evaluated_get(dg); me=ev.to_mesh(); n=len(me.vertices)
        if n:
            co=np.empty(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
            M=np.array(o.matrix_world); P=co@M[:3,:3].T+M[:3,3]
            idx=np.linspace(0,n-1,min(n,3000)).astype(int)
            uv=np.array([world_to_camera_view(sc,cam,__import__('mathutils').Vector(P[i])) for i in idx])
            b=[round(uv[:,0].min()*W),round(uv[:,0].max()*W),round((1-uv[:,1].max())*H),round((1-uv[:,1].min())*H)]
        else: b=None
        nf=len(me.polygons); ev.to_mesh_clear()
    else: b=None; nf=None
    print('OBJ', o.name, o.type, cols, 'HR' if o.hide_render else '', 'HV' if o.hide_viewport else '', nf, b, mods, (o.parent.name if o.parent else ''), (o.instance_type if o.instance_type!='NONE' else ''))
