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
want=[(28,677),(1101,1151),(1106,537),(896,729),(14,535)]
for fs in isl:
    es=set(e for f in fs for e in f.edges); bnd=sum(1 for e in es if len(e.link_faces)==1)
    if (len(fs)==12 and bnd==6) or (len(fs)==18 and bnd==12): continue
    vs=list({v.index:v for f in fs for v in f.verts}.values())
    P=np.array([v.co[:] for v in vs]); c=pt(P.mean(0))
    if not any(abs(c[0]-w[0])<2 and abs(c[1]-w[1])<2 for w in want): continue
    A=np.c_[P[:,0],P[:,1],np.ones(len(P))]; cf,*_=np.linalg.lstsq(A,P[:,2],rcond=None); r=P[:,2]-A@cf
    print('PLATE',len(fs),c,'verts',len(vs),'xy ext',(P.max(0)-P.min(0)).round(2))
    # sort by x and y, print residual grid
    for key in (0,1):
        u=np.round(P[:,key],2); 
        groups=collections.defaultdict(list)
        for ui,ri in zip(u,r): groups[ui].append(ri)
        if len(groups)<=12 or True:
            print('  axis',key,'ngroups',len(groups),' '.join(f'{k:.2f}:{np.mean(v)*1000:+.0f}({len(v)})' for k,v in sorted(groups.items())[:40]))
    for f in fs[:6]:
        print('   face',[ (round(v.co.x,2),round(v.co.y,2),round(float(v.co.z-(cf[0]*v.co.x+cf[1]*v.co.y+cf[2]))*1000)) for v in f.verts])
