import bpy, hashlib, numpy as np, json
out = {}
for n in ['COL_ruined', 'R3_colosseum_podium', 'R4_arena_skin', 'T_land', 'R8_pantheon', 'R_core_road', 'R_via_appia', 'R_via_ostiensis', 'F_centuriatio', 'MS3_core34_to_5']:
    o = bpy.data.objects[n]; me = o.data
    co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co)
    pv = np.empty(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', pv)
    mi = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', mi)
    h = hashlib.sha256(); h.update(np.round(np.array(o.matrix_world), 6).tobytes()); h.update(np.round(co, 6).tobytes()); h.update(pv.tobytes()); h.update(mi.tobytes())
    h.update(','.join(s.material.name if s.material else '-' for s in o.material_slots).encode())
    out[n] = h.hexdigest()[:16]
out['marker'] = bpy.context.scene.get('rc_layout_v8_13a')
print('HASH ' + json.dumps(out))
