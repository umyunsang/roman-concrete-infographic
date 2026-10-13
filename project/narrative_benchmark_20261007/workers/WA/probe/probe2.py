import bpy, sys
import numpy as np
from mathutils import Vector
W='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work'
sys.path.insert(0, W+'/workers/layout')
from common import Screen, world_verts
S=Screen()
cam=S.cam; fwd=-(cam.matrix_world.to_3x3() @ Vector((0,0,1))).normalized()
print('cam fwd', fwd, 'shift', cam.data.shift_x, cam.data.shift_y, 'lens', cam.data.lens, cam.data.sensor_width, cam.data.sensor_fit)
def depth(wv): return (wv - np.array(S.origin)) @ np.array(fwd)
o=bpy.data.objects['H_gate_body']; me=o.data
print('gate body verts', len(me.vertices), 'faces', len(me.polygons))
from collections import Counter
c=Counter()
for p in me.polygons:
    n=tuple(round(v,2) for v in p.normal); c[(n,len(p.vertices))]+=1
print(c.most_common(20))
big=[(p.index,len(p.vertices),round(p.area,3),tuple(round(v,2) for v in p.normal)) for p in me.polygons if p.area>0.5]
print('big faces', big)
co=np.array([v.co[:] for v in me.vertices]); print('local bbox', co.min(0), co.max(0))
for n in ['H_gate_keystone','S_pin_harbor','S_pin_harbor_dot','S_pin_pompeii_dot','S_lead03','S_lead04','S_lead05','S_lead09','S_sect_dot0','S_sect0','S_sect0_edge','S_sect_brick1227','S_core1_underline','S_core1_badge']:
    o=bpy.data.objects[n]; wv=world_verts(o); P=S.project(wv); d=depth(wv)
    print(n, 'nv',len(wv),'depth',round(d.min(),4),round(d.max(),4))
    if len(wv)<=40:
        for i,(p,dd) in enumerate(zip(P,d)): print('   ',i,np.round(p,2),round(dd,4))
    if n=='S_pin_harbor':
        for f in o.data.polygons: print('   f',f.index,list(f.vertices))
