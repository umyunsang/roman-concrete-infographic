"""워커 B: 석회 가마 꼭대기 연기(Meshy 덩어리, z>6.35)가 땅 그림자까지 드리운 '꼭대기 조각상'처럼 읽힘(블라인드 심사)
→ 그 부분을 지우고, 그림자 없는 2번째 패스(81_NOSHADOW)에 밝은 회색 연기 뭉치 셋(위로 갈수록 크고 옅게)."""
import math
import bpy
import bmesh
import numpy as np
from mathutils import Vector
U = bpy.data.texts['asset_utils.py'].as_module()
o = bpy.data.objects['D2_lime_kiln']
if not o.get('b_smoke_cut'):
    bm = bmesh.new(); bm.from_mesh(o.data)
    M = o.matrix_world
    kill = [v for v in bm.verts if (M @ v.co).z > 6.35]
    bmesh.ops.delete(bm, geom=kill, context='VERTS')
    bm.to_mesh(o.data); bm.free(); o.data.update()
    o['b_smoke_cut'] = True
    print('kiln smoke verts removed', len(kill))
P = U.eval_world_coords(o, 1)
top = P[P[:, 2] > P[:, 2].max() - 0.4]
cx, cy, cz = top[:, 0].mean(), top[:, 1].mean(), P[:, 2].max()
U.remove_obj('D2_kiln_smoke')
if not int(__import__('os').environ.get('B_SMOKE', '0')):
    print('kiln smoke: none (연기 뭉치는 애벌레·눈사람처럼 읽혀 뺌 — 가마 꼭대기 구멍만)')
else:
    bm = bmesh.new()
    rng = np.random.default_rng(4)
    for k, (dx, dy, dz, r) in enumerate(((0.0, 0.0, 0.35, 0.34), (0.05, 0.12, 0.75, 0.42), (0.05, 0.3, 1.15, 0.5), (-0.05, 0.55, 1.5, 0.56), (-0.25, 0.85, 1.8, 0.6), (-0.5, 1.2, 2.0, 0.58))):   # 이어진 연기 줄기(바람에 살짝 흐름)
        res = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
        for v in res['verts']:
            p = v.co.copy()
            n = 1 + 0.1 * math.sin(3 * p.x + k) * math.sin(2 * p.y + 1.3 * k)
            v.co = Vector((cx + dx + p.x * r * n, cy + dy + p.y * r * n * 0.85, cz + dz + p.z * r * 0.62 * n))
    me = bpy.data.meshes.new('D2_kiln_smoke'); bm.to_mesh(me); bm.free()
    sm = bpy.data.objects.new('D2_kiln_smoke', me)
    U.coll('81_NOSHADOW').objects.link(sm)
    sm.color = (0.95, 0.95, 0.95, 1)
    for p in me.polygons:
        p.use_smooth = True
    bb = U.screen_bbox(sm, 1)
    print('smoke screen', [round(x, 1) for x in bb])
    import json
    for t in json.load(open('/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_B/loop/figma_texts.json')):
        b = t['b']
        if not (bb[2] < b[0] - 2 or b[2] < bb[0] - 2 or bb[3] < b[1] - 2 or b[3] < bb[1] - 2):
            print('SMOKE TEXT HIT', t['c'][:10])
