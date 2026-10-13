"""Measurement export (run inside Blender on any blend): projected triangles of the map objects near the Colosseum
and Pantheon (for screen-silhouette gaps, measured outside Blender by measure.py) plus camera-ray checks.
Run: Blender -b <x.blend> --factory-startup --python measure_export.py -- <out_prefix>
Writes <out_prefix>_tris.npz and <out_prefix>_rays.json."""
import bpy, sys, json
from pathlib import Path
import numpy as np
from mathutils import Vector
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import Screen, need, world_verts, bvh_of, Terrain, map_visible_objects, overlay_objects, screen_tris

out = Path(sys.argv[sys.argv.index('--') + 1])
S = Screen(); O = bpy.data.objects
ROI = (100, 1100, 300, 1150)
arrays = {}; meta = {}
for kind, objs in (('map', map_visible_objects()), ('overlay', overlay_objects())):
    for o in objs:
        if o.name == 'T_land' or o.type != 'MESH' or len(o.data.vertices) == 0:
            continue
        P, T = screen_tris(o, S)
        if len(T) == 0:
            continue
        tri = P[T]
        keep = (tri[:, :, 0].max(1) >= ROI[0]) & (tri[:, :, 0].min(1) <= ROI[1]) & (tri[:, :, 1].max(1) >= ROI[2]) & (tri[:, :, 1].min(1) <= ROI[3])
        if not keep.any():
            continue
        arrays[o.name] = tri[keep].astype(np.float32)
        meta[o.name] = kind
np.savez_compressed(str(out) + '_tris.npz', **arrays)

res = {'kinds': meta}
origin = S.origin
mapobjs = map_visible_objects()
land = need('T_land'); TER = Terrain(land)
roads = [need(n) for n in ('R_core_road', 'R_via_appia', 'R_via_ostiensis')]
roadnames = {r.name for r in roads}
B, own = bvh_of([o for o in mapobjs if o.name not in roadnames | {'T_land'}])
OV, own_ov = bvh_of(overlay_objects())
hidden = {}
for r in roads:
    W = world_verts(r); per = {}; terr = 0; ov = {}; pts = {}
    for p in W:
        d = Vector(p) - origin; L = d.length; dn = d / L
        h = B.ray_cast(origin, dn, L - 0.05)
        if h[0] is not None:
            nm = own[h[2]]; per[nm] = per.get(nm, 0) + 1
            pts.setdefault(nm, []).append(S.to_pt(Vector(p)).round(1).tolist())
        elif TER.bvh.ray_cast(origin, dn, L - 0.05)[0] is not None:
            terr += 1
        h2 = OV.ray_cast(origin, dn, 1e4)
        if h2[0] is not None:
            nm = own_ov[h2[2]]; ov[nm] = ov.get(nm, 0) + 1
    boxes = {k: [round(float(np.min(np.array(v)[:, 0]))), round(float(np.max(np.array(v)[:, 0]))),
                 round(float(np.min(np.array(v)[:, 1]))), round(float(np.max(np.array(v)[:, 1])))] for k, v in pts.items()}
    hidden[r.name] = {'vertices': len(W), 'hidden_by_object': per, 'hidden_box_pt': boxes,
                      'hidden_by_terrain_only': terr, 'under_overlay_shapes': ov}
res['roads_hidden'] = hidden

# footing checks
col, pod, pan = need('COL_ruined'), need('R3_colosseum_podium'), need('R8_pantheon')
ALL, own_all = bvh_of(mapobjs)
PW = world_verts(pod); inner = PW[0::3, :2]
def inside_poly(poly, P):
    x, y = P[:, 0], P[:, 1]; r = np.zeros(len(P), bool); n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if y1 == y2: continue
        r ^= ((y1 > y) != (y2 > y)) & (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1)
    return r
def visible(p):
    d = Vector(p) - origin; L = d.length
    return ALL.ray_cast(origin, d / L, L - 0.03)[0] is None
# podium inner edge must stay under the walls (a visible inner vertex = gap between wall foot and podium)
vis_inner = [S.to_pt(Vector(p)).round(1).tolist() for p in PW[0::3] if visible(p)]
res['podium_inner_edge_visible'] = {'count': len(vis_inner), 'of': len(PW) // 3, 'points_pt': vis_inner[:40]}
# Colosseum vertices below the podium top that lie outside the podium inner ring and can be seen (exposed footing)
CW = world_verts(col)
top_z = float(np.median(PW[1::3, 2]))
cand = CW[(CW[:, 2] < top_z - 0.02)]
cand = cand[~inside_poly(inner, cand[:, :2])]
vis_low = [S.to_pt(Vector(p)).round(1).tolist() for p in cand[::3] if visible(p)]
res['colosseum_low_outside_visible'] = {'count': len(vis_low), 'checked': len(cand[::3]), 'podium_top_z': round(top_z, 3),
                                        'points_pt': vis_low[:40]}
# Colosseum foot vs terrain/podium: lowest vertices per 10-degree sector
c = CW[:, :2].mean(0)
ang = np.degrees(np.arctan2(CW[:, 1] - c[1], CW[:, 0] - c[0]))
# Pantheon foot vs terrain
PA = world_verts(pan); zmin = PA[:, 2].min(); foot = PA[PA[:, 2] < zmin + 0.05]
rel = np.array([p[2] - TER.z(p[0], p[1]) for p in foot])
low = foot[np.argsort(rel)]
res['pantheon_foot'] = {'n': len(foot), 'rel_min_med_max': [round(float(rel.min()), 3), round(float(np.median(rel)), 3), round(float(rel.max()), 3)],
                        'float_gt_0.05': int((rel > 0.05).sum()),
                        'visible_floating_pts': [S.to_pt(Vector(p)).round(1).tolist() for p, r_ in zip(foot, rel) if r_ > 0.05 and visible(p)][:20],
                        'world_per_pt': round(float(S.world_per_pt(Vector(foot.mean(0)))), 4)}
(Path(str(out) + '_rays.json')).write_text(json.dumps(res, ensure_ascii=False, indent=1))
print('MEASURE_EXPORT_DONE', len(arrays))
