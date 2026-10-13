import bpy, sys, math, json
import numpy as np
from mathutils import Vector
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen
S=Screen()
coll=bpy.data.collections['81_NOSHADOW']
dirs={'cam_up':(0.4,-0.4,0.82),'a1':(0.3,-0.5,0.81),'a2':(0.5,-0.3,0.81),'a3':(0.5,-0.5,0.7),'a4':(0.35,-0.35,0.87),'a5':(0.2,-0.55,0.81),'a6':(0.55,-0.45,0.7),'a7':(0.45,-0.55,0.7),'a8':(0.6,-0.6,0.53),'a9':(0.3,-0.6,0.74)}
mats=['RC.v12.base_lime_calcium_crystal']
res={}
x0,y0,z0=30.0,-45.0,8.0
objs=[]
for j,mn in enumerate(mats):
    for i,(k,d) in enumerate(dirs.items()):
        me=bpy.data.meshes.new(f'T_{j}_{i}')
        cx,cy,cz=x0+i*2.2,y0+i*2.2,z0+j*3.0
        # quad facing camera-ish (normal (1,-1,0)) but custom normals override
        a=Vector((cx,cy,cz)); u=Vector((0.6,0.6,0)); v=Vector((0,0,0.8))
        me.from_pydata([a-u-v,a+u-v,a+u+v,a-u+v],[],[[0,1,2,3]])
        me.update()
        dd=Vector(d).normalized()
        me.normals_split_custom_set([tuple(dd)]*len(me.loops))
        o=bpy.data.objects.new(f'T_{j}_{i}',me); coll.objects.link(o); me.materials.append(bpy.data.materials[mn]); objs.append((o,k,mn,S.to_pt(a)))
H=runpy=None
import runpy
Hh=runpy.run_path('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/scripts/integrate_assets.py', run_name='h')
out='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/WC/renders/normals2'
Hh['render_two_pass'](out+'.png')
json.dump([(k,mn,[float(p[0]),float(p[1])]) for o,k,mn,p in objs],open(out+'.json','w'))
