import bpy, sys, json, hashlib
import numpy as np
out = sys.argv[sys.argv.index('--') + 1:][0]
names = ['R_core_road','R_via_appia','R_via_ostiensis','R1_road_landing1','R1_road_landing5','R4_bridge_west_bed','R1_road5_bed',
         'B_pons1','B_pons2','B_pons1_parapet0','B_pons1_parapet1','B_pons2_parapet0','B_pons2_parapet1','H_mold_plank0']
F = {'objects': {}, 'road_materials': {}, 'n_materials': len(bpy.data.materials)}
for n in names:
    o = bpy.data.objects[n]; me = o.data; a = np.zeros(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', a)
    co = np.zeros(len(me.vertices) * 3, np.float32); me.vertices.foreach_get('co', co)
    F['objects'][n] = {'slots': [s.material.name if s.material else None for s in o.material_slots], 'polys': len(me.polygons),
                       'matidx_sha': hashlib.sha1(a.tobytes()).hexdigest()[:12], 'n_idx1': int((a == 1).sum()),
                       'geom_sha': hashlib.sha1(co.tobytes()).hexdigest()[:12], 'mesh_users': me.users}
for m in bpy.data.materials:
    if m.name.startswith('RC.road') or m.name == 'RC.v12.base_road_foundation':
        F['road_materials'][m.name] = [round(c, 6) for c in m.diffuse_color]
open(out, 'w').write(json.dumps(F, indent=1, sort_keys=True)); print('FP', out)
