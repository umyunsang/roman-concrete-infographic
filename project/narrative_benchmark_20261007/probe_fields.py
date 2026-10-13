import bpy, bmesh, numpy as np, collections
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; cam=sc.camera; O=bpy.data.objects
def pt(p):
    v=world_to_camera_view(sc,cam,p); return (v.x*1191,(1-v.y)*1684)
for name in ('F_centuriatio',):
    o=O[name]; mw=o.matrix_world
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
        P=np.array([(mw@v.co)[:] for x in fs for v in x.verts])
        ext=P.max(0)-P.min(0); c=P.mean(0)
        isl.append((len(fs),ext.round(2).tolist(),pt(Vector(c))))
    print(name,'islands',len(isl))
    cnt=collections.Counter(n for n,_,_ in isl); print(' sizes',cnt.most_common(12))
    for n,e,c in sorted(isl,key=lambda t:-t[0])[:8]: print('  big',n,e,[round(v) for v in c])
    for n,e,c in [t for t in isl if t[0]==6][:6]: print('  6f',e,[round(v) for v in c])
    for n,e,c in [t for t in isl if 8<=t[0]<=30][:8]: print('  mid',n,e,[round(v) for v in c])
print('roads', [(o.name,len(o.data.polygons)) for o in O if o.name.startswith('R_') and o.type=='MESH'])
print('COL group', [(o.name,[c.name for c in o.users_collection]) for o in O if o.type=='MESH' and not o.hide_render and ('20_LANDMARK' in [c.name for c in o.users_collection])])
