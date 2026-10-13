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
for name in ['MS1_core1_to_2', 'MS2_core2_to_34', 'MS3_core34_to_5']:
    V, F, mats, mn = mesh(name)
    pl = [i for i, m in enumerate(mn) if 'plinth' in m]
    plv = np.array(sorted({v for fi, f in enumerate(F) if mats[fi] in pl for v in f}))
    zb = V[plv, 2].min(); zt = V[plv, 2].max(); c = V[plv][V[plv, 2] <= zb + 0.05][:, :2].mean(0)
    isp = np.zeros(len(V), bool); isp[plv] = True
    near = RV[np.hypot(RV[:, 0] - c[0], RV[:, 1] - c[1]) < 15]
    for S in (1.0, 0.6, 0.55):
        V2 = V.copy()
        up = ~isp
        V2[up, :2] = c + (V[up, :2] - c) * S
        V2[up, 2] = zt + (V[up, 2] - zt) * S
        bvh = BVHTree.FromPolygons([Vector(v) for v in V2], F)
        occ = 0
        for p in near:
            d = camloc - p; d /= np.linalg.norm(d)
            if bvh.ray_cast(Vector(p) + Vector(d) * 2e-3, Vector(d))[0] is not None: occ += 1
        h = np.linalg.norm(to_pt_np(np.array([[c[0], c[1], zb], [c[0], c[1], V2[:, 2].max()]]))[1] - to_pt_np(np.array([[c[0], c[1], zb], [c[0], c[1], V2[:, 2].max()]]))[0])
        print(name, 'plinth kept, column+plate scale', S, 'h_pt', round(float(h), 1), 'occluded road verts (MS-only test)', occ)
