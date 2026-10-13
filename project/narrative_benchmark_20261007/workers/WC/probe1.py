import bpy, sys, json
import numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts
S = Screen()
pats = ['NB_lime_clast_specimen','NB_core4_sequence_','R8_','D1_','R1_','R3_','NB_modern_building','S_core']
out = []
for o in sorted(bpy.data.objects, key=lambda o:o.name):
    if not any(o.name.startswith(p) for p in pats): continue
    d = {'name':o.name,'type':o.type,'coll':[c.name for c in o.users_collection],'hide_r':o.hide_render,
         'loc':[round(v,4) for v in o.location],'rot':[round(v,4) for v in o.rotation_euler],'scale':[round(v,4) for v in o.scale],
         'parent':o.parent.name if o.parent else None}
    if o.type=='MESH':
        d['nv']=len(o.data.vertices); d['nf']=len(o.data.polygons); d['mesh']=o.data.name; d['mesh_users']=o.data.users
        d['mats']=[(s.material.name if s.material else None) for s in o.material_slots]
        d['mods']=[(m.type,m.name) for m in o.modifiers]
        Wv=world_verts(o)
        if len(Wv):
            P=S.project(Wv)
            d['wmin']=[round(v,3) for v in Wv.min(0)]; d['wmax']=[round(v,3) for v in Wv.max(0)]
            d['pt']=[round(P[:,0].min(),1),round(P[:,0].max(),1),round(P[:,1].min(),1),round(P[:,1].max(),1)]
    out.append(d)
for d in out: print(json.dumps(d, ensure_ascii=False))
print('MATERIALS')
mats=set()
for d in out:
    for m in d.get('mats',[]): mats.add(m)
for mn in sorted(m for m in mats if m):
    m=bpy.data.materials[mn]
    users=[o.name for o in bpy.data.objects if o.type=='MESH' and any(s.material==m for s in o.material_slots)]
    bsdf=None
    if m.use_nodes:
        bsdf=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    col = list(bsdf.inputs['Base Color'].default_value) if bsdf else None
    print(mn, 'diffuse', [round(v,4) for v in m.diffuse_color], 'bsdf', col and [round(v,4) for v in col], 'nusers', len(users), users[:12])
sc=bpy.context.scene
print('engine', sc.render.engine, 'light', sc.display.shading.light, 'color_type', sc.display.shading.color_type, 'vt', sc.view_settings.view_transform, sc.view_settings.look, sc.view_settings.exposure, sc.view_settings.gamma)
print('studio', sc.display.shading.studio_light, 'cavity', sc.display.shading.show_cavity, 'shadow', sc.display.shading.show_shadows, sc.display.shadow_shift, sc.display.light_direction[:])
print('res', sc.render.resolution_x, sc.render.resolution_y, 'cam', sc.camera.name, sc.camera.data.type)
