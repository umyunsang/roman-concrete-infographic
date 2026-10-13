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
rows=[]
for fs in isl:
    es=set(e for f in fs for e in f.edges); bnd=sum(1 for e in es if len(e.link_faces)==1)
    N=np.array([f.normal[:] for f in fs]); 
    N=N*np.sign(N[:,2:3]+1e-9)  # orient up
    P=np.array([v.co[:] for f in fs for v in f.verts]); ext=P.max(0)-P.min(0)
    nm=N.mean(0); nm/=np.linalg.norm(nm)
    dev=N-nm; spread=np.linalg.norm(dev,axis=1).max()
    rows.append((len(fs),bnd,ext,spread,pt(P.mean(0)),N[:,2].min()))
by=collections.defaultdict(list)
for r in rows: by[r[0]].append(r)
for n in sorted(by):
    R=by[n]; b=collections.Counter(r[1] for r in R); sp=np.array([r[3] for r in R]); nz=np.array([r[5] for r in R])
    E=np.array([r[2] for r in R])
    print(n,len(R),'bnd',dict(b),'normal spread p10/50/90',np.percentile(sp,[10,50,90]).round(3),'min nz',np.percentile(nz,[10,50,90]).round(2),'ext med',np.median(E,0).round(2))
# stakes/bales geometry
for n in (12,18):
    fs=[x for x in isl if len(x)==n][0]
    for f in fs: print(n,'face',len(f.verts),[round(x,2) for x in f.normal],[round(x,3) for x in f.calc_center_median()])
