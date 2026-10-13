import bpy, numpy as np, math
from mathutils import Vector
from mathutils.kdtree import KDTree
O=bpy.data.objects
T=O['T_land']; mw=T.matrix_world
V=np.array([(mw@v.co)[:] for v in T.data.vertices])
c=np.array((-1.796,0.300))
d=np.linalg.norm(V[:,:2]-c,axis=1)
pit=(d<30)&(np.abs(V[:,2]+1)<1e-3)
riv=(d<45)&(V[:,2]<-1.001)
print('pit',pit.sum(),'river-ish',riv.sum(),'river min r',d[riv].min() if riv.sum() else None)
kd=KDTree(int(pit.sum()))
for i,p in enumerate(V[pit]): kd.insert(Vector((p[0],p[1],0)),i)
kd.balance()
near=d<40
dp=np.full(len(V),1e9)
for i in np.nonzero(near)[0]: dp[i]=kd.find(Vector((V[i,0],V[i,1],0)))[2]
for a,b in [(0.001,0.8),(0.8,1.5),(1.5,2.5),(2.5,3.5),(3.5,4.5),(4.5,5.5),(5.5,6.5),(6.5,8)]:
    s=near&~pit&(dp>=a)&(dp<b)
    print('ring %.1f-%.1f n=%d zmin %.5f zmax %.5f  n_nonflat %d'%(a,b,s.sum(),V[s,2].min(),V[s,2].max(),(np.abs(V[s,2])>1e-4).sum()))
s=near&~pit&(dp<0.8); print('pit-edge non-pit z values', np.unique(V[s,2].round(3))[:20])
# other ground-level objects within the band region (dp<6) : count verts of visible meshes (excluding COL group) lying over band
band=lambda P: np.array([kd.find(Vector((x,y,0)))[2] for x,y in P])
for o in O:
    if o.type!='MESH' or o.hide_render or o.name in ('T_land','COL_ruined','R3_colosseum_podium','R4_arena_skin'): continue
    if any(cc.hide_render for cc in o.users_collection): continue
    m_=o.matrix_world; n=len(o.data.vertices); step=max(1,n//4000)
    P=np.array([(m_@o.data.vertices[i].co)[:2] for i in range(0,n,step)])
    if np.min(np.linalg.norm(P-c,axis=1))>40: continue
    bd=band(P)
    if (bd<6).sum(): print('OBJ over band',o.name,'n',(bd<6).sum(),'min dist to pit',bd.min().round(2))
