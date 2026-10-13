import bpy, json, sys, runpy
from pathlib import Path
import numpy as np
NB = Path('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work')
INV = runpy.run_path(str(NB / 'workers/inventory/inventory.py'), run_name='inventory_lib')
to_pt_np = INV['to_pt_np']
dg = bpy.context.evaluated_depsgraph_get()
out = {}
for nm in ['D2_heat1', 'H_book1', 'H_core_sample', 'H_mold_box', 'H_lime_pile', 'H_stone0', 'NB_modern_building', 'C2_hot_mixing', 'R1_lab_bench', 'D2_cube']:
    ob = bpy.data.objects[nm]
    ev = ob.evaluated_get(dg); me = ev.to_mesh()
    co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co); ev.to_mesh_clear()
    M = np.array(ob.matrix_world); P = co.reshape(-1, 3) @ M[:3, :3].T + M[:3, 3]
    c = P.mean(0)
    base = to_pt_np(c[None])[0]
    d = {}
    for k, v in (('x', [1, 0, 0]), ('y', [0, 1, 0]), ('z', [0, 0, 1]), ('screen_right_dir', [0.7071, 0.7071, 0]), ('toward_cam_dir', [0.7071, -0.7071, 0])):
        d[k] = (to_pt_np((c + np.array(v) * 0.1)[None])[0] - base).tolist()
    out[nm] = {'center_pt': base.tolist(), 'dpt_per_0.1unit': d, 'parent': ob.parent.name if ob.parent else None}
print(json.dumps(out, indent=0))
