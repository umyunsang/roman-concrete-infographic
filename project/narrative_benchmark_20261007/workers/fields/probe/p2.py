import bpy, bmesh, numpy as np, collections
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; cam=sc.camera; O=bpy.data.objects
def pt(p):
    v=world_to_camera_view(sc,cam,p); return (round(v.x*1191),round((1-v.y)*1684))
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
cnt=collections.Counter(len(fs) for fs in isl); print('face-count hist',sorted(cnt.items()))
# per face count, nverts per face hist
for n in sorted(cnt):
    ex=[fs for fs in isl if len(fs)==n][0]
    print('n',n,'face sizes',collections.Counter(len(f.verts) for f in ex))
# print details of one big plate
big=[fs for fs in isl if len(fs)>=30][:2]
for fs in big:
    vs=set(v for f in fs for v in f.verts)
    P=np.array([v.co[:] for v in vs])
    print('PLATE faces',len(fs),'verts',len(vs),'min',P.min(0).round(3),'max',P.max(0).round(3), 'screen', pt(Vector(P.mean(0))))
    for f in fs:
        c=f.calc_center_median(); n=f.normal
        print('  f',f.index,len(f.verts),'c',[round(x,3) for x in c],'n',[round(x,3) for x in n],'area',round(f.calc_area(),3))
