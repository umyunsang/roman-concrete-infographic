import bpy, json, math, runpy, sys
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BASE = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/'
g = runpy.run_path(BASE + 'nb_work/workers/inventory/inventory.py'); to_pt_np = g['to_pt_np']
sc = bpy.context.scene; camloc = np.array(sc.camera.matrix_world.translation); dg = bpy.context.evaluated_depsgraph_get()
def mesh(n):
    o = bpy.data.objects[n]; ev = o.evaluated_get(dg); me = ev.to_mesh(); M = o.matrix_world
    V = np.array([tuple(M @ v.co) for v in me.vertices]); F = [tuple(p.vertices) for p in me.polygons]
    mats = np.array([p.material_index for p in me.polygons]); mn = [s.material.name if s.material else '' for s in o.material_slots]
    ev.to_mesh_clear(); return V, F, mats, mn
ROADS = ['R_core_road', 'R1_road_landing1', 'R1_road_landing5', 'R1_road5_bed', 'R_via_appia', 'R_via_ostiensis', 'R_roadgeo_ostiensis_junction_fill']
RV = np.concatenate([mesh(n)[0] for n in ROADS])
bedV = mesh('R4_bridge_west_bed')[0]
Tv, Tf, _, _ = mesh('T_land'); TB = BVHTree.FromPolygons([Vector(v) for v in Tv], Tf)
V, F, mats, mn = mesh('MS2_core2_to_34')
pl = [i for i, m in enumerate(mn) if 'plinth' in m]
plv = sorted({v for fi, f in enumerate(F) if mats[fi] in pl for v in f})
zb = V[plv, 2].min(); c = V[plv][V[plv, 2] <= zb + 0.05][:, :2].mean(0)
near = RV[np.hypot(RV[:, 0] - c[0], RV[:, 1] - c[1]) < 15]
def seg_dist(P, A, B):
    AB = B - A; t = np.clip(((P - A) @ AB) / (AB @ AB), 0, 1); return np.hypot(*(P - (A + t * AB)))
for S in (0.6,):
    for dx in np.arange(-0.5, 1.01, 0.25):
        for dy in np.arange(0.0, 1.76, 0.25):
            xy = (V[:, :2] - c) * S + c + [dx, dy]
            V2 = np.c_[xy, zb + (V[:, 2] - zb) * S]
            foot = V2[plv][V2[plv, 2] <= zb + 0.03]
            tz = [TB.ray_cast(Vector((p[0], p[1], 50)), Vector((0, 0, -1)))[0].z for p in foot[::max(1, len(foot) // 16)]]
            dz = float(np.median(tz)) - zb
            V2[:, 2] += dz
            bvh = BVHTree.FromPolygons([Vector(v) for v in V2], F)
            occ = 0
            for p in near:
                d = camloc - p; d /= np.linalg.norm(d)
                if bvh.ray_cast(Vector(p) + Vector(d) * 2e-3, Vector(d))[0] is not None: occ += 1
            # footprint-bed distance (world), road distance
            fxy = foot[:, :2]
            bd = min(min(seg_dist(p, bedV[i, :2], bedV[(i + 1) % 4, :2]) for i in range(4)) for p in fxy)
            rd = float(np.min(np.hypot(near[:, 0, None] - fxy[None, :, 0], near[:, 1, None] - fxy[None, :, 1])))
            k = float(np.linalg.norm(to_pt_np(np.array([[c[0], c[1], zb], [c[0] + 0.7071, c[1] + 0.7071, zb]]))[1] - to_pt_np(np.array([[c[0], c[1], zb], [c[0] + 0.7071, c[1] + 0.7071, zb]]))[0]))
            print('S', S, 'dx', round(dx, 2), 'dy', round(dy, 2), 'dz', round(dz, 3), 'occ', occ, 'bed gap ~pt', round(bd * k, 2), 'road-vertex gap ~pt', round(rd * k, 2), 'terrain span', round(max(tz) - min(tz), 3))
