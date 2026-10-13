import bpy, json, math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene
cam=sc.camera
W,H=1191,1684
def topt(v):
    c=world_to_camera_view(sc,cam,v)
    return (c.x*W,(1-c.y)*H)
out={}
print('camera',cam.name,cam.data.type,cam.data.ortho_scale if cam.data.type=='ORTHO' else cam.data.lens, tuple(round(a,3) for a in cam.matrix_world.to_euler()))
ob=bpy.data.objects['L05_aqua_claudia']
dg=bpy.context.evaluated_depsgraph_get()
oe=ob.evaluated_get(dg); me=oe.to_mesh()
vs=[ob.matrix_world@v.co for v in me.vertices]
import numpy as np
P=np.array([[v.x,v.y,v.z] for v in vs])
print('n verts',len(P),'bbox',P.min(0).round(2),P.max(0).round(2))
xy=P[:,:2]-P[:,:2].mean(0)
u,s,vt=np.linalg.svd(xy,full_matrices=False)
ax=vt[0]; print('axis dir',ax.round(3))
t=xy@ax; n=xy@vt[1]
z=P[:,2]
zmin,zmax=z.min(),z.max(); print('z range',zmin,zmax)
# sample a mid-height slice: vertices with z in mid band
band=(z>zmin+0.3*(zmax-zmin))&(z<zmin+0.5*(zmax-zmin))
tt=np.sort(t[band])
print('slice verts',band.sum())
# histogram of t to find piers
hist,edges=np.histogram(t[band],bins=2000)
occ=hist>0
# runs of occupied bins
runs=[];i=0
while i<len(occ):
    if occ[i]:
        j=i
        while j<len(occ) and occ[j]: j+=1
        runs.append((edges[i],edges[j])); i=j
    else: i+=1
w=[b-a for a,b in runs]; 
print('n runs',len(runs),'median run len',np.median(w))
cent=np.array([(a+b)/2 for a,b in runs])
sp=np.diff(cent); print('median spacing',np.median(sp),'pier width median',np.median(w))
# projected screen length of 1m along axis at center and vertical 1m
c=Vector((*(P[:,:2].mean(0)),zmin))
a1=Vector((ax[0],ax[1],0))
p0=topt(c); p1=topt(c+a1); pz=topt(c+Vector((0,0,1)))
print('screen pt per 1m along axis',(p1[0]-p0[0],p1[1]-p0[1]),'per 1m up',(pz[0]-p0[0],pz[1]-p0[1]))
# view direction in ground plane
vd=cam.matrix_world.to_3x3()@Vector((0,0,-1))
print('view dir',tuple(round(x,3) for x in vd))
ang=math.degrees(math.atan2(vd.y,vd.x)-math.atan2(ax[1],ax[0]))
print('angle between view(xy) and axis',ang)
