import bpy, numpy as np, json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; cam=sc.camera; o=bpy.data.objects['F_centuriatio']; me=o.data; mw=o.matrix_world
V=np.zeros(len(me.vertices)*3); me.vertices.foreach_get('co',V); V=V.reshape(-1,3)
S=np.array([ (lambda v:(v.x*1191,(1-v.y)*1684))(world_to_camera_view(sc,cam,mw@Vector(p))) for p in V])
# grid occupancy at 20pt
occ={}
for x,y in S:
    k=(int(x//40),int(y//40)); occ[k]=occ.get(k,0)+1
rows={}
for (i,j),n in sorted(occ.items(), key=lambda t:(t[0][1],t[0][0])): rows.setdefault(j,[]).append(i*40)
for j in sorted(rows): print('y',j*40, 'x cells', rows[j])
