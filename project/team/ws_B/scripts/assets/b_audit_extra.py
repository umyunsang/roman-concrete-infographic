"""워커 B 추가 감사: audit_v7이 이름으로만 보는 배경 물체 밖의 새 물체(R_*_curb/_bed/_chev, F_crops/F_hedges/F_villa_*, B_pons*_pave, 나무)의
꼭짓점이 글 상자(+2pt, 지명·라벨·SUPPORT·DETAIL·CORE)에 들어가는지 + 물체 수·삼각형 합계."""
import json
import bpy
import numpy as np
U = bpy.data.texts['asset_utils.py'].as_module()
T = json.load(open('/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_B/loop/figma_texts.json'))
names = [o.name for o in bpy.data.objects if o.type == 'MESH' and (o.name.startswith(('R_', 'F_', 'B_pons', 'L01_', 'S_lab_island_rock', 'D2_kiln_smoke', 'L03_forum_vesta_roof', 'L04_palatine')) or o.name.startswith('T_') and o.users_collection and o.users_collection[0].name == '60_TREES')]
hits = 0
for n in names:
    q = U.project_pts(U.eval_world_coords(bpy.data.objects[n], 1))
    for t in T:
        if t['kind'] not in ('place', 'label', 'support', 'detail', 'core') and not n.startswith('L01_'):
            continue
        x0, y0, x1, y1 = t['b']
        k = int(((q[:, 0] > x0 - 2) & (q[:, 0] < x1 + 2) & (q[:, 1] > y0 - 2) & (q[:, 1] < y1 + 2)).sum())
        if k:
            hits += 1; print('EXTRA 글 상자 침범', n, t['c'][:12], k)
tot = 0
for c in bpy.data.collections:
    if c.hide_render or c.name.startswith('70_'):
        continue
    for o in c.objects:
        if o.type == 'MESH' and not o.hide_render:
            tot += U.tri_count(o)
big = sorted([(U.tri_count(o), o.name) for o in bpy.data.objects if o.type == 'MESH' and not o.hide_render], reverse=True)[:3]
print('EXTRA 합계: 추가 침범', hits, '| 장면 삼각형', tot, '| 가장 큰 물체', big)
