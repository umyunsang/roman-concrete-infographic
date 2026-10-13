import bpy, bmesh, numpy as np
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; cam=sc.camera; O=bpy.data.objects
o=O['R_core_road']; print('mods',[m.type for m in o.modifiers], 'mats',[s.material.name for s in o.material_slots])
bm=bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
mw=o.matrix_world
def pt(p):
    v=world_to_camera_view(sc,cam,mw@p); return (v.x*1191,(1-v.y)*1684)
seen=set(); isl=[]
for f in bm.faces:
    if f.index in seen: continue
    st=[f]; seen.add(f.index); comp=[]
    while st:
        a=st.pop(); comp.append(a)
        for e in a.edges:
            for g in e.link_faces:
                if g.index not in seen: seen.add(g.index); st.append(g)
    c=sum((x.calc_center_median() for x in comp),__import__('mathutils').Vector())/len(comp)
    isl.append((len(comp),pt(c)))
print('islands',len(isl))
nw=[s for s in isl if 295<s[1][0]<545 and 480<s[1][1]<700]
print('NW islands',len(nw),'sizes',sorted(set(s[0] for s in nw))[:20], 'max',max(s[0] for s in nw))
import collections
print(collections.Counter(s[0] for s in nw).most_common(8))
