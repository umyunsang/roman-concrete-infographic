import bpy, runpy, json, numpy as np
from mathutils import Vector
inv=runpy.run_path('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/inventory/inventory.py', run_name='inv_mod')
to_pt_np=inv['to_pt_np']
cam=bpy.context.scene.camera
print('CAM', cam.data.type, cam.data.ortho_scale, tuple(round(a,3) for a in cam.rotation_euler), tuple(round(a,3) for a in cam.location))
p=np.array([[0,0,0],[0,0,1],[1,0,0],[0,1,0]],float)
q=to_pt_np(p)
print('vert 1 unit ->', np.linalg.norm(q[1]-q[0]), 'x unit', q[2]-q[0], 'y unit', q[3]-q[0])
for n in ['T_land','L10_sea','L02_tiber','R_via_ostiensis','R_via_appia','R_core_road','T_cypress','T_pine.004','T_pine.022','R_roadgeo_ostiensis_junction_fill','R1_road5_bed','R1_road_landing5']:
    o=bpy.data.objects[n]; bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    zs=[v.z for v in bb]
    print(n, o.type, 'zmin %.3f zmax %.3f'%(min(zs),max(zs)), 'mods', [m.type for m in o.modifiers], 'rot', tuple(round(a,3) for a in o.rotation_euler), 'scale', tuple(round(a,3) for a in o.scale))
