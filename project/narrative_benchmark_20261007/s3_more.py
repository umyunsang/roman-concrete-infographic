import bpy, json, math, runpy, sys, time
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
T0 = time.time()
BASE = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/'
g = runpy.run_path(BASE + 'nb_work/workers/inventory/inventory.py')
to_pt_np = g['to_pt_np']; render_visible = g['render_visible']; in_overlay = g['in_overlay']
OUT = BASE + 'opb2/'
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
    if not polys:
        ev.to_mesh_clear(); continue
    GEO[o.name] = dict(P=np.array([tuple(v) for v in verts]), polys=polys, mats=np.array([p.material_index for p in me.polygons]),
                       matnames=[s.material.name if s.material else None for s in o.material_slots],
                       normals=np.array([tuple((M.to_3x3() @ p.normal).normalized()) for p in me.polygons]),
                       centers=np.array([tuple(M @ p.center) for p in me.polygons]), areas=np.array([p.area for p in me.polygons]))
    ev.to_mesh_clear()
    TREES[o.name] = BVHTree.FromPolygons(verts, polys)
    AABB[o.name] = (GEO[o.name]['P'].min(0), GEO[o.name]['P'].max(0))
def cast(origin, d, maxdist=1e5, skip=(), only=None):
    origin = Vector(origin); d = Vector(d).normalized(); best = None
    for n in (only or TREES.keys()):
        if n in skip: continue
        lo, hi = AABB[n]
        h = TREES[n].ray_cast(origin, d, maxdist)
        if h[0] is not None and (best is None or h[3] < best[3]): best = (n, h[0], h[1], h[3])
    return best
def ptz(p):
    return to_pt_np(np.array(p))
res = {}
ROADS = ['R_core_road', 'R1_road_landing1', 'R1_road_landing5', 'R1_road5_bed', 'R_via_appia', 'R_via_ostiensis', 'R_roadgeo_ostiensis_junction_fill']
# ---- 1. road top-face triangles
for n in ROADS + ['L02_tiber', 'B_pons1', 'B_pons2', 'R4_bridge_west_bed']:
    G = GEO[n]; uv = to_pt_np(G['P']); tris = []
    for fi, poly in enumerate(G['polys']):
        if G['normals'][fi][2] > 0.5:
            for j in range(1, len(poly) - 1): tris.append((poly[0], poly[j], poly[j + 1]))
    if tris: np.save(OUT + f'tritop_{n}.npy', uv[np.array(tris)].astype(np.float32))
print('tops', round(time.time() - T0, 1))
# ---- 2. road support sampling (core road + landing1): bottom-ish vertices -> cast down skipping roads
sup = []
for n in ['R_core_road', 'R1_road_landing1']:
    P = GEO[n]['P']
    idx = np.arange(0, len(P), 3)
    uv = to_pt_np(P[idx])
    for k, i in enumerate(idx):
        p = Vector(P[i])
        cand = [m for m, (lo, hi) in AABB.items() if m not in ROADS and lo[0] - .1 <= p.x <= hi[0] + .1 and lo[1] - .1 <= p.y <= hi[1] + .1]
        h = cast(p + Vector((0, 0, 1e-3)), (0, 0, -1), 50, only=cand)
        hu = cast(p - Vector((0, 0, 1e-3)), (0, 0, 1), 0.6, only=cand)
        sup.append([n, float(uv[k, 0]), float(uv[k, 1]), h[0] if h else None, (h[3] - 1e-3) if h else None, hu[0] if hu else None, (hu[3] - 1e-3) if hu else None, float(p.z)])
res['road_support'] = sup
print('road support', len(sup), round(time.time() - T0, 1))
# ---- 3. milestones: plinth footprint vs road (world XY grid), terrain under corners, plinth thickness, pillar axis
for aid, n in [('milestone_1_to_2', 'MS1_core1_to_2'), ('milestone_2_to_34', 'MS2_core2_to_34'), ('milestone_34_to_5', 'MS3_core34_to_5')]:
    G = GEO[n]; mn = G['matnames']
    def fidx(key): return np.where(np.isin(G['mats'], [i for i, m in enumerate(mn) if m and key in m]))[0]
    fp, fs = fidx('roman_plinth'), fidx('milestone_stone')
    Pp = G['P'][sorted({v for f in fp for v in G['polys'][f]})]
    Ps = G['P'][sorted({v for f in fs for v in G['polys'][f]})]
    zb, zt = Pp[:, 2].min(), Pp[:, 2].max()
    # footprint hull XY via simple convex hull (monotone chain)
    pts = sorted(set(map(tuple, np.round(Pp[Pp[:, 2] <= zb + 0.05][:, :2], 5))))
    def cross(o, a, b): return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower = []; upper = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0: lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0: upper.pop()
        upper.append(p)
    hull = np.array(lower[:-1] + upper[:-1])
    # grid inside hull
    lo, hi = hull.min(0), hull.max(0)
    xs = np.arange(lo[0], hi[0], 0.04); ys = np.arange(lo[1], hi[1], 0.04)
    inside = []; onroad = []; terr = []
    from matplotlib.path import Path as _P
