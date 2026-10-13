import bpy, bmesh, json, sys
import numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts
S = Screen()
sc = bpy.context.scene
print('scene props', {k: sc[k] for k in sc.keys() if not k.startswith('_')} if sc.keys() else None)
for n in ['R_core_road','R_via_ostiensis','R_via_appia','R1_road_landing1','R1_road_landing5','T_land','R4_bridge_west_bed','R1_road5_bed','MS3_core34_to_5','R3_colosseum_podium','COL_ruined','F_centuriatio']:
    o = bpy.data.objects.get(n)
    if o is None: print(n, 'MISSING'); continue
    me = o.data
    W = world_verts(o)
    P = S.project(W) if len(W) else np.zeros((0,2))
    print(n, o.type, 'verts', len(me.vertices), 'faces', len(me.polygons), 'mats', [m.name if m else None for m in me.materials],
          'mods', [m.type for m in o.modifiers], 'users', me.users, 'loc', tuple(round(v,3) for v in o.location), 'rot', tuple(round(v,3) for v in o.rotation_euler), 'scale', tuple(round(v,3) for v in o.scale),
          'parent', o.parent.name if o.parent else None, 'coll', [c.name for c in o.users_collection],
          'scr', [round(float(v),1) for v in (P[:,0].min(),P[:,0].max(),P[:,1].min(),P[:,1].max())] if len(P) else None,
          'zrange', [round(float(W[:,2].min()),3), round(float(W[:,2].max()),3)] if len(W) else None)
print('camera', sc.camera.name, sc.camera.data.type, sc.render.engine, sc.render.resolution_x, sc.render.resolution_y)
