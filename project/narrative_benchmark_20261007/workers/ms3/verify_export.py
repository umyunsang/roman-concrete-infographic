"""Independent verification export (run inside Blender on any blend; saves nothing).
Run: Blender -b <x.blend> --factory-startup --python verify_export.py -- <out_prefix>
Writes <out_prefix>_tris.npz  (projected triangles, pt, of every map / overlay object near MS3 + text boxes)
       <out_prefix>_check.json (hidden road vertices by MS3, plinth footing, object fingerprints)."""
import bpy, sys, json, hashlib
from pathlib import Path
import numpy as np
from mathutils import Vector
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, need, world_verts, bvh_of, Terrain, map_visible_objects, overlay_objects, screen_tris

out = sys.argv[sys.argv.index('--') + 1]
S = Screen(); ms = need('MS3_core34_to_5')
P, T = screen_tris(ms, S); box = (P[:, 0].min() - 80, P[:, 0].max() + 80, P[:, 1].min() - 80, P[:, 1].max() + 80)
arrays, kinds = {}, {}
for kind, objs in (('map', map_visible_objects()), ('overlay', overlay_objects())):
    for o in objs:
        if o.name == 'T_land' or len(o.data.vertices) == 0: continue
        P, T = screen_tris(o, S)
        if len(T) == 0: continue
        tri = P[T]
        keep = (tri[:, :, 0].max(1) >= box[0]) & (tri[:, :, 0].min(1) <= box[1]) & (tri[:, :, 1].max(1) >= box[2]) & (tri[:, :, 1].min(1) <= box[3])
        if keep.any(): arrays[o.name] = tri[keep].astype(np.float32); kinds[o.name] = kind
# MS3 arrow triangles separately
me = ms.data; me.calc_loop_triangles()
k = [i for i, s in enumerate(ms.material_slots) if s.material and 'direction_arrow' in s.material.name][0]
mi = np.empty(len(me.loop_triangles), np.int32); me.loop_triangles.foreach_get('material_index', mi)
P, T = screen_tris(ms, S); arrays['__MS3_arrow'] = P[T][mi == k].astype(np.float32)
np.savez_compressed(out + '_tris.npz', **arrays)

res = {'kinds': kinds, 'box': [float(v) for v in box]}
# hidden road vertices: (a) camera ray hits MS3 before the vertex; (b) first hit among all non-road map objects is MS3
roads = [o for o in map_visible_objects() if o.name.startswith(('R_', 'R1_', 'R4_bridge', 'B_pons'))]
blk = [o for o in map_visible_objects() if o not in roads and o.name != 'T_land']
B_all, own = bvh_of(blk); B_ms, _ = bvh_of([ms])
org = S.origin
ha, hb = {}, {}
for r in roads:
    for p in world_verts(r):
        d = Vector(p) - org; L = d.length; d /= L
        if B_ms.ray_cast(org, d, L - 0.05)[0] is not None: ha[r.name] = ha.get(r.name, 0) + 1
        h = B_all.ray_cast(org, d, L - 0.05)
        if h[0] is not None and own[h[2]] == ms.name: hb[r.name] = hb.get(r.name, 0) + 1
res['hidden_by_ms3_any'] = ha; res['hidden_by_ms3_first_hit'] = hb
res['hidden_total'] = [sum(ha.values()), sum(hb.values())]
# footing: plinth bottom ring vs T_land and vs road top under it
TER = Terrain(need('T_land'))
co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
kp = [i for i, s in enumerate(ms.material_slots) if s.material and 'roman_plinth' in s.material.name][0]
pv = sorted({v for p in me.polygons if p.material_index == kp for v in p.vertices})
W = world_verts(ms); Wp = W[pv]; bot = Wp[Wp[:, 2] < Wp[:, 2].min() + 0.01]
rel = np.array([p[2] - TER.z(p[0], p[1]) for p in bot])
xs = np.linspace(bot[:, 0].min(), bot[:, 0].max(), 15); ys = np.linspace(bot[:, 1].min(), bot[:, 1].max(), 15)
res['footing'] = {'bottom_z': round(float(Wp[:, 2].min()), 4), 'plinth_top_z': round(float(Wp[:, 2].max()), 4),
                  'bottom_ring_minus_ground_min_med_max': [round(float(rel.min()), 3), round(float(np.median(rel)), 3), round(float(rel.max()), 3)],
                  'ring_points_above_ground': int((rel > 0).sum()), 'ring_points': len(rel),
                  'ground_in_bbox_min_max': [round(float(min(TER.z(x, y) for x in xs for y in ys)), 3), round(float(max(TER.z(x, y) for x in xs for y in ys)), 3)],
                  'world_per_pt': round(float(S.world_per_pt(Vector(bot.mean(0)))), 4)}
res['ms3'] = {'location': [round(v, 4) for v in ms.matrix_world.translation], 'rot_z_deg': round(float(np.degrees(ms.rotation_euler.z)), 3),
              'scale': [round(v, 4) for v in ms.scale]}


def mesh_fp(m):
    h = hashlib.sha256()
    for label, coll, field, width, dt in (('v', m.vertices, 'co', 3, np.float32), ('e', m.edges, 'vertices', 2, np.int32),
                                          ('l', m.loops, 'vertex_index', 1, np.int32), ('pm', m.polygons, 'material_index', 1, np.int32)):
        a = np.empty(len(coll) * width, dt); coll.foreach_get(field, a); h.update(label.encode()); h.update(a.tobytes())
    return h.hexdigest()[:16]


fp = {}
for o in sorted(bpy.data.objects, key=lambda x: x.name):
    h = hashlib.sha256(np.array(o.matrix_world, np.float64).round(6).tobytes())
    h.update(json.dumps([o.hide_render, [s.material.name if s.material else None for s in o.material_slots]]).encode())
    fp[o.name] = {'all': h.hexdigest()[:16] + (mesh_fp(o.data) if o.type == 'MESH' else ''),
                  'mesh': mesh_fp(o.data) if o.type == 'MESH' else None}
res['fingerprints'] = fp
res['materials'] = {m.name: [round(c, 6) for c in m.diffuse_color] for m in bpy.data.materials}
res['scene_props'] = {k: str(bpy.context.scene[k])[:400] for k in bpy.context.scene.keys()}
Path(out + '_check.json').write_text(json.dumps(res, ensure_ascii=False, indent=1))
print('VERIFY_EXPORT_DONE', len(arrays), res['hidden_total'], res['footing'])
