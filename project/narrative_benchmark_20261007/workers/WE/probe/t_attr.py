import bpy, bmesh, numpy as np
o = bpy.data.objects['R1_road5_bed']; me = o.data
a = me.attributes.new('rc_we_orig_co', 'FLOAT_VECTOR', 'POINT')
co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co); a.data.foreach_set('vector', co)
bm = bmesh.new(); bm.from_mesh(me)
print('bm float_vector layers', list(bm.verts.layers.float_vector.keys()) if hasattr(bm.verts.layers, 'float_vector') else 'no float_vector')
bm.verts.ensure_lookup_table()
bmesh.ops.delete(bm, geom=[bm.verts[0]], context='VERTS')
bm.to_mesh(me); me.update()
b = me.attributes.get('rc_we_orig_co'); print('after delete', len(me.vertices), b is not None, b and b.data_type)
v = np.empty(len(me.vertices) * 3); b.data.foreach_get('vector', v); print(v.reshape(-1, 3)[:3], co.reshape(-1, 3)[1:4])
print(bpy.app.version_string)
