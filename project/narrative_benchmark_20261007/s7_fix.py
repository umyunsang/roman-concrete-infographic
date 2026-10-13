import bpy, json, math, runpy, sys, time
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
T0 = time.time()
BASE = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/'
g = runpy.run_path(BASE + 'nb_work/workers/inventory/inventory.py')
to_pt_np = g['to_pt_np']
sc = bpy.context.scene; cam = sc.camera; camloc = np.array(cam.matrix_world.translation)
dg = bpy.context.evaluated_depsgraph_get()
def mesh(name):
    o = bpy.data.objects[name]; ev = o.evaluated_get(dg); me = ev.to_mesh(); M = o.matrix_world
    V = np.array([tuple(M @ v.co) for v in me.vertices]); F = [tuple(p.vertices) for p in me.polygons]
    mats = np.array([p.material_index for p in me.polygons]); mn = [s.material.name if s.material else '' for s in o.material_slots]
    ev.to_mesh_clear(); return V, F, mats, mn
ROADS = ['R_core_road', 'R1_road_landing1', 'R1_road_landing5', 'R1_road5_bed', 'R_via_appia', 'R_via_ostiensis', 'R_roadgeo_ostiensis_junction_fill', 'R4_bridge_west_bed']
RV = {n: mesh(n)[0] for n in ROADS}
Tv, Tf, _, _ = mesh('T_land'); TB = BVHTree.FromPolygons([Vector(v) for v in Tv], Tf)
podV, podF, _, _ = mesh('R3_colosseum_podium')
cypV = mesh('T_cypress')[0]
def terrain_z(x, y):
    h = TB.ray_cast(Vector((x, y, 50)), Vector((0, 0, -1)))
    return h[0].z if h[0] is not None else None
out = {}
for name, rng in (('MS3_core34_to_5', 3.0), ('MS2_core2_to_34', 3.0)):
    V, F, mats, mn = mesh(name)
    pl = [i for i, m in enumerate(mn) if 'plinth' in m]
    plv = sorted({v for fi, f in enumerate(F) if mats[fi] in pl for v in f})
    zb = V[plv, 2].min()
    foot = V[plv][V[plv, 2] <= zb + 0.05][:, :2]
    c0 = foot.mean(0)
    # footprint as convex hull (angle sort)
    ang = np.arctan2(foot[:, 1] - c0[1], foot[:, 0] - c0[0])
    hull = foot[np.argsort(ang)]
    # road vertices near
    allR = np.concatenate([RV[n] for n in ROADS]); names = np.concatenate([[n] * len(RV[n]) for n in ROADS])
    near = np.hypot(allR[:, 0] - c0[0], allR[:, 1] - c0[1]) < 25
    R = allR[near]; Rn = names[near]
    Ruv = to_pt_np(R)
    res = []
    base_uv = to_pt_np(V)
    for dx in np.arange(-rng, rng + 1e-6, 0.25):
        for dy in np.arange(-rng, rng + 1e-6, 0.25):
            c = c0 + np.array([dx, dy])
            # terrain under footprint: set plinth bottom at median terrain z (flush)
            tz = [terrain_z(*(p + [dx, dy])) for p in hull[::max(1, len(hull) // 12)]]
            tz = [t for t in tz if t is not None]
            if not tz: continue
            dz = float(np.median(tz)) - zb
            Vt = V + np.array([dx, dy, dz])
            # footprint vs road: XY distance from road vertices to footprint polygon (approx via centre distance minus radius)
            hp = hull + [dx, dy]
            # point-in-convex test for road verts
            d_c = np.hypot(R[:, 0] - c[0], R[:, 1] - c[1])
            cand = d_c < 6
            inside = 0; mind = 1e9
            for p in R[cand]:
                # distance to polygon edges
                dmin = 1e9; ins = True
                for i in range(len(hp)):
                    a, b = hp[i], hp[(i + 1) % len(hp)]
                    ab = b - a; t = np.clip(((p[:2] - a) @ ab) / (ab @ ab), 0, 1); q = a + t * ab
                    dmin = min(dmin, float(np.hypot(*(p[:2] - q))))
                    if (ab[0] * (p[1] - a[1]) - ab[1] * (p[0] - a[0])) < 0: ins = False
                if ins: inside += 1
                mind = min(mind, dmin)
            if inside: continue
            gap_pt = mind * 8.1
            if not (1.0 <= gap_pt <= 10.0): continue
            # occlusion of road vertices by moved milestone
            bvh = BVHTree.FromPolygons([Vector(v) for v in Vt], F)
            uvm = base_uv + (to_pt_np(np.array([[c[0], c[1], zb + dz]])) - to_pt_np(np.array([[c0[0], c0[1], zb]])))
            bx = [uvm[:, 0].min() - 2, uvm[:, 0].max() + 2, uvm[:, 1].min() - 2, uvm[:, 1].max() + 2]
            sel = (Ruv[:, 0] >= bx[0]) & (Ruv[:, 0] <= bx[1]) & (Ruv[:, 1] >= bx[2]) & (Ruv[:, 1] <= bx[3])
            occ = 0
            for p in R[sel]:
                d = camloc - p; d /= np.linalg.norm(d)
                h = bvh.ray_cast(Vector(p) + Vector(d) * 2e-3, Vector(d))
                if h[0] is not None: occ += 1
            # gaps to podium and cypress (XY, world -> pt)
            dpod = float(np.min(np.hypot(podV[:, 0] - c[0], podV[:, 1] - c[1]))) - float(np.max(np.hypot(hp[:, 0] - c[0], hp[:, 1] - c[1])))
            res.append([float(dx), float(dy), float(dz), gap_pt, occ, dpod * 8.1, to_pt_np(np.array([[c[0], c[1], zb + dz]]))[0].tolist()])
    res.sort(key=lambda r: (r[4], math.hypot(r[0], r[1])))
    out[name] = {'c0': c0.tolist(), 'best': res[:15], 'n_ok_occ0': sum(1 for r in res if r[4] == 0), 'n': len(res)}
    print(name, 'candidates', len(res), 'zero-occ', out[name]['n_ok_occ0'], 'best', res[:5], round(time.time() - T0, 1))
json.dump(out, open(BASE + 'opb2/s7_fix.json', 'w'))
