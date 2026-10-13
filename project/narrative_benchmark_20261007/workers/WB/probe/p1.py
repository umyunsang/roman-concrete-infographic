import bpy, sys, json
import numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts
S = Screen()
O = bpy.data.objects
names = [o.name for o in O if o.name.startswith(('C2_', 'D2_', 'S_lead02', 'S_lead_dot2', 'D2'))]
print('names', names)
for n in sorted(names):
    o = O[n]
    info = dict(type=o.type, parent=o.parent.name if o.parent else None, coll=[c.name for c in o.users_collection],
                loc=[round(x,3) for x in o.location], rot=[round(x,3) for x in o.rotation_euler], scl=[round(x,3) for x in o.scale],
                mats=[s.material.name if s.material else None for s in o.material_slots], data=o.data.name if o.data else None,
                users=o.data.users if o.data else None)
    if o.type=='MESH':
        Wv = world_verts(o); P = S.project(Wv)
        info['nv']=len(o.data.vertices); info['nf']=len(o.data.polygons)
        info['wbox']=[round(float(x),3) for x in (*Wv.min(0), *Wv.max(0))]
        info['ptbox']=[round(float(x),1) for x in (*P.min(0), *P.max(0))]
    print(n, json.dumps(info, ensure_ascii=False))
# who else uses materials
for mn in ['RC.v12.roman_stone','RC.v12.linen','RC.v12.mixture','RC.v12.skin','RC.v12.basin','RC.v12.cloth','RC.v12.toolwood','RC.v12.base_hot_mixing','RC.v12.base_lime_specimen_matrix','RC.v12.base_lime_calcium_crystal','RC.v12.base_line','RC.v12.base_water_process']:
    m = bpy.data.materials.get(mn)
    users = [o.name for o in O if any(s.material==m for s in o.material_slots)] if m else None
    col = None
    if m:
        col = list(m.diffuse_color)
        if m.use_nodes:
            b = next((nd for nd in m.node_tree.nodes if nd.type=='BSDF_PRINCIPLED'), None)
            if b: col = ('bsdf', list(b.inputs['Base Color'].default_value))
    print(mn, 'users', users[:12] if users else users, len(users) if users else 0, col)
sc=bpy.context.scene
print('engine', sc.render.engine, sc.display.shading.light, sc.display.shading.color_type, sc.render.resolution_x, sc.render.resolution_y)
print('cam', sc.camera.name, sc.camera.data.type, sc.camera.data.ortho_scale if sc.camera.data.type=='ORTHO' else sc.camera.data.lens, list(sc.camera.matrix_world.translation), list(sc.camera.rotation_euler))
print('collections', [(c.name, c.hide_render) for c in bpy.data.collections])
