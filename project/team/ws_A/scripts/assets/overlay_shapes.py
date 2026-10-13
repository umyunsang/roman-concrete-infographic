"""Figma v7의 글이 아닌 평면 도형을 Blender로 (15:26 사용자: 오버레이는 글만, 도형·다이어그램·이미지는 Blender)
- 떠 있는 도형(카메라 앞 평면, 아무것에도 가려지지 않음): CORE 번호 원판·제목 밑줄, SUPPORT 점선 핀·끝점, DETAIL 지시선·③ 단면 도식, 연표 자·점·화살촉
- 땅에 칠한 도형: CORE 읽는 순서 점선 길(콜로세움 둘레, 콜로세움에 가려지는 부분은 가려짐)
좌표는 Figma 634:78에서 읽은 값(화면 pt). 컬렉션 80_SHAPES. Blender에서: exec(open(<이 파일>).read())
"""
import json
import math
import bpy
import numpy as np
from mathutils import Vector

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_A/'
U = bpy.data.texts['asset_utils.py'].as_module()
exec(open(ROOT + 'scripts/assets/shapes2d.py').read())
C = U.coll('80_SHAPES')
for o in list(C.objects):
    bpy.data.objects.remove(o, do_unlink=True)
cam, CP, FWD = _cam()
NEAR = CP + FWD * 150.0          # 카메라 앞 평면(장면 어느 것보다 가까움)
BLACK, DARK, MID = 0.07, 0.2, 0.45

# ---- CORE 번호 원판(지름 20) + 밑줄(0.8) ----
CORE = {1: ((528, 388.5), (528, 441.5, 660.5)), 2: ((69.5, 758.5), (69.5, 811.5, 213.6)),
        3: ((408.5, 1030.5), (408.5, 1083.5, 530.9)), 4: ((638.5, 1034.5), (638.5, 1087.5, 799.1)),   # 18:05 ③ -8, ④ -4
        5: ((982.5, 818.5), (982.5, 871.5, 1085.2))}   # 18:05 ⑤ -8
for k, ((bx, by), (ux, uy, ux1)) in CORE.items():
    disc('S_core%d_badge' % k, (bx + 10, by + 10), 10, NEAR, C, gray=BLACK, lift=0)
    line('S_core%d_underline' % k, [(ux, uy), (ux1, uy)], 0.8, NEAR, C, gray=BLACK, lift=0)

# ---- SUPPORT 점선 핀(1.0, 점선 3/3) + 끝점(지름 3.4) ----
PINS = {'harbor': ((240, 1533), (198, 1497)), 'lab': ((590, 1497.8), (590, 1536.9)),
        'pompeii': ((724, 1545), (724, 1482)), 'privernum': ((897, 1062), (1024, 1062))}
for k, (a, b) in PINS.items():
    dashed('S_pin_' + k, [a, b], 1.0, 3.0, 3.0, NEAR, C, gray=DARK, lift=0)
    disc('S_pin_' + k + '_dot', b, 1.7, NEAR, C, gray=DARK, n=16, lift=0)

# ---- DETAIL 지시선 + 끝점 ----
# R7: ① 라벨은 모형 왼쪽(원래 v6처럼) — 끝점은 모형에서 직접 계산
_cr = sorted([o for o in bpy.data.objects if o.name.startswith('D1_crystal')], key=lambda o: U.screen_bbox(o, 1)[0])
_c0 = U.screen_bbox(_cr[0], 1) if _cr else (100, 355, 104, 359)
_sw = U.screen_bbox(bpy.data.objects['D1_seawater'], 1) if bpy.data.objects.get('D1_seawater') else (62, 350, 143, 401)
D1A = ((_c0[0] + _c0[2]) / 2, (_c0[1] + _c0[3]) / 2); D1B = (_sw[0] + 9, (_sw[1] + _sw[3]) / 2 + 10)
LEAD = [((52, 347.5), D1A), ((61, 387.5), D1B),        # ① 새 결정·바닷물 속
        ((140, 1007), (128, 1007)),                                 # ② 석회 알갱이
        ((298.9, 1231.9), (315.8, 1231.9)), ((373.8, 1231.9), (390.7, 1231.9)),   # ③ 양방향 지시선
        ((300.8, 1258.5), (324.1, 1258.5)), ((365.1, 1258.5), (388.4, 1258.5)),
        ((303.4, 1287.0), (319.8, 1287.0)), ((369.8, 1287.0), (386.2, 1287.0)),
        ((309.5, 1308.0), (318.6, 1308.0)), ((375.6, 1308.0), (384.7, 1308.0))]
for i, (a, b) in enumerate(LEAD):
    line('S_lead%02d' % i, [a, b], 0.9, NEAR, C, gray=DARK, lift=0)
for i, p in enumerate([D1A, D1B, (128, 1007)]):
    disc('S_lead_dot%d' % i, p, 1.6, NEAR, C, gray=DARK, n=12, lift=0)
# ③ 단면 도식(회색 단계 사각형) + 땅 높이 선 + 벽돌 줄
SECT = [((390.7, 1221, 401.2, 1245), 0.9), ((388.4, 1245, 403.4, 1272), 0.7), ((386.2, 1272, 405.7, 1300.5), 0.5),
        ((384.7, 1300.5, 407.2, 1315.5), 0.3)]
for i, ((x0, y0, x1, y1), g) in enumerate(SECT):
    P = to_plane([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], NEAR)
    _mesh('S_sect%d' % i, P, [(0, 1, 2, 3)], C, g, 0)
    line('S_sect%d_edge' % i, [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], 0.6, NEAR, C, gray=DARK, lift=0)
line('S_sect_ground', [(382.4, 1300.5), (418.4, 1300.5)], 1.0, NEAR, C, gray=BLACK, lift=0)
for y in (1227, 1233, 1239):
    line('S_sect_brick%d' % y, [(390.7, y), (401.2, y)], 0.5, NEAR, C, gray=DARK, lift=0)
for i, p in enumerate([(390.7, 1231.9), (388.4, 1258.5), (386.2, 1287.0), (384.7, 1308.0)]):
    disc('S_sect_dot%d' % i, p, 1.7, NEAR, C, gray=DARK, n=12, lift=0)

# ---- 연표 자 + 화살촉 + 점 ----
line('S_time_rule', [(49.5, 1640.5), (802, 1640.5)], 1.0, NEAR, C, gray=BLACK, lift=0)
P = to_plane([(802, 1637), (809, 1640.5), (802, 1644)], NEAR)
_mesh('S_time_head', P, [(0, 1, 2)], C, BLACK, 0)
for i, x in enumerate((50, 168, 286, 404, 522, 640, 758)):
    disc('S_time_dot%d' % i, (x, 1640.5), 2.6, NEAR, C, gray=BLACK, n=16, lift=0)

# ---- CORE 읽는 순서 점선 길: Figma 경로(베지어)를 땅 위에 ----
OX, OY = 224.927, 626.0
SEGS = [[(370.07, 0), (260.70, 0), (156.94, 27.99), (86.64, 76.44)],
        [(86.64, 76.44), (-66.32, 181.87), (-9.92, 342.19), (202.10, 404.67)],
        [(312.19, 425.36), (343.70, 428.25), (375.72, 428.77), (407.46, 426.90)],
        [(524.10, 408.58), (655.69, 373.73), (740.07, 297.71), (740.07, 214.0)]]


def bez(P, n=40):
    P = np.array(P, float); t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 3 * P[0] + 3 * (1 - t) ** 2 * t * P[1] + 3 * (1 - t) * t ** 2 * P[2] + t ** 3 * P[3]


D = np.load(ROOT + 'assets/terrain_hf.npz'); G0 = float(D['u'][0, 0]); GS = float(D['u'][1, 0] - D['u'][0, 0]); HG = D['h']


def ground_pts(uv):
    """화면 pt → 그 화면 자리에 보이는 땅 위 점(땅 높이 반복 보정)"""
    out = []
    for u, v in uv:
        h = 0.0
        for _ in range(4):
            w = U.pt_to_world(u, v, h)
            q = U.project_pts(np.array([[w.x, w.y, 0.0]]))[0]
            i = int(np.clip(round((q[0] - G0) / GS), 0, HG.shape[0] - 1)); j = int(np.clip(round((q[1] - G0) / GS), 0, HG.shape[1] - 1))
            h = float(HG[i, j])
        out.append((w.x, w.y, h + 0.06))
    return np.array(out)


# 18:00 점선 읽는 순서 길 제거 → fill_plains의 R_ring(로마 포장 길)·R_pons(다리)로 대체
U.remove_obj('S_core_path')
print('shapes', len(C.objects))
