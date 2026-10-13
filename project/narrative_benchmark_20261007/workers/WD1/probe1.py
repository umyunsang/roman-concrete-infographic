import bpy, sys, json, numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts
S = Screen()
OWN = ['COL_ruined', 'R3_colosseum_podium', 'R4_arena_skin', 'R8_pantheon', 'D2_lime_kiln', 'L05_aqua_claudia', 'L07_vesuvius', 'L08_pompeii']
OWN += [o.name for o in bpy.data.objects if o.name.startswith('L01_')]
mat_users = {}
for o in bpy.data.objects:
    if o.type == 'MESH':
        for s in o.material_slots:
            if s.material:
                mat_users.setdefault(s.material.name, set()).add(o.name)
out = {}
for n in OWN:
    o = bpy.data.objects[n]
    W = world_verts(o)
    P = S.project(W)
    me = o.data
    mi = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', mi)
    cnt = np.bincount(mi, minlength=len(o.material_slots))
    mats = []
    for i, s in enumerate(o.material_slots):
        m = s.material
        col = None
        if m:
            col = list(m.diffuse_color)
        mats.append({'slot': i, 'mat': m.name if m else None, 'faces': int(cnt[i]) if i < len(cnt) else 0,
                     'diffuse': [round(c, 4) for c in col] if col else None,
                     'other_users': sorted(mat_users.get(m.name, set()) - {n}) if m else []})
    out[n] = {'loc': list(o.location), 'rot': [round(np.degrees(a), 3) for a in o.rotation_euler], 'scale': list(o.scale),
              'parent': o.parent.name if o.parent else None,
              'collections': [c.name for c in o.users_collection],
              'verts': len(me.vertices), 'faces': len(me.polygons), 'mesh_users': me.users,
              'world_min': W.min(0).round(3).tolist(), 'world_max': W.max(0).round(3).tolist(),
              'screen_box': [round(float(P[:, 0].min()), 1), round(float(P[:, 0].max()), 1), round(float(P[:, 1].min()), 1), round(float(P[:, 1].max()), 1)],
              'modifiers': [(m.name, m.type) for m in o.modifiers], 'mats': mats,
              'shade_smooth_frac': float(np.mean([p.use_smooth for p in me.polygons])) if len(me.polygons) < 400000 else None}
sh = bpy.context.scene.display.shading
out['_shading'] = {k: str(getattr(sh, k)) for k in ['light', 'color_type', 'show_cavity', 'cavity_type', 'cavity_ridge_factor', 'cavity_valley_factor', 'curvature_ridge_factor', 'curvature_valley_factor', 'show_shadows', 'shadow_intensity', 'studio_light', 'show_specular_highlight']}
out['_engine'] = bpy.context.scene.render.engine
out['_res'] = [bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y, bpy.context.scene.render.resolution_percentage]
out['_cam'] = {'loc': list(S.cam.location), 'rot': [round(np.degrees(a), 4) for a in S.cam.rotation_euler], 'type': S.cam.data.type, 'ortho': S.cam.data.ortho_scale}
out['_collections'] = {c.name: [c.hide_render, len(c.objects)] for c in bpy.data.collections}
print('JSON' + json.dumps(out))
