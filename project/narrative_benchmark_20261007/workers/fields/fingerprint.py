"""Dump a fingerprint of every object / material (+ ridge check on F_centuriatio) to JSON.
Run: Blender -b X.blend --factory-startup --python fingerprint.py -- <out.json>"""
import bpy, sys, json, hashlib, bmesh
import numpy as np
out = sys.argv[sys.argv.index('--') + 1]
def h(a): return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()[:16]
fp = {'objects': {}, 'materials': {}}
for o in bpy.data.objects:
    d = {'type': o.type, 'mw': h(np.round(np.array(o.matrix_world), 5)), 'hide_render': o.hide_render,
         'slots': [s.material.name if s.material else None for s in o.material_slots]}
    if o.type == 'MESH':
        me = o.data; V = np.zeros(len(me.vertices) * 3, np.float32); me.vertices.foreach_get('co', V)
        L = np.zeros(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', L)
        M = np.zeros(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', M)
        d.update(nv=len(me.vertices), nf=len(me.polygons), co=h(V), loops=h(L), mat_index=h(M), mesh=me.name)
    fp['objects'][o.name] = d
for m in bpy.data.materials:
    fp['materials'][m.name] = [round(c, 6) for c in m.diffuse_color]
fp['scene'] = {'camera': bpy.context.scene.camera.name, 'res': list(bpy.context.scene.render.resolution[:]) if hasattr(bpy.context.scene.render, 'resolution') else [bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y],
               'shading': [bpy.context.scene.display.shading.light, bpy.context.scene.display.shading.color_type]}
o = bpy.data.objects['F_centuriatio']; me = o.data
V = np.zeros(len(me.vertices) * 3); me.vertices.foreach_get('co', V); V = V.reshape(-1, 3)
fp['F_first_verts_hash'] = {n: h(V[:n].astype(np.float32)) for n in (28590,)}
# ridge check: in every ridged plate, crop faces must sit above soil faces (residual to the plate's plane)
names = [s.material.name if s.material else '' for s in o.material_slots]
bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
seen = set(); stats = []
for f in bm.faces:
    if f.index in seen: continue
    st = [f]; seen.add(f.index); fs = []
    while st:
        a = st.pop(); fs.append(a)
        for e in a.edges:
            for g in e.link_faces:
                if g.index not in seen: seen.add(g.index); st.append(g)
    kinds = {names[x.material_index] for x in fs}
    if not any('crop_' in k for k in kinds): continue
    P = np.array([v.co[:] for x in fs for v in x.verts]); A = np.c_[P[:, 0], P[:, 1], np.ones(len(P))]
    cf = np.linalg.lstsq(A, P[:, 2], rcond=None)[0]
    def resid(x):
        c = x.calc_center_median(); return c.z - (cf[0] * c.x + cf[1] * c.y + cf[2])
    # rim (lip) faces touch the plate's two end rows; leave them out by taking only faces whose verts are not on the lip
    zr = {v: v.co.z - (cf[0] * v.co.x + cf[1] * v.co.y + cf[2]) for x in fs for v in x.verts}
    lip = np.percentile(list(zr.values()), 95)
    crop = [resid(x) for x in fs if 'crop_' in names[x.material_index]]
    soil = [resid(x) for x in fs if 'soil_' in names[x.material_index] and max(zr[v] for v in x.verts) < lip - 1e-4]
    stats.append((float(np.mean(crop)), float(np.mean(soil)), float(min(crop)), float(max(soil)) if soil else None))
S = np.array([(a, b, c) for a, b, c, d in stats])
fp['ridge_check'] = {'ridged_plates': len(stats), 'crop_mean_resid_avg': round(float(S[:, 0].mean()), 4),
                     'soil_mean_resid_avg': round(float(S[:, 1].mean()), 4),
                     'plates_crop_above_soil': int((S[:, 0] > S[:, 1]).sum())}
open(out, 'w').write(json.dumps(fp, indent=0))
print('FP', json.dumps(fp['ridge_check']))
