"""(비교 시험 A) Figma 최종 v6의 CORE·DETAIL·SUPPORT 글을 Blender 3D 글로 배치 (14:58 사용자: "블렌더로 할지 오버레이로 할지 보자")
- 떠 있는 글: 카메라를 향한 세로 평면(카메라와 같은 회전) — 글 덩어리 아랫변 아래 땅 깊이에 세움, 화면 pt 크기 그대로 맞춤
- CORE 번호: 검은 원판 + 흰 숫자, 밑줄: 얇은 판
- 지명: 땅에 눕힘(rot 30 → 세계 Y축 방향, -30 → 세계 X축 방향)
- 색: Workbench 색 방식 OBJECT — 글 검정·회색, 나머지 흰색
컬렉션 70_LABELS_TEST (지우면 원래대로). Blender에서: exec(open(<이 파일>).read())
"""
import json
import math
import bpy
import numpy as np
from mathutils import Vector, Matrix

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_B/'
U = bpy.data.texts['asset_utils.py'].as_module()
T = json.load(open(ROOT + 'assets/figma_text_v6.json'))
FONT_B = bpy.data.fonts.load('/Users/um-yunsang/Library/Fonts/NotoSansCJKkr-Bold.otf', check_existing=True)
FONT_R = bpy.data.fonts.load('/Users/um-yunsang/Library/Fonts/NotoSansCJKkr-Regular.otf', check_existing=True)
D = np.load(ROOT + 'assets/terrain_hf.npz')
HG = D['h'].astype(np.float64); G0 = float(D['u'][0, 0]); GS = float(D['u'][1, 0] - D['u'][0, 0])
COL = {'black': (0.07, 0.07, 0.07, 1), 'gray': (0.25, 0.25, 0.25, 1), 'white': (1, 1, 1, 1)}

C = U.coll('70_LABELS_TEST')
for o in list(C.objects):
    bpy.data.objects.remove(o, do_unlink=True)
cam = bpy.data.objects['CAM_iso']
CAM_ROT = cam.matrix_world.to_3x3().normalized()
RIGHT = CAM_ROT @ Vector((1, 0, 0)); UP = CAM_ROT @ Vector((0, 1, 0)); TOWARD = CAM_ROT @ Vector((0, 0, 1))


def h_uv(u, v):
    fi = (u - G0) / GS; fj = (v - G0) / GS
    i0 = int(np.clip(math.floor(fi), 0, HG.shape[0] - 2)); j0 = int(np.clip(math.floor(fj), 0, HG.shape[1] - 2))
    a = min(max(fi - i0, 0), 1); b = min(max(fj - j0, 0), 1)
    return (HG[i0, j0] * (1 - a) + HG[i0 + 1, j0] * a) * (1 - b) + (HG[i0, j0 + 1] * (1 - a) + HG[i0 + 1, j0 + 1] * a) * b


def make_text(name, body, bold, size_world):
    cu = bpy.data.curves.new(name, 'FONT')
    cu.body = body
    cu.font = FONT_B if bold else FONT_R
    cu.font_bold = FONT_B
    cu.size = size_world
    cu.space_line = 1.12
    cu.align_x = 'LEFT'
    cu.fill_mode = 'BOTH'
    ob = bpy.data.objects.new(name, cu)
    C.objects.link(ob)
    return ob


def fit_in_plane(ob, x, y, scale):
    """화면 상자 왼쪽 위가 (x, y)에 오도록, 카메라 평면 안에서 옮김."""
    for _ in range(2):
        bpy.context.view_layer.update()
        bb = U.screen_bbox(ob, 1)
        du, dv = x - bb[0], y - bb[1]
        ob.location = ob.location + RIGHT * (du / scale) - UP * (dv / scale)


def standing(item):
    x, y, w, h = item['x'], item['y'], item['w'], item['h']
    vb = y + h + 2.0                                        # 글 아랫변 바로 아래 땅에 세움
    g = Vector(U.pt_to_world(x, vb, 0.0))
    g.z = h_uv(x, vb)
    scale = float(U.rise_per_unit(np.array([[x, vb]]))[0])   # 이 깊이에서 1단위 = scale pt (세로 평면은 가로도 같음)
    ob = make_text('L_' + item['id'], item['t'], item['b'], item['s'] / scale)
    ob.rotation_euler = cam.rotation_euler.copy()
    ob.location = g + TOWARD * 0.02
    ob.color = COL[item.get('c', 'black')]
    # Blender가 CJK OTF를 em의 약 1/3로 읽음 → Figma 글 상자 너비에 맞춰 배율 보정
    bpy.context.view_layer.update()
    bb = U.screen_bbox(ob, 1)
    k = w / max(1e-6, bb[2] - bb[0])
    ob.scale = (k, k, k)
    fit_in_plane(ob, x, y, scale)
    return ob, scale


def disc(name, cu, cv, r_pt, scale, z_ref_loc):
    me = bpy.data.meshes.new(name)
    n = 24
    verts = [(0, 0, 0)] + [(math.cos(2 * math.pi * k / n) * r_pt / scale, math.sin(2 * math.pi * k / n) * r_pt / scale, 0) for k in range(n)]
    faces = [(0, k + 1, (k + 1) % n + 1) for k in range(n)]
    me.from_pydata(verts, [], faces)
    ob = bpy.data.objects.new(name, me); C.objects.link(ob)
    ob.rotation_euler = cam.rotation_euler.copy()
    ob.location = z_ref_loc
    ob.color = COL['black']
    bpy.context.view_layer.update()
    bb = U.screen_bbox(ob, 1)
    du, dv = cu - (bb[0] + bb[2]) / 2, cv - (bb[1] + bb[3]) / 2
    ob.location = ob.location + RIGHT * (du / scale) - UP * (dv / scale) - TOWARD * 0.01
    return ob


def underline(name, x0, yv, x1, scale, ref_loc):
    me = bpy.data.meshes.new(name)
    L = (x1 - x0) / scale; t = 0.9 / scale
    me.from_pydata([(0, 0, 0), (L, 0, 0), (L, t, 0), (0, t, 0)], [], [(0, 1, 2, 3)])
    ob = bpy.data.objects.new(name, me); C.objects.link(ob)
    ob.rotation_euler = cam.rotation_euler.copy(); ob.location = ref_loc
    ob.color = COL['black']
    bpy.context.view_layer.update()
    bb = U.screen_bbox(ob, 1)
    ob.location = ob.location + RIGHT * ((x0 - bb[0]) / scale) - UP * ((yv - bb[1]) / scale)
    return ob


def lying(item):
    """지명: 땅에 눕힌 글. rot 30 → 세계 +Y 방향으로 읽힘, -30 → 세계 +X 방향, 0 → 떠 있는 글."""
    if item.get('rot', 0) == 0:
        return standing(item)[0]
    cu_, cv_ = item['x'] + item['w'] / 2, item['y'] + item['h'] / 2
    g = Vector(U.pt_to_world(cu_, cv_, 0.0)); g.z = h_uv(cu_, cv_) + 0.12
    s_ground = float(U.rise_per_unit(np.array([[cu_, cv_]]))[0]) * 0.82   # 땅 위 가로 축척 근사
    ob = make_text('L_' + item['id'], item['t'], item['b'], item['s'] / s_ground)
    ob.data.align_x = 'CENTER'; ob.data.align_y = 'CENTER'
    ob.rotation_euler = (0, 0, math.radians(90 if item['rot'] > 0 else 0))
    ob.location = g
    ob.color = COL['black']
    bpy.context.view_layer.update()
    bb = U.screen_bbox(ob, 1)
    diag_fig = math.hypot(item['w'], item['h']); diag_now = math.hypot(bb[2] - bb[0], bb[3] - bb[1])
    k = diag_fig / max(1e-6, diag_now)
    ob.scale = (k, k, k)
    return ob


made = []
for it in T:
    if it['g'] == 'PLACE':
        made.append(lying(it)); continue
    ob, scale = standing(it)
    made.append(ob)
    if it.get('badge'):
        ob.location = ob.location + TOWARD * 0.03
        made.append(disc('L_' + it['id'] + '_badge', it['x'] + it['w'] / 2, it['y'] + it['h'] / 2, 9.0, scale, ob.location.copy()))
    if it.get('ul'):
        x0, yv, x1 = it['ul']
        made.append(underline('L_' + it['id'] + '_ul', x0, yv, x1, scale, ob.location.copy()))

# 색 방식: OBJECT (글 검정, 나머지 기본 흰색)
sc = bpy.context.scene
sc.display.shading.color_type = 'OBJECT'
for o in bpy.data.objects:
    if o.type in ('MESH',) and o.users_collection and o.users_collection[0].name != '70_LABELS_TEST':
        o.color = (1, 1, 1, 1)
print('labels', len(made))
