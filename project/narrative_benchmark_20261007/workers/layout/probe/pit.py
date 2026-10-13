import bpy, numpy as np, math
from mathutils import Vector
O=bpy.data.objects
T=O['T_land']; print('T_land users',T.data.users,'mods',[m.type for m in T.modifiers],'shape keys',T.data.shape_keys, 'mw identity', T.matrix_world==T.matrix_world.Identity(4) if hasattr(T.matrix_world,'Identity') else T.matrix_world)
print('uv layers',[u.name for u in T.data.uv_layers],'color attrs',[a.name for a in T.data.color_attributes],'attrs',[a.name for a in T.data.attributes])
mw=T.matrix_world
V=np.array([(mw@v.co)[:] for v in T.data.vertices])
c=np.array((-1.796,0.300))
d=np.linalg.norm(V[:,:2]-c,axis=1)
near=d<40
pit=near&(V[:,2]<-0.005)
print('pit verts',pit.sum(),'x',V[pit,0].min(),V[pit,0].max(),'y',V[pit,1].min(),V[pit,1].max())
zs=V[pit,2]; print('pit z hist',np.histogram(zs,bins=[-1.5,-1.001,-0.999,-0.9,-0.5,-0.1,-0.005])[0])
# spacing
E=np.array([[e.vertices[0],e.vertices[1]] for e in T.data.edges])
L=np.linalg.norm(V[E[:,0],:2]-V[E[:,1],:2],axis=1)
m=near[E[:,0]]
print('edge len near',np.percentile(L[m],[5,50,95]))
# distance of near verts to pit; flatness in ring
from mathutils.kdtree import KDTree
kd=KDTree(int(pit.sum()))
for i,p in enumerate(V[pit]): kd.insert(Vector(p),i)
kd.balance()
dp=np.array([kd.find(Vector((x,y,-1)))[2] if n else 1e9 for (x,y,z),n in zip(V,near)])
for a,b in [(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,8),(8,10)]:
    s=near&~pit&(dp>=a)&(dp<b)
    if s.sum(): print('ring %d-%d n=%d zmin %.4f zmax %.4f'%(a,b,s.sum(),V[s,2].min(),V[s,2].max()))
# podium inner ring polygon vs pit
pod=O['R3_colosseum_podium']; pm=pod.matrix_world; PV=np.array([(pm@v.co)[:] for v in pod.data.vertices]); N=len(PV)//3
inner=PV[0::3,:2]; outer=PV[1::3,:2]; lip=PV[2::3,:2]
def inside(poly,P):
    x,y=P[:,0],P[:,1]; res=np.zeros(len(P),bool); n=len(poly)
    for i in range(n):
        x1,y1=poly[i]; x2,y2=poly[(i+1)%n]
        cond=((y1>y)!=(y2>y)) & (x < (x2-x1)*(y-y1)/(y2-y1+1e-12)+x1)
        res^=cond
    return res
print('pit verts inside podium inner ring',inside(inner,V[pit,:2]).sum(),'/',pit.sum())
print('pit verts inside podium lip ring',inside(lip,V[pit,:2]).sum())
# radius stats
ang=np.arctan2(inner[:,1]-c[1],inner[:,0]-c[0])
print('inner r',np.percentile(np.linalg.norm(inner-c,axis=1),[0,50,100]),'outer r',np.percentile(np.linalg.norm(outer-c,axis=1),[0,50,100]),'lip r',np.percentile(np.linalg.norm(lip-c,axis=1),[0,50,100]))
pr=np.linalg.norm(V[pit,:2]-c,axis=1); print('pit r max',pr.max())
# per-angle: pit max radius vs inner radius
pa=np.arctan2(V[pit,1]-c[1],V[pit,0]-c[0])
for a0 in np.linspace(-math.pi,math.pi,13)[:-1]:
    s=(pa>=a0)&(pa<a0+math.pi/6); t=(ang>=a0)&(ang<a0+math.pi/6)
    print('ang %.0f pit rmax %.2f inner rmin %.2f lip rmin %.2f'%(math.degrees(a0),pr[s].max() if s.sum() else -1,np.linalg.norm(inner[t]-c,axis=1).min(),np.linalg.norm(lip[t]-c,axis=1).min()))
# COL lowest parts vs terrain zero
col=O['COL_ruined']; cm=col.matrix_world; CV=np.array([(cm@v.co)[:] for v in col.data.vertices])
print('COL verts below z<-0.01:',(CV[:,2]<-0.01).sum(),'of',len(CV))
s=CV[:,2]<-0.01; print('their r max',np.linalg.norm(CV[s,:2]-c,axis=1).max())
# F_centuriatio islands inside podium lip ring?
F=O['F_centuriatio']; fm=F.matrix_world; FV=np.array([(fm@v.co)[:] for v in F.data.vertices])
print('field verts inside lip ring',inside(lip,FV[:,:2]).sum())
for n in ['R_core_road','R_via_appia','R_via_ostiensis','MS3_core34_to_5','MS2_core2_to_34','T_cypress']:
    o=O[n]; m_=o.matrix_world; RV=np.array([(m_@v.co)[:] for v in o.data.vertices]); print(n,'verts inside lip ring',inside(lip,RV[:,:2]).sum())
