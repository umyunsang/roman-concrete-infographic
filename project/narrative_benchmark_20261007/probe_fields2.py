import bpy, bmesh, numpy as np, collections
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; cam=sc.camera; O=bpy.data.objects
o=O['F_centuriatio']; mw=o.matrix_world
bm=bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
seen=set(); kinds=collections.Counter(); ex=collections.defaultdict(list)
for f in bm.faces:
    if f.index in seen: continue
    st=[f]; seen.add(f.index); fs=[]
    while st:
        a=st.pop(); fs.append(a)
        for e in a.edges:
            for g in e.link_faces:
                if g.index not in seen: seen.add(g.index); st.append(g)
    P=np.array([(mw@v.co)[:] for x in fs for v in x.verts]); e=P.max(0)-P.min(0)
    h=sorted(e[:2]); key=(len(fs))
    ex[key].append((round(h[0],2),round(h[1],2),round(e[2],2)))
for k in sorted(ex):
    a=np.array(ex[k]); print(k,len(a),'minor/major/z p50',np.median(a,0).round(2),'p10',np.percentile(a,10,0).round(2),'p90',np.percentile(a,90,0).round(2))
for o in O:
    if o.type=='MESH' and not o.hide_render and ('field' in o.name.lower() or o.name.startswith(('F_','H_bale','bale','S_hay','R1_road_landing'))):
        print('OBJ',o.name,len(o.data.polygons),[s.material.name for s in o.material_slots])
