import bpy, json, math, runpy, sys, time
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
T0 = time.time()
BASE = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/'
g = runpy.run_path(BASE + 'nb_work/workers/inventory/inventory.py')
to_pt_np = g['to_pt_np']; render_visible = g['render_visible']; in_overlay = g['in_overlay']
IDX = json.load(open(BASE + 'nb_work/review_loop/obj_r11/assets_index.json'))
ASSET = {a['id']: a for a in IDX['assets']}
sc = bpy.context.scene; cam = sc.camera; camloc = Vector(cam.matrix_world.translation)
dg = bpy.context.evaluated_depsgraph_get()
vis = sorted([o for o in bpy.data.objects if render_visible(o)], key=lambda o: o.name)
GEO = {}; TREES = {}; AABB = {}
for o in vis:
    if in_overlay(o): continue
    ev = o.evaluated_get(dg); me = ev.to_mesh(); M = o.matrix_world
    verts = [M @ v.co for v in me.vertices]; polys = [tuple(p.vertices) for p in me.polygons]
    if polys:
        GEO[o.name] = np.array([tuple(v) for v in verts]); TREES[o.name] = BVHTree.FromPolygons(verts, polys)
        AABB[o.name] = (GEO[o.name].min(0), GEO[o.name].max(0))
    ev.to_mesh_clear()
def cast(origin, d, maxdist=1e5, skip=(), only=None):
    origin = Vector(origin); d = Vector(d).normalized(); best = None
    for n in (only if only is not None else TREES.keys()):
        if n in skip or n not in TREES: continue
        lo, hi = AABB[n]
        if not (lo[0] - .05 <= origin.x <= hi[0] + .05 and lo[1] - .05 <= origin.y <= hi[1] + .05) and abs(d.z) > 0.99: continue
        h = TREES[n].ray_cast(origin, d, maxdist)
        if h[0] is not None and (best is None or h[3] < best[3]): best = (n, h[0], h[1], h[3])
    return best
ROADS = ['R_core_road', 'R1_road_landing1', 'R1_road_landing5', 'R1_road5_bed', 'R_via_appia', 'R_via_ostiensis', 'R_roadgeo_ostiensis_junction_fill']
BR = ['B_pons1', 'B_pons1_parapet0', 'B_pons1_parapet1', 'B_pons2', 'B_pons2_parapet0', 'B_pons2_parapet1', 'R4_bridge_west_bed']
res = {}
# world grid over R_core_road + landing1 extents; classify each road point by region via projected pt
P = np.concatenate([GEO['R_core_road'], GEO['R1_road_landing1']])
lo, hi = P.min(0), P.max(0)
step = 0.12
regs = {k: v['bbox_visible_final_pt'] for k, v in ASSET.items() if k.startswith('road_core')}
pts = []
for x in np.arange(lo[0], hi[0], step):
    for y in np.arange(lo[1], hi[1], step):
        h = cast((x, y, 40), (0, 0, -1), 100, only=['R_core_road', 'R1_road_landing1'] )
        if not h: continue
        top = h[1]
        # is the road the first thing seen from above (skip nothing)? record
        # support below the road: continue down skipping roads
        s = cast((x, y, top.z - 1e-3), (0, 0, -1), 100, skip=set(ROADS))
        # terrain above road top? (terrain poke)
        tu = cast((x, y, top.z + 1e-3), (0, 0, 1), 5, only=['T_land'])
        # lowest road surface at this xy (bottom of paver): cast up from far below hitting road
        hb = cast((x, y, -20), (0, 0, 1), 100, only=['R_core_road', 'R1_road_landing1'])
        uv = to_pt_np(np.array([[x, y, top.z]]))[0]
        pts.append([float(x), float(y), float(top.z), s[0] if s else None, float(s[1].z) if s else None, tu[0] if tu else None, float(hb[1].z) if hb else None, float(uv[0]), float(uv[1])])
res['grid'] = pts
print('grid', len(pts), round(time.time() - T0, 1))
# river direction near bridges: L02_tiber vertices within r of bridge centre
for bn, deck in [('bridge_north', 'B_pons1'), ('bridge_south', 'B_pons2')]:
    D = GEO[deck]; c = D[:, :2].mean(0)
    U, S_, Vt = np.linalg.svd(D[:, :2] - c, full_matrices=False); ax = Vt[0]
    # river: sample water presence on a grid around the bridge, take water points within 9 units, PCA
    wp = []
    for x in np.arange(c[0] - 9, c[0] + 9, 0.25):
        for y in np.arange(c[1] - 9, c[1] + 9, 0.25):
            if math.hypot(x - c[0], y - c[1]) > 9: continue
            h = cast((x, y, 40), (0, 0, -1), 100, only=['L02_tiber', 'T_land'])
            if h and h[0] == 'L02_tiber': wp.append((x, y))
    wp = np.array(wp); wc = wp.mean(0)
    U, S_, Vt = np.linalg.svd(wp - wc, full_matrices=False); rv = Vt[0]
    ang = math.degrees(math.acos(abs(float(ax @ rv))))
    # road direction near each deck end: road top points 0.5..3.5 units beyond each end along/around axis
    t = (D[:, :2] - c) @ ax
    ends = {}
    for nm, sgn in (('end_min', -1), ('end_max', 1)):
        e = c + ax * (t.min() if sgn < 0 else t.max())
        rp = []
        RP = GEO['R_core_road']
        d_ = np.hypot(RP[:, 0] - e[0], RP[:, 1] - e[1])
        # road vertices outside deck (beyond end along axis) within 1..5 units of end
        along = (RP[:, :2] - e) @ ax * sgn
        sel = (d_ >= 0.8) & (d_ <= 5.0) & (along > -1.0)
        Q = RP[sel, :2]
        if len(Q) > 10:
            qc = Q.mean(0); U, S_, Vt = np.linalg.svd(Q - qc, full_matrices=False); rd = Vt[0]
            bend = math.degrees(math.acos(min(1.0, abs(float(ax @ rd)))))
        else:
            rd = None; bend = None; qc = None
        # gap: nearest road vertex to the deck end edge (world) -> pt
        j = int(np.argmin(d_))
        ends[nm] = {'end_xy': e.tolist(), 'end_pt': to_pt_np(np.array([[e[0], e[1], 0.3]]))[0].tolist(), 'road_dir': None if rd is None else rd.tolist(), 'bend_deg': bend,
                    'nearest_road_world': float(d_[j]), 'road_centroid_xy': None if qc is None else qc.tolist(), 'n_road_pts': int(sel.sum())}
    res[bn] = {'axis': ax.tolist(), 'river_dir': rv.tolist(), 'axis_river_angle_deg': ang, 'eps_deg': abs(90 - ang), 'n_water_pts': len(wp), 'ends': ends}
print('bridges', round(time.time() - T0, 1))
json.dump(res, open(BASE + 'opb2/s5_roads.json', 'w'))
print('DONE', round(time.time() - T0, 1))
