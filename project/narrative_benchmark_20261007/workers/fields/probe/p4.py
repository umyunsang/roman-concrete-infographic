import bpy, bmesh, numpy as np, collections
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; cam=sc.camera; O=bpy.data.objects
def pt(p):
    v=world_to_camera_view(sc,cam,Vector(p)); return (round(v.x*1191),round((1-v.y)*1684))
o=O['F_centuriatio']; me=o.data
bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
seen=set(); isl=[]
for f in bm.faces:
    if f.index in seen: continue
    st=[f]; seen.add(f.index); fs=[]
    while st:
        a=st.pop(); fs.append(a)
        for e in a.edges:
            for g in e.link_faces:
                if g.index not in seen: seen.add(g.index); st.append(g)
    isl.append(fs)
plates=[];props=[]
for fs in isl:
    es=set(e for f in fs for e in f.edges); bnd=sum(1 for e in es if len(e.link_faces)==1)
    closedish = (len(fs)==12 and bnd==6) or (len(fs)==18 and bnd==12)
    if closedish: props.append(fs)
    else: plates.append(fs)
print('plates',len(plates),'props',len(props))
amp=[];stats=[]
for fs in plates:
    vs=list({v.index:v for f in fs for v in f.verts}.values())
    P=np.array([v.co[:] for v in vs])
    A=np.c_[P[:,0],P[:,1],np.ones(len(P))]; c,*_=np.linalg.lstsq(A,P[:,2],rcond=None)
    r=P[:,2]-A@c
    N=np.array([f.normal[:] for f in fs]); N*=np.sign(N[:,2:3]+1e-9)
    nm=N.mean(0); D=N-nm; D[:,2]=0
    # principal dir of deviations
    if len(fs)>1:
        u,s,vt=np.linalg.svd(D[:,:2],full_matrices=False); d=vt[0]; proj=D[:,:2]@d
    else: proj=np.zeros(1); d=np.zeros(2)
    stats.append((len(fs),round(float(r.max()-r.min()),3),round(float(np.abs(proj).mean()),3),round(float(np.abs(proj).min()),3),pt(P.mean(0)),d.round(2).tolist()))
stats.sort(key=lambda t:t[2])
for s in stats[:30]: print('lowtilt',s)
print('...')
for s in stats[-8:]: print('hightilt',s)
h=np.array([s[2] for s in stats]); print('tilt hist',np.histogram(h,bins=[0,0.02,0.05,0.08,0.1,0.12,0.15,0.2,0.3])[0])
