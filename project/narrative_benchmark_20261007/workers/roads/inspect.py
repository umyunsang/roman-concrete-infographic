import bpy, bmesh, numpy as np, collections
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; cam=sc.camera; O=bpy.data.objects
print('ENGINE',sc.render.engine, 'light',sc.display.shading.light, 'color_type',sc.display.shading.color_type, 'res',sc.render.resolution_x,sc.render.resolution_y)
print('view transform', sc.view_settings.view_transform, sc.view_settings.look, sc.view_settings.exposure, sc.view_settings.gamma, 'bg', sc.display.shading.background_type, tuple(sc.world.color) if sc.world else None)
def to_pt(p):
    v=world_to_camera_view(sc,cam,p); return (v.x*1191,(1-v.y)*1684)
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
names=['R_core_road','R_via_appia','R_via_ostiensis','R1_road_landing1','R1_road_landing5','B_pons1','B_pons2','R4_bridge_west_bed','R1_road5_bed']
for n in names:
    o=O.get(n)
    if o is None: print('MISSING',n); continue
    mats=[s.material.name if s.material else None for s in o.material_slots]
    mi=collections.Counter(p.material_index for p in o.data.polygons)
    isl=islands(o); sz=collections.Counter(len(i) for i in isl)
    mw=o.matrix_world
    idx=np.linspace(0,len(o.data.vertices)-1,min(3000,len(o.data.vertices))).astype(int)
    P=np.array([to_pt(mw@o.data.vertices[i].co) for i in idx])
    print('OBJ',n,'users',o.data.users,'cols',[c.name for c in o.users_collection],'hide_r',o.hide_render,'polys',len(o.data.polygons),'mats',mats,'matidx',dict(mi),'color',tuple(round(c,3) for c in o.color))
    print('   islands',len(isl),'size hist (top)',sorted(sz.items())[:12],'big',[k for k in sz if k>40][:10], 'screen',P[:,0].min().round(),P[:,0].max().round(),P[:,1].min().round(),P[:,1].max().round())
for m in bpy.data.materials:
    if any(k in m.name.lower() for k in ('road','bridge','pons','stone','milestone','curb','paver','basalt','travert','label','sign')):
        print('MAT',m.name,'users',m.users,'diffuse',tuple(round(c,4) for c in m.diffuse_color))
# objects using road material
rm=bpy.data.materials.get('RC.v12.base_road_foundation')
print('ROADMAT users:', [o.name for o in O if any(s.material==rm for s in o.material_slots)])
# children/bridge related
print('BRIDGE-ish:',[ (o.name,[s.material.name for s in o.material_slots if s.material]) for o in O if any(k in o.name for k in ('pons','bridge','B_','rail','parapet','landing','bed'))])
# milestone color 983821
def srgb(c): return '#%02X%02X%02X'%tuple(round(255*(12.92*x if x<=0.0031308 else 1.055*x**(1/2.4)-0.055)) for x in c[:3])
for m in bpy.data.materials:
    h=srgb(m.diffuse_color)
    if h in ('#983821',) or 'mile' in m.name.lower():
        print('MILEMAT',m.name,h,[o.name for o in O if any(s.material==m for s in o.material_slots)][:30])
print('ALLMATS',[(m.name,srgb(m.diffuse_color)) for m in bpy.data.materials if m.users])
