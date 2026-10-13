import bpy, sys, json
import numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts
S = Screen()
O = bpy.data.objects
for o in O:
    if o.name.startswith('MS') or 'marker' in o.name or o.name.startswith('shape_core') or (o.parent and o.parent.name.startswith('MS')):
        W = world_verts(o) if o.type == 'MESH' else np.array([o.matrix_world.translation[:]])
        P = S.project(W) if len(W) else np.zeros((0,2))
        print(o.name, o.type, 'parent', o.parent.name if o.parent else None, 'colls', [c.name for c in o.users_collection],
              'loc', [round(v,3) for v in o.location], 'rot', [round(v,4) for v in o.rotation_euler], 'scale', [round(v,3) for v in o.scale],
              'nv', len(W), 'mesh', o.data.name if o.type=='MESH' else None, 'users', o.data.users if o.data else None,
              'mats', [s.material.name if s.material else None for s in o.material_slots],
              'wbox', W.min(0).round(3).tolist() if len(W) else None, W.max(0).round(3).tolist() if len(W) else None,
              'sbox', [round(float(P[:,0].min()),1), round(float(P[:,0].max()),1), round(float(P[:,1].min()),1), round(float(P[:,1].max()),1)] if len(P) else None,
              'hide_render', o.hide_render, 'children', [c.name for c in o.children])
print('scene props', list(bpy.context.scene.keys()))
for k in bpy.context.scene.keys():
    print(k, str(bpy.context.scene[k])[:300])
