import bpy, sys, json, hashlib
import numpy as np
out = sys.argv[sys.argv.index('--') + 1]
F = {}
for o in sorted(bpy.data.objects, key=lambda o: o.name):
    e = {'mw': np.array(o.matrix_world).round(5).tolist(), 'mats': [s.material.name if s.material else None for s in o.material_slots],
         'parent': o.parent.name if o.parent else None, 'hide': o.hide_render, 'mods': [m.type for m in o.modifiers]}
    if o.type == 'MESH':
        co = np.empty(len(o.data.vertices) * 3); o.data.vertices.foreach_get('co', co)
        mi = np.empty(len(o.data.polygons), np.int32); o.data.polygons.foreach_get('material_index', mi)
        sm = np.empty(len(o.data.polygons), bool); o.data.polygons.foreach_get('use_smooth', sm)
        e['mesh'] = hashlib.sha1(co.round(5).tobytes() + mi.tobytes() + sm.tobytes()).hexdigest()[:16]
        e['nv'] = len(o.data.vertices)
    F[o.name] = e
M = {m.name: [round(c, 6) for c in m.diffuse_color] for m in bpy.data.materials}
json.dump({'objects': F, 'materials': M}, open(out, 'w'))
