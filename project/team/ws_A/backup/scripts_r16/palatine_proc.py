"""R7 팔라티노 언덕 궁전 유적 — 절차 제작(Meshy 스캔이 지저분해 교체)
계단식 언덕 3단 + 카메라 쪽 두 면(+x, -y)에 아치 기초(어두운 아치 구멍) + 위에 무너진 궁전 벽·기둥 + 앞쪽 계단.
화면 상자 (340, 1000, 404, 1100)에 맞춤(강 오른쪽 둑 밖, CORE ③ 배지 왼쪽).
Blender에서: exec(open(<이 파일>).read())
"""
import math
import bpy
import bmesh
import numpy as np
from mathutils import Vector

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_A/'
U = bpy.data.texts['asset_utils.py'].as_module()
exec(open(ROOT + 'scripts/assets/place.py').read())
rng = np.random.default_rng(9)
bm = bmesh.new()
cols = []          # (면 묶음, 회색) — 나중에 재질 대신 오브젝트 둘로 나눔
dark = bmesh.new()


def box(b, cx, cy, z0, sx, sy, sz):
    r = bmesh.ops.create_cube(b, size=1.0)
    for v in r['verts']:
        v.co = Vector((cx + v.co.x * sx, cy + v.co.y * sy, z0 + (v.co.z + 0.5) * sz))


def arch_hole(cx, cy, z0, w, h, normal):
    """면 바로 앞에 어두운 아치 모양 판(직사각 + 반원). normal: (1,0) 또는 (0,-1)"""
    n = 10
    pts = [(-w / 2, 0), (w / 2, 0), (w / 2, h - w / 2)]
    for k in range(1, n):
        a = math.pi * k / n
        pts.append((w / 2 * math.cos(a), h - w / 2 + w / 2 * math.sin(a)))
    pts.append((-w / 2, h - w / 2))
    vs = []
    for (t, z) in pts:
        if normal == (1, 0):
            vs.append(dark.verts.new((cx + 0.012, cy + t, z0 + z)))
        else:
            vs.append(dark.verts.new((cx + t, cy - 0.012, z0 + z)))
    dark.faces.new(vs)


# 언덕 3단 (뒤로 갈수록 작고 높게)
TER = [(0.0, 0.0, 0.0, 6.0, 5.0, 0.9), (-0.5, 0.45, 0.9, 4.8, 3.9, 0.8), (-0.9, 0.85, 1.7, 3.4, 2.7, 0.7)]
for (cx, cy, z0, sx, sy, sz) in TER:
    box(bm, cx, cy, z0, sx, sy, sz)
    # 앞면(+x)과 왼쪽 앞면(-y)에 아치 줄
    for face in ((1, 0), (0, -1)):
        length = sy if face == (1, 0) else sx
        k = max(3, int(length / 0.6))
        for i in range(k):
            t = -length / 2 + (i + 0.5) * length / k
            if face == (1, 0):
                arch_hole(cx + sx / 2, cy + t, z0 + 0.12, 0.34, sz * 0.62, face)
            else:
                arch_hole(cx + t, cy - sy / 2, z0 + 0.12, 0.34, sz * 0.62, face)
# 위: 무너진 궁전(벽 조각·기둥)
top = 2.4
walls = [(-1.4, 0.4, 1.6, 0.18, 1.1), (-0.6, 1.4, 0.18, 1.4, 0.9), (-1.6, 1.6, 0.18, 1.0, 1.3), (-0.3, 0.3, 0.9, 0.18, 0.7)]
for (cx, cy, sx, sy, h) in walls:
    box(bm, cx, cy, top, sx, sy, h)
for i in range(6):
    x = -1.9 + i * 0.32
    r = bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.07, radius2=0.07, depth=0.9 if i % 3 else 0.55)
    for v in r['verts']:
        v.co += Vector((x, -0.15, top + (0.45 if i % 3 else 0.275)))
# 앞쪽 계단(-y 쪽 가운데)
for k in range(6):
    box(bm, 0.6, -2.5 - 0.0, k * 0.15, 1.2, 0.5 - k * 0.07, 0.15)
# 메시 두 개(흰 몸체, 어두운 아치)
U.remove_obj('L04_palatine_new'); U.remove_obj('L04_palatine_arch')
me = bpy.data.meshes.new('L04_palatine_new'); bm.to_mesh(me); bm.free()
md = bpy.data.meshes.new('L04_palatine_arch'); dark.to_mesh(md); dark.free()
body = bpy.data.objects.new('L04_palatine_new', me); holes = bpy.data.objects.new('L04_palatine_arch', md)
REG = bpy.data.collections['40_REGION']
REG.objects.link(body); REG.objects.link(holes)
holes.parent = body
body.color = (1, 1, 1, 1); holes.color = (0.38, 0.38, 0.38, 1)
for o in (body, holes):
    for p in o.data.polygons:
        p.use_smooth = False
m = body.modifiers.new('bv', 'BEVEL'); m.width = 0.03; m.segments = 1; m.limit_method = 'ANGLE'
old = bpy.data.objects.get('L04_palatine')
if old:
    bpy.data.objects.remove(old, do_unlink=True)
body.name = 'L04_palatine'
body.location = U.pt_to_world(372, 1090, 0)


def fit_with_child(ob, box_):
    for _ in range(5):
        bpy.context.view_layer.update()
        g = U.screen_bbox([ob, holes], 1)
        s = min((box_[2] - box_[0]) / (g[2] - g[0]), (box_[3] - box_[1]) / (g[3] - g[1]))
        ob.scale = ob.scale * s
        bpy.context.view_layer.update()
        g = U.screen_bbox([ob, holes], 1)
        du = (box_[0] + box_[2]) / 2 - (g[0] + g[2]) / 2; dv = box_[3] - g[3]
        base = U.pt_to_world((g[0] + g[2]) / 2, g[3], 0); mv = U.pt_to_world((g[0] + g[2]) / 2 + du, g[3] + dv, 0)
        ob.location = ob.location + (mv - base)
    bpy.context.view_layer.update()
    return [round(x, 1) for x in U.screen_bbox([ob, holes], 1)]


print('palatine', fit_with_child(body, (340, 1000, 404, 1100)), U.tri_count(body) + U.tri_count(holes))
