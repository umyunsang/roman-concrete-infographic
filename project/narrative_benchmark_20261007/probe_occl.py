import bpy, numpy as np, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; cam=sc.camera; O=bpy.data.objects
origin=cam.matrix_world.translation
def to_pt(p):
    v=world_to_camera_view(sc,cam,p); return (v.x*1191,(1-v.y)*1684)
dg=bpy.context.evaluated_depsgraph_get()
def bvh(names):
    V,F=[],[]
    for n in names:
        o=O[n]; ev=o.evaluated_get(dg); me=ev.to_mesh(); mw=o.matrix_world; b=len(V)
        V+=[mw@v.co for v in me.vertices]; F+=[[b+i for i in p.vertices] for p in me.polygons]; ev.to_mesh_clear()
    return BVHTree.FromPolygons(V,F)
occ={'COL':bvh(['COL_ruined']),'POD':bvh(['R3_colosseum_podium'])}
road=O['R_core_road']; mw=road.matrix_world
res={'COL':[],'POD':[]}
for v in road.data.vertices:
    p=mw@v.co; d=(p-origin); L=d.length; d.normalize()
    for k,b in occ.items():
        h=b.ray_cast(origin,d,L-0.05)
        if h[0] is not None: res[k].append(to_pt(p))
for k,P in res.items():
    P=np.array(P); print(k,'occluded verts',len(P))
    if len(P):
        # cluster by x bins
        for x0 in range(200,1000,25):
            s=(P[:,0]>=x0)&(P[:,0]<x0+25)
            if s.sum(): print('  x%4d-%4d n=%4d y %.0f-%.0f'%(x0,x0+25,s.sum(),P[s,1].min(),P[s,1].max()))
# road vertices in screen near NW (for path design): print centerline samples between x 300-560, y 480-700
P=np.array([to_pt(mw@v.co) for v in road.data.vertices])
s=(P[:,0]>300)&(P[:,0]<560)&(P[:,1]>480)&(P[:,1]<700)
print('NW road verts',s.sum())
for x0 in range(300,560,20):
    t=s&(P[:,0]>=x0)&(P[:,0]<x0+20)
    if t.sum(): print('  NW x%d y %.0f-%.0f'%(x0,P[t,1].min(),P[t,1].max()))
s=(P[:,0]>330)&(P[:,0]<800)&(P[:,1]>950)&(P[:,1]<1040)
for x0 in range(330,800,30):
    t=s&(P[:,0]>=x0)&(P[:,0]<x0+30)
    if t.sum(): print('  S x%d y %.0f-%.0f'%(x0,P[t,1].min(),P[t,1].max()))
# podium outer ring screen y at bottom
pod=O['R3_colosseum_podium']; pm=pod.matrix_world; n=len(pod.data.vertices); print('podium verts',n)
Q=np.array([to_pt(pm@v.co) for v in pod.data.vertices])
zs=np.array([(pm@v.co).z for v in pod.data.vertices])
print('order check z of first 9', [round(z,2) for z in zs[:9]])
for x0 in range(330,850,30):
    t=(Q[:,0]>=x0)&(Q[:,0]<x0+30)
    if t.sum(): print('  POD x%d ymax %.0f'%(x0,Q[t,1].max()))
