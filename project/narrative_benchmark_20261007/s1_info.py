import bpy, json, math, runpy, sys
import numpy as np
from mathutils import Vector
INV = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/inventory/inventory.py'
g = runpy.run_path(INV)
to_pt_np = g['to_pt_np']; eval_mesh_arrays = g['eval_mesh_arrays']; render_visible = g['render_visible']
sc = bpy.context.scene; cam = sc.camera
out = {}
out['cam'] = {'type': cam.data.type, 'ortho_scale': cam.data.ortho_scale, 'rot_deg': [math.degrees(a) for a in cam.matrix_world.to_euler()],
              'loc': list(cam.location), 'res': [sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage],
              'engine': sc.render.engine, 'fwd': list((cam.matrix_world.to_3x3() @ Vector((0,0,-1))).normalized())}
# screen scale: pt per world unit horizontally/vertically
p0 = np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1]], float)
uv = to_pt_np(p0)
out['pt_per_unit'] = {'x': float(np.linalg.norm(uv[1]-uv[0])), 'y': float(np.linalg.norm(uv[2]-uv[0])), 'z': float(np.linalg.norm(uv[3]-uv[0])), 'z_vec': (uv[3]-uv[0]).tolist(), 'x_vec': (uv[1]-uv[0]).tolist(), 'y_vec': (uv[2]-uv[0]).tolist()}
dg = bpy.context.evaluated_depsgraph_get()
mine = ['COL_ruined','R3_colosseum_podium','R4_arena_skin','R8_pantheon','B_pons1','B_pons1_parapet0','B_pons1_parapet1','B_pons2','B_pons2_parapet0','B_pons2_parapet1','R4_bridge_west_bed','MS1_core1_to_2','MS2_core2_to_34','MS3_core34_to_5','R1_road_landing1','R_core_road']
objs = {}
for n in mine:
    o = bpy.data.objects[n]
    P, mi, e, nf, tris = eval_mesh_arrays(o, dg)
    zax = o.matrix_world.to_3x3() @ Vector((0,0,1))
    tilt = math.degrees(zax.normalized().angle(Vector((0,0,1))))
    objs[n] = {'nverts': len(P), 'min': P.min(0).tolist(), 'max': P.max(0).tolist(), 'tilt_deg': tilt,
               'loc': list(o.location), 'rot_deg': [math.degrees(a) for a in o.rotation_euler], 'scale': list(o.scale),
               'collections': [c.name for c in o.users_collection], 'parent': o.parent.name if o.parent else None,
               'children': [c.name for c in o.children], 'modifiers': [m.type for m in o.modifiers]}
out['objs'] = objs
out['all'] = sorted([o.name for o in bpy.data.objects if render_visible(o)])
json.dump(out, open(sys.argv[sys.argv.index('--')+1], 'w'), indent=1)
print('DONE')
