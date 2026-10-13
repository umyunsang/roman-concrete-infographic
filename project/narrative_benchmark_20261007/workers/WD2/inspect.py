"""WD2 inspection: dump my objects + neighbours (read-only). Run: Blender -b in.blend --factory-startup --python inspect.py -- out.json"""
import bpy, sys, json, math
import numpy as np
from mathutils import Vector
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts, Terrain, need

out = sys.argv[sys.argv.index('--') + 1]
S = Screen()
land = need('T_land'); T = Terrain(land)
MINE = ['L09_portus_lighthouse', 'L09_portus_mole', 'L12_harbor_pilae', 'NB_marine_breakwater', 'L11_privernum_wall',
        'C5_researchers', 'L08_pompeii_site', 'T_cypress', 'R_via_ostiensis', 'R_roadgeo_ostiensis_junction_fill']
MINE += sorted(o.name for o in bpy.data.objects if o.name.startswith('T_pine'))
EXTRA = ['L10_sea', 'W_water_marks', 'S_pin_harbor', 'S_pin_harbor_dot', 'T_land']
rep = {'scene': {'camera': S.cam.name, 'cam_type': S.cam.data.type, 'res': [bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y],
                 'engine': bpy.context.scene.render.engine}}
for n in MINE + EXTRA + [o.name for o in bpy.data.objects if 'harbor' in o.name.lower() or 'portus' in o.name.lower() or 'ostien' in o.name.lower() or 'sea' in o.name.lower()]:
    o = bpy.data.objects.get(n)
    if o is None or n in rep:
        continue
    d = {'type': o.type, 'loc': list(o.location), 'rot': [math.degrees(a) for a in o.rotation_euler], 'scale': list(o.scale),
         'parent': o.parent.name if o.parent else None, 'colls': [c.name for c in o.users_collection],
         'hide_render': o.hide_render, 'mods': [(m.type, m.name) for m in o.modifiers],
         'children': [c.name for c in o.children]}
    if o.type == 'MESH':
        W = world_verts(o)
        d['data'] = o.data.name; d['data_users'] = o.data.users; d['nv'] = len(o.data.vertices); d['nf'] = len(o.data.polygons)
        d['wmin'] = W.min(0).round(3).tolist(); d['wmax'] = W.max(0).round(3).tolist()
        P = S.project(W); d['pt_bbox'] = [round(P[:, 0].min(), 1), round(P[:, 0].max(), 1), round(P[:, 1].min(), 1), round(P[:, 1].max(), 1)]
        d['mats'] = []
        idx = np.zeros(len(o.data.polygons), np.int32); o.data.polygons.foreach_get('material_index', idx)
        for i, s in enumerate(o.material_slots):
            m = s.material
            d['mats'].append({'slot': i, 'name': m.name if m else None, 'link': s.link, 'faces': int((idx == i).sum()),
                              'users': m.users if m else 0,
                              'diffuse': [round(c, 4) for c in m.diffuse_color] if m else None})
        c = W.mean(0)
        d['terrain_z_at_center'] = round(T.z(c[0], c[1]), 3)
        d['wpp_at_center'] = round(S.world_per_pt(Vector(c)), 4)
    rep[n] = d
# who uses which material among mine
mats = {}
for o in bpy.data.objects:
    for s in o.material_slots:
        if s.material:
            mats.setdefault(s.material.name, set()).add(o.name)
rep['material_users'] = {m: sorted(v) for m, v in mats.items() if any(n in v for n in MINE)}
rep['collections'] = {c.name: {'hide_render': c.hide_render, 'n': len(c.objects)} for c in bpy.data.collections}
cam = S.cam
rep['camera'] = {'loc': list(cam.location), 'rot': [math.degrees(a) for a in cam.rotation_euler], 'ortho_scale': cam.data.ortho_scale,
                 'dir': list(cam.matrix_world.col[2].xyz)}
json.dump(rep, open(out, 'w'), indent=1, ensure_ascii=False, default=str)
print('WROTE', out)
