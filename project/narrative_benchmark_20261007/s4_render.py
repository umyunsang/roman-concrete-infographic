import bpy, json, math, runpy, sys, time, os
import numpy as np
from mathutils import Vector
T0 = time.time()
BASE = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/'
g = runpy.run_path(BASE + 'nb_work/workers/inventory/inventory.py')
render_visible = g['render_visible']; OVL = g['OVERLAY_COLLECTIONS']
OUT = BASE + 'opb2/sub/'; os.makedirs(OUT, exist_ok=True)
IDX = json.load(open(BASE + 'nb_work/review_loop/obj_r11/assets_index.json'))
ASSET = {a['id']: a for a in IDX['assets']}
sc = bpy.context.scene; r = sc.render
print('engine', r.engine, 'res', r.resolution_x, r.resolution_y, r.resolution_percentage, 'shadows', sc.display.shading.show_shadows, 'light', sc.display.shading.light)
saved = {c.name: c.hide_render for c in bpy.data.collections}
for c in bpy.data.collections:
    if c.name in OVL: c.hide_render = True
r.resolution_percentage = 72
r.use_border = True; r.use_crop_to_border = True
r.image_settings.file_format = 'PNG'; r.image_settings.color_mode = 'RGBA'
W, H = 1191.0, 1684.0
jobs = {'landmark_colosseum': ['COL_ruined', 'R3_colosseum_podium', 'R4_arena_skin'], 'landmark_pantheon': ['R8_pantheon'],
        'bridge_north': ['B_pons1', 'B_pons1_parapet0', 'B_pons1_parapet1'], 'bridge_south': ['B_pons2', 'B_pons2_parapet0', 'B_pons2_parapet1', 'R4_bridge_west_bed'],
        'milestone_1_to_2': ['MS1_core1_to_2'], 'milestone_2_to_34': ['MS2_core2_to_34'], 'milestone_34_to_5': ['MS3_core34_to_5']}
meta = {}
for aid, objs in jobs.items():
    c = ASSET[aid]['crop_pt']
    r.border_min_x = c[0] / W; r.border_max_x = c[1] / W
    r.border_min_y = 1 - c[3] / H; r.border_max_y = 1 - c[2] / H
    for tag, hide in (('with', False), ('without', True)):
        st = {n: bpy.data.objects[n].hide_render for n in objs}
        for n in objs: bpy.data.objects[n].hide_render = hide or st[n]
        r.filepath = OUT + f'{aid}_{tag}.png'
        bpy.ops.render.render(write_still=True)
        for n in objs: bpy.data.objects[n].hide_render = st[n]
    meta[aid] = {'crop_pt': c}
    print(aid, round(time.time() - T0, 1))
for c in bpy.data.collections: c.hide_render = saved[c.name]
json.dump(meta, open(OUT + 'meta.json', 'w'))
print('DONE', round(time.time() - T0, 1))
