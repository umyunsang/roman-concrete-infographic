"""idmap.py - per-pixel ID map aligned with a render_crops job (same pixel grid).
Blender -b <blend> --factory-startup --python idmap.py -- <jobs_done.json> <job name> <out.npz>
Saves: hit (object index, -1 none), names, mat (material name index, -1), mats, normal (world, 3), depth."""
import bpy, sys, json, numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/WD1')
import wd1lib as L
argv = sys.argv[sys.argv.index('--') + 1:]
jobs = json.load(open(argv[0])); job = next(j for j in jobs if j['name'] == argv[1]); out = argv[2]
S = L.Screen()
objs = L.map_visible_objects()
dg = bpy.context.evaluated_depsgraph_get()
bvh, owner, fidx = L.bvh_of(objs)
mat_of = {}
for o in objs:
    ev = o.evaluated_get(dg); me = ev.to_mesh()
    mi = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', mi)
    slots = [s.material.name if s.material else '' for s in o.material_slots] or ['']
    mat_of[o.name] = (mi, slots)
    ev.to_mesh_clear()
x0, x1, y0, y1 = job['px_box']; s = job['s_eff']
H, Wd = y1 - y0, x1 - x0
names, mats = [], []
hit = -np.ones((H, Wd), np.int32); mat = -np.ones((H, Wd), np.int32); nrm = np.zeros((H, Wd, 3), np.float32)
for j in range(H):
    for i in range(Wd):
        pt = ((x0 + i + 0.5) / s, (y0 + j + 0.5) / s)
        org, d = S.ray(pt)
        loc, n, idx, dist = bvh.ray_cast(org, d)
        if idx is None:
            continue
        o = owner[idx]
        if o not in names:
            names.append(o)
        hit[j, i] = names.index(o)
        mi, slots = mat_of[o]
        mn = slots[min(mi[fidx[idx]], len(slots) - 1)]
        if mn not in mats:
            mats.append(mn)
        mat[j, i] = mats.index(mn)
        if n.dot(d) > 0:
            n = -n
        nrm[j, i] = n[:]
np.savez_compressed(out, hit=hit, names=np.array(names), mat=mat, mats=np.array(mats), normal=nrm,
                    right=np.array(S.cam.matrix_world.col[0].xyz.normalized()[:]))
print('IDMAP', job['name'], H, Wd, names[:8])
