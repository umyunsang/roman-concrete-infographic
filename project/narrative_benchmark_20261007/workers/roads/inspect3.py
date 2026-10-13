import bpy, bmesh, numpy as np, collections
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; cam=sc.camera; O=bpy.data.objects
def to_pt(p):
    v=world_to_camera_view(sc,cam,p); return np.array((v.x*1191,(1-v.y)*1684))
dg=bpy.context.evaluated_depsgraph_get()
T=O['T_land']; ev=T.evaluated_get(dg); me=ev.to_mesh()
TB=BVHTree.FromPolygons([T.matrix_world@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons]); ev.to_mesh_clear()
def tz(x,y):
    h=TB.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))[0]; return h.z if h else 0
def islands(o):
    bm=bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
    seen=set(); out=[]
    for f in bm.faces:
        if f.index in seen: continue
        st=[f]; seen.add(f.index); fs=[]
        while st:
            a=st.pop(); fs.append(a.index)
            for e in a.edges:
                for g in e.link_faces:
                    if g.index not in seen: seen.add(g.index); st.append(g)
        out.append(fs)
    bm.free(); return out
for n in ['R_core_road','R_via_appia','R_via_ostiensis','R1_road_landing1','R1_road_landing5','B_pons1','B_pons2','R4_bridge_west_bed','R1_road5_bed','B_pons1_parapet0']:
    o=O[n]; print('SLOTS',n,[(s.link, s.material.name if s.material else None) for s in o.material_slots], 'mods',[m.type for m in o.modifiers], 'parent', o.parent.name if o.parent else None)
for n in ['R_core_road','R_via_appia','R_via_ostiensis']:
    o=O[n]; me=o.data; mw=o.matrix_world; W=np.array([(mw@v.co)[:] for v in me.vertices])
    H=[]; odd=[]
    for fs in islands(o):
        vs=sorted({vi for f in fs for vi in me.polygons[f].vertices}); P=W[vs]
        c=P.mean(0); g=tz(c[0],c[1]); top=P[:,2].max()-g
        e=P.max(0)-P.min(0); E=max(e[0],e[1])
        if len(fs)<40:
            H.append(top)
            if top>0.112 or E>0.7: odd.append((len(fs),round(float(E),2),round(float(top),3),to_pt(Vector(c)).round(1).tolist()))
        else:
            # curb top height: sample upward faces
            ups=[f for f in fs if (mw.to_3x3()@me.polygons[f].normal).z>0.7]
            ht=[ (mw@me.polygons[f].center).z - tz(*(mw@me.polygons[f].center)[:2]) for f in ups[:60]]
            print('  CURB',n,len(fs),'top above ground p10/50/90',np.percentile(ht,[10,50,90]).round(3) if ht else None)
    H=np.array(H); print(n,'small islands',len(H),'top above ground pct 1/10/50/90/99',np.percentile(H,[1,10,50,90,99]).round(3))
    print('  hist',np.histogram(H,bins=[-1,0.0,0.05,0.07,0.08,0.09,0.1,0.11,0.12,0.14,0.2,1,5])[0].tolist())
    for x in odd: print('  ODD',x)
cnt=0; objs=0
for o in O:
    if o.type=='MESH' and not o.hide_render and o.visible_get(): cnt+=len(o.data.polygons); objs+=1
print('VISIBLE MESH objs',objs,'polys',cnt)
