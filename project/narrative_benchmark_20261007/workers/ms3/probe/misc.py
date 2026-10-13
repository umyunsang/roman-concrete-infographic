import bpy, sys
import numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts, Terrain, need, map_visible_objects, overlay_objects, screen_tris
S = Screen()
w = need('W_water_marks'); W = world_verts(w); P = S.project(W)
m = (P[:,0] > 650) & (P[:,0] < 1050) & (P[:,1] > 820) & (P[:,1] < 1080)
T = Terrain(need('T_land'))
print('W_water_marks verts in roi', m.sum(), 'mats', [s.material.name for s in w.material_slots])
if m.any():
    rel = np.array([p[2]-T.z(p[0],p[1]) for p in W[m]]); print('z rel terrain', rel.min(), rel.max(), 'pts', P[m][:10].round(1))
# non-mesh renderables
vl = bpy.context.view_layer
def walk(lc, hidden, out):
    c = lc.collection; h = hidden or lc.exclude or c.hide_render
    for o in c.objects:
        if not h and not o.hide_render and o.type not in ('MESH', 'CAMERA', 'LIGHT', 'EMPTY'): out.append((o.name, o.type, c.name))
    for ch in lc.children: walk(ch, h, out)
out = []; walk(vl.layer_collection, False, out); print('non-mesh renderables', out)
ms = need('MS3_core34_to_5'); print('MS3 modifiers', [m.type for m in ms.modifiers], 'parent', ms.parent, 'constraints', list(ms.constraints), 'anim', ms.animation_data)
print('rotation mode', ms.rotation_mode, 'delta', ms.delta_location[:], ms.delta_rotation_euler[:], ms.delta_scale[:])
print('MS3 matrix', [list(r) for r in ms.matrix_world])
print('MS2 users', ms.data.users, [o.name for o in bpy.data.objects if o.data == ms.data])
print('render engine', bpy.context.scene.render.engine, bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y)
