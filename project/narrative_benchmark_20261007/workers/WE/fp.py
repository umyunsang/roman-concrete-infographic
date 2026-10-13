"""fp.py - per-object fingerprints (mesh coordinates rounded 1e-5, topology, material indices and slots, material
colours, sharp_edge / field-role attributes, matrix). Blender -b <blend> --factory-startup --python fp.py -- <out.json>"""
import bpy, sys, json, hashlib
import numpy as np
from pathlib import Path
fp = {}
for o in bpy.data.objects:
    h = hashlib.sha1()
    h.update(np.array(o.matrix_world, np.float64).round(6).tobytes())
    if o.type == 'MESH':
        me = o.data
        co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co); h.update(co.round(5).tobytes())
        pv = np.empty(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', pv); h.update(pv.tobytes())
        mi = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', mi); h.update(mi.tobytes())
        for an in ('sharp_edge', 'sharp_face', 'rc_v12_13_field_role'):
            a = me.attributes.get(an)
            if a is not None:
                v = np.zeros(len(a.data), np.int32 if a.data_type == 'INT' else bool); a.data.foreach_get('value', v); h.update(v.tobytes())
    for s in o.material_slots:
        m = s.material
        h.update(repr(m.name if m else None).encode())
        if m:
            h.update(np.array(m.diffuse_color).round(6).tobytes())
    fp[o.name] = h.hexdigest()
Path(sys.argv[sys.argv.index('--') + 1]).write_text(json.dumps(fp, indent=0, sort_keys=True))
print('FP', len(fp))
