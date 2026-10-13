import bpy, bmesh, numpy as np, collections
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; cam=sc.camera; O=bpy.data.objects
s=sc.display.shading
print('SHADING', {k:getattr(s,k) for k in ['light','studio_light','show_cavity','cavity_type','show_specular_highlight','show_shadows','shadow_intensity','show_object_outline','use_dof','color_type','show_xray']}, 'light_dir', tuple(sc.display.light_direction), 'shadow_shift',sc.display.shadow_shift, 'shadow_focus', sc.display.shadow_focus)
print('CAV', s.cavity_ridge_factor, s.cavity_valley_factor, s.curvature_ridge_factor, s.curvature_valley_factor)
def to_pt(p):
    v=world_to_camera_view(sc,cam,p); return np.array((v.x*1191,(1-v.y)*1684))
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
r=cam.matrix_world.col[0].xyz.normalized()
for n in ['R_core_road','R_via_appia','R_via_ostiensis','R1_road_landing1','R1_road_landing5','B_pons1','B_pons2','B_pons1_parapet0','B_pons2_parapet0','R4_bridge_west_bed','R1_road5_bed']:
    o=O[n]; me=o.data; mw=o.matrix_world
    W=np.array([(mw@v.co)[:] for v in me.vertices])
    isl=islands(o)
    print('==',n,'loc',tuple(round(x,2) for x in o.location),'wpp', round(1/np.linalg.norm(to_pt(mw@me.vertices[0].co+r)-to_pt(mw@me.vertices[0].co)),4))
    for fs in isl:
        if len(fs)==5 and n.startswith('R_'): continue
        vs=sorted({vi for f in fs for vi in me.polygons[f].vertices})
        P=W[vs]; ext=P.max(0)-P.min(0); q=np.array([to_pt(__import__('mathutils').Vector(p)) for p in P])
        nz=[round(me.polygons[f].normal.z,2) for f in fs][:12]
        print('  isl faces',len(fs),'verts',len(vs),'ext xyz',ext.round(3),'screen',q[:,0].min().round(1),q[:,0].max().round(1),q[:,1].min().round(1),q[:,1].max().round(1),'nz',nz)
    # paver extents
    pav=[fs for fs in isl if len(fs)<=40]
    if n.startswith('R_') and pav:
        E=[]
        for fs in pav:
            vs=sorted({vi for f in fs for vi in me.polygons[f].vertices}); P=W[vs]; e=P.max(0)-P.min(0); E.append(max(e[0],e[1]))
        print('  paver max-horiz-extent p0/50/99/100',np.percentile(E,[0,50,99,100]).round(3))
for o in O:
    if o.name.startswith('MS'):
        mw=o.matrix_world; P=np.array([to_pt(mw@v.co) for v in o.data.vertices])
        print('MS',o.name,[s.material.name for s in o.material_slots], collections.Counter(p.material_index for p in o.data.polygons), 'screen',P[:,0].min().round(1),P[:,0].max().round(1),P[:,1].min().round(1),P[:,1].max().round(1), 'cols',[c.name for c in o.users_collection])
