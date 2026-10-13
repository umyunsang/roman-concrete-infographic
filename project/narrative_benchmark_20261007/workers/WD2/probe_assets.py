import bpy, sys, json, math, numpy as np
from mathutils import Vector
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/WD2')
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts
from wd2_lib import islands, bvh_world, ray_down_z
out = sys.argv[sys.argv.index('--')+1]
S = Screen(); sc = bpy.context.scene; dg = bpy.context.evaluated_depsgraph_get()
rep = {}
def isl_info(o, maxn=400):
    me = o.data; W = world_verts(o); mi = np.zeros(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', mi)
    res = []
    for fs in islands(me):
        vs = sorted({v for f in fs for v in me.polygons[f].vertices}); P = W[vs]; sp = S.project(P)
        mats = np.bincount(mi[fs], minlength=len(o.material_slots)).tolist()
        res.append({'nf': len(fs), 'mats': mats, 'c': P.mean(0).round(3).tolist(), 'wmin': P.min(0).round(3).tolist(), 'wmax': P.max(0).round(3).tolist(),
                    'pt': [round(sp[:,0].min(),1), round(sp[:,0].max(),1), round(sp[:,1].min(),1), round(sp[:,1].max(),1)]})
    res.sort(key=lambda r: -r['nf'])
    return {'slots': [s.material.name for s in o.material_slots], 'n_islands': len(res), 'islands': res[:maxn]}
for n in ['L09_portus_mole', 'C5_researchers', 'L08_pompeii_site', 'NB_marine_breakwater', 'L11_privernum_wall', 'T_cypress']:
    rep[n] = isl_info(bpy.data.objects[n])
# breakwater z histogram
o = bpy.data.objects['NB_marine_breakwater']; W = world_verts(o)
rep['bw_z_hist'] = np.histogram(W[:,2], bins=20)[0].tolist(); rep['bw_z_edges'] = np.histogram(W[:,2], bins=20)[1].round(3).tolist()
# pines: trunk lean, base gap, support under base
land = bvh_world([bpy.data.objects['T_land']])
pines = {}
for o in bpy.data.objects:
    if not o.name.startswith('T_pine'): continue
    me = o.data; W = world_verts(o)
    mi = np.zeros(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', mi)
    slots = [s.material.name for s in o.material_slots]
    ti = slots.index('RC.v12.trunk')
    tv = sorted({v for p in me.polygons if p.material_index == ti for v in p.vertices})
    T = W[tv]; zmin, zmax = T[:,2].min(), T[:,2].max()
    bot = T[T[:,2] < zmin + 0.05].mean(0); top = T[T[:,2] > zmax - 0.05].mean(0)
    lean = math.degrees(math.atan2(np.linalg.norm((top-bot)[:2]), (top-bot)[2]))
    fol = W[np.setdiff1d(np.arange(len(W)), tv)]
    # base samples
    base = W[W[:,2] < W[:,2].min() + 0.05]
    gaps = []; sup = []
    for p in base[::max(1, len(base)//16)]:
        hit, loc, nor, fi, ob, _ = sc.ray_cast(dg, Vector((p[0], p[1], p[2] + 0.5)), Vector((0,0,-1)))
        # skip self
        while hit and ob is not None and ob.original == o:
            hit, loc, nor, fi, ob, _ = sc.ray_cast(dg, loc + Vector((0,0,-1e-4)), Vector((0,0,-1)))
        if hit: gaps.append(round(p[2] - loc.z, 3)); sup.append(ob.original.name)
    pines[o.name] = {'loc': list(o.location), 'rot_z': o.rotation_euler.z, 'scale': list(o.scale), 'lean_deg': round(lean, 2),
                     'trunk_bot': bot.round(3).tolist(), 'trunk_top': top.round(3).tolist(), 'zmin': round(float(W[:,2].min()),3),
                     'gaps': gaps, 'support': sorted(set(sup)), 'data': me.name,
                     'crown_w': round(float(max(np.ptp(fol[:,0]), np.ptp(fol[:,1]))), 3), 'crown_c': fol.mean(0).round(3).tolist(),
                     'base_pt': [round(float(v),1) for v in S.project([bot])[0]]}
rep['pines'] = pines
json.dump(rep, open(out, 'w'), indent=0)
print('ok')
