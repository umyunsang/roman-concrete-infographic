import bpy, sys, json, numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, Terrain, need, world_verts
S = Screen()
out = {}
for n in ('MS1_core1_to_2','MS2_core2_to_34','MS3_core34_to_5'):
    o = bpy.data.objects[n]; me = o.data
    co = np.array([v.co[:] for v in me.vertices])
    slots = [(s.material.name if s.material else None, s.link) for s in o.material_slots]
    pm = np.array([p.material_index for p in me.polygons])
    parts = {}
    for k in range(len(slots)):
        vs = sorted({v for p in me.polygons if p.material_index == k for v in p.vertices})
        if vs:
            c = co[vs]; parts[k] = {'n_v': len(vs), 'n_f': int((pm==k).sum()), 'min': c.min(0).round(3).tolist(), 'max': c.max(0).round(3).tolist()}
    W = world_verts(o); P = S.project(W)
    out[n] = {'mesh': me.name, 'users': me.users, 'nv': len(me.vertices), 'nf': len(me.polygons), 'loc': list(o.location), 'rot': list(o.rotation_euler), 'scale': list(o.scale),
              'parent': o.parent.name if o.parent else None, 'colls': [c.name for c in o.users_collection], 'slots': slots, 'parts': parts,
              'screen_box': [P[:,0].min(), P[:,0].max(), P[:,1].min(), P[:,1].max()], 'modifiers': [m.type for m in o.modifiers]}
    for s in o.material_slots:
        if s.material:
            m = s.material
            users = [ob.name for ob in bpy.data.objects if any(ss.material == m for ss in ob.material_slots)]
            bs = next((nd for nd in m.node_tree.nodes if nd.type=='BSDF_PRINCIPLED'), None) if m.use_nodes else None
            out.setdefault('materials', {})[m.name] = {'users': users, 'diffuse': list(m.diffuse_color), 'bsdf': list(bs.inputs[0].default_value) if bs else None, 'nodes':[nd.type for nd in m.node_tree.nodes] if m.use_nodes else None}
# pantheon
for n in [o.name for o in bpy.data.objects if 'pantheon' in o.name.lower()]:
    o = bpy.data.objects[n]; W = world_verts(o); P = S.project(W)
    out.setdefault('pantheon', {})[n] = {'zmin': W[:,2].min(), 'zmax': W[:,2].max(), 'box': [P[:,0].min(), P[:,0].max(), P[:,1].min(), P[:,1].max()], 'loc': list(o.location), 'scale': list(o.scale)}
print('JSON', json.dumps(out, default=float))
