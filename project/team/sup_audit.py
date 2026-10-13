"""감독 독립 감사: 장면의 모든 렌더 메시(땅·바다·강·카메라 앞 도형 제외)의 화면 꼭짓점이 Figma 글 상자 안에 들어가는지.
blender -b <ws>/roman_concrete_map.blend --python team/sup_audit.py   (저장 안 함)
"""
import json, bpy, numpy as np
U = bpy.data.texts['asset_utils.py'].as_module()
T = json.load(open('/Users/um-yunsang/Documents/로마콘크리트_3D/loop/figma_texts.json'))
SKIP_COLL = {'80_SHAPES', '81_NOSHADOW', '85_HEADER'}
SKIP_OBJ = {'T_land', 'L10_sea', 'L02_tiber'}
PAD = 1.5
hits = []; n = 0; tris = 0
for o in bpy.context.scene.objects:
    if o.type != 'MESH' or o.hide_render or not o.visible_get():
        continue
    tris += sum(len(p.vertices) - 2 for p in o.data.polygons)
    if o.name in SKIP_OBJ or any(c.name in SKIP_COLL for c in o.users_collection):
        continue
    n += 1
    step = 1 if len(o.data.vertices) < 150000 else 3
    q = U.project_pts(U.eval_world_coords(o, step))
    for t in T:
        if t['kind'] == 'title':
            continue
        x0, y0, x1, y1 = t['b']
        k = int(((q[:, 0] > x0 - PAD) & (q[:, 0] < x1 + PAD) & (q[:, 1] > y0 - PAD) & (q[:, 1] < y1 + PAD)).sum())
        if k:
            hits.append((t['kind'], t['c'][:18], o.name, [c.name for c in o.users_collection][0], k))
ob = []
for o in bpy.context.scene.objects:
    if o.type == 'MESH' and not o.hide_render and o.visible_get() and o.name not in SKIP_OBJ and not any(c.name in SKIP_COLL for c in o.users_collection):
        bb = U.screen_bbox([o], 1 if len(o.data.vertices) < 150000 else 3)
        if bb[0] < -2 or bb[1] < -2 or bb[2] > 1193 or bb[3] > 1686:
            ob.append((o.name, [round(v) for v in bb]))
for h in hits:
    print('SUP_HIT', h)
for x in ob:
    print('SUP_OUT', x)
print('SUP_SUMMARY objects', n, 'hits', len(hits), 'outside', len(ob), 'tris', tris)
