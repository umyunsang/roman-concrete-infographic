import bpy, sys, json
import numpy as np
out = sys.argv[sys.argv.index('--') + 1]
R = {}
for n in ['S_lead05', 'S_sect_tdot2', 'S_sect_tdot0', 'S_sect_dot1', 'S_sect_tdot3', 'S_sect_dot0']:
    o = bpy.data.objects[n]; co = np.empty(len(o.data.vertices) * 3); o.data.vertices.foreach_get('co', co)
    R[n] = {'co': co.tolist(), 'mw': np.array(o.matrix_world).tolist(), 'sm': [p.use_smooth for p in o.data.polygons][:5]}
json.dump(R, open(out, 'w'))
