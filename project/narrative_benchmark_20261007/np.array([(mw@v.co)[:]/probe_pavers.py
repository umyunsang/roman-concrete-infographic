import bpy, bmesh, numpy as np, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; cam=sc.camera; O=bpy.data.objects
def to_pt(p):
    v=world_to_camera_view(sc,cam,p); return np.array((v.x*1191,(1-v.y)*1684))
T=O['T_land']; dg=bpy.context.evaluated_depsgraph_get(); ev=T.evaluated_get(dg); me=ev.to_mesh()
TB=BVHTree.FromPolygons([T.matrix_world@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons])
def tz(x,y):
    h=TB.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))[0]; return h.z if h else 0
o=O['R_core_road']; mw=o.matrix_world
bm=bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
seen=set(); isl=[]
for f in bm.faces:
    if f.index in seen: continue
    st=[f]; seen.add(f.index); fs=[]
    while st:
        a=st.pop(); fs.append(a)
        for e in a.edges:
            for g in e.link_faces:
                if g.index not in seen: seen.add(g.index); st.append(g)
    vs=sorted({v.index for x in fs for v in x.verts}); isl.append((fs,vs))
W=np.array([(mw@v.co)[:] for v in o.data.vertices])
ref=[(fs,vs) for fs,vs in isl if len(fs)<=6 and (lambda q: 330<q[0]<420 and 600<q[1]<660)(to_pt(Vector(W[vs].mean(0))))]
C=np.array([W[vs,:2].mean(0) for fs,vs in ref])
c0=C.mean(0); U,S,Vt=np.linalg.svd(C-c0); t=Vt[0]; n=np.array([-t[1],t[0]])
print('ref pavers',len(ref),'dir',t)
L=[];Wd=[];Hh=[];top=[]
for fs,vs in ref:
    P=W[vs]; s=(P[:,:2]-c0)@t; l=(P[:,:2]-c0)@n
    L.append(s.max()-s.min()); Wd.append(l.max()-l.min())
    g=tz(*P[:,:2].mean(0)); Hh.append(P[:,2].max()-g); top.append(P[:,2].max()-P[:,2].min())
print('paver len p10/50/90',np.percentile(L,[10,50,90]).round(3),'wid',np.percentile(Wd,[10,50,90]).round(3),'top above ground',np.percentile(Hh,[10,50,90]).round(3),'box h',np.percentile(top,[10,50,90]).round(3))
s=(C-c0)@t; l=(C-c0)@n
print('lat range',l.min().round(2),l.max().round(2))
# rows: sort by s, show lateral lists for a few rows
order=np.argsort(s)
print('s sorted first 40', np.round(s[order][:40],2))
print('l of those', np.round(l[order][:40],2))
# bed islands
for fs,vs in isl:
    if len(fs)>40:
        P=W[vs]; q=np.array([to_pt(Vector(p)) for p in P])
        g=np.array([tz(*p[:2]) for p in P])
        print('BED',len(fs),'screen',q[:,0].min().round(),q[:,0].max().round(),q[:,1].min().round(),q[:,1].max().round(),'h above ground p10/50/90',np.percentile(P[:,2]-g,[10,50,90]).round(3))
