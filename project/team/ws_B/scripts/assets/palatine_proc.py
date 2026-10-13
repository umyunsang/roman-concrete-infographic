"""워커 B · 비평 7: 팔라티노 언덕 궁전 유적 — '계단 피라미드(지구라트)'처럼 보이던 3단 상자를 버리고 절차 제작으로 다시.
- 자연 언덕(둥근 평정 구릉, 가장자리 잡음) — 단 없음
- 카메라 쪽(+x) 면: 언덕을 받치는 세베루스 하부 구조 = 높은 옹벽 + 2층 아치(어두운 아치 구멍)
- 언덕 위: 도미티아누스 궁전(Domus Flavia/Augustana) 방들의 무너진 벽(높이 제각각, 윗단 들쭉날쭉), 열주 안마당(기둥 고리),
  긴 경기장 정원(Stadium Palatinum: 긴 네모 + 한쪽 반원 끝, 낮은 담) — 로마 궁전 유적으로 읽히게
몸체(흰 0.95) + 아치 구멍(자식, 0.36). 화면 자리는 원래와 같음(339~401 × 1110~1170, 바닥 맞춤).
Blender에서: exec(open(<이 파일>).read())
"""
import math
import bpy
import bmesh
import numpy as np
from mathutils import Vector

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_B/'
U = bpy.data.texts['asset_utils.py'].as_module()
rng = np.random.default_rng(17)
bm = bmesh.new()
dark = bmesh.new()
hb = bmesh.new()      # 언덕(풀밭 흙, 한 단계 어둡게)
pb = bmesh.new()      # 언덕 위 우산소나무(팔라티노의 상징)
HILL_H = 1.0
XW = 2.35            # +x 옹벽 위치(언덕 가운데 부분만 여기서 수직으로 자름)


def box(b, cx, cy, z0, sx, sy, sz, rot=0.0):
    r = bmesh.ops.create_cube(b, size=1.0)
    c, s = math.cos(rot), math.sin(rot)
    for v in r['verts']:
        x, y = v.co.x * sx, v.co.y * sy
        v.co = Vector((cx + x * c - y * s, cy + x * s + y * c, z0 + (v.co.z + 0.5) * sz))


def cyl(b, cx, cy, z0, r, h, seg=10):
    res = bmesh.ops.create_cone(b, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=h)
    for v in res['verts']:
        v.co += Vector((cx, cy, z0 + h / 2))


def hill_z(x, y):
    """둥근 평정 구릉: 초타원 반지름 r(4제곱) → 평정 + 완만한 비탈, 가장자리 잡음. +x는 옹벽에서 수직으로 끊김."""
    ang = math.atan2(y, x)
    wob = 1 + 0.07 * math.sin(3 * ang + 0.6) + 0.05 * math.sin(5 * ang + 2.1) + 0.03 * math.sin(9 * ang)
    rx, ry = 3.35 * wob, 2.9 * wob
    r = ((abs(x) / rx) ** 2.6 + (abs(y) / ry) ** 2.6) ** (1 / 2.6)
    t = min(1.0, max(0.0, (1.02 - r) / 0.5))
    z = HILL_H * t * t * (3 - 2 * t)
    z += 0.05 * math.sin(2.3 * x + 1.0) * math.sin(1.9 * y + 0.4) * t
    if x > XW and -1.55 < y < 1.55:
        z = 0.0
    return z


# 1) 언덕(격자 메시)
N = 64
xs = np.linspace(-3.6, 3.6, N); ys = np.linspace(-3.3, 3.3, N)
vid = {}
for i, x in enumerate(xs):
    for j, y in enumerate(ys):
        vid[i, j] = hb.verts.new((x, y, hill_z(x, y) - 0.04))
for i in range(N - 1):
    for j in range(N - 1):
        zs = [vid[a, b_].co.z for a, b_ in ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))]
        if max(zs) > -0.03:
            hb.faces.new((vid[i, j], vid[i + 1, j], vid[i + 1, j + 1], vid[i, j + 1]))
for v in [v for v in hb.verts if not v.link_faces]:
    hb.verts.remove(v)

# 2) +x 옹벽(세베루스 하부 구조) + 2층 아치 구멍
y_lo, y_hi = -1.55, 1.55
box(bm, XW + 0.02, 0.0, -0.05, 0.34, y_hi - y_lo, HILL_H + 0.17)
box(bm, XW + 0.06, 0.0, HILL_H + 0.1, 0.42, y_hi - y_lo + 0.1, 0.07)       # 처마 띠
for k in range(2):                                                            # 버팀 기둥(옹벽 양 끝)
    box(bm, XW + 0.06, (y_lo if k == 0 else y_hi), -0.05, 0.42, 0.3, HILL_H + 0.2)


def arch_hole(cx, cy, z0, w, h, normal):
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


n_ar = 5
for tier, (z0, h, w) in enumerate(((0.04, 0.52, 0.4), (0.62, 0.34, 0.34))):
    for k in range(n_ar):
        y = y_lo + 0.32 + k * (y_hi - y_lo - 0.64) / (n_ar - 1)
        if tier == 1 and k in (3,):
            continue                              # 위층 몇 칸은 무너짐
        arch_hole(XW + 0.19, y, z0, w, h, (1, 0))
# 옹벽 위 무너진 윗단(들쭉날쭉)
for k in range(7):
    y = y_lo + 0.2 + k * (y_hi - y_lo - 0.4) / 6
    box(bm, XW + 0.02, y, HILL_H + 0.17, 0.3, 0.3, rng.uniform(0.03, 0.2))

# 3) 언덕 위: 궁전 방들의 무너진 벽(평정 위 z = HILL_H)
TOP = HILL_H - 0.03


def ruin_wall(x0, y0, x1, y1, hmax, thick=0.13):
    L = math.hypot(x1 - x0, y1 - y0); n = max(2, int(L / 0.28)); rot = math.atan2(y1 - y0, x1 - x0)
    for k in range(n):
        t = (k + 0.5) / n
        if rng.random() < 0.1:
            continue                              # 무너진 틈
        h = hmax * (0.45 + 0.55 * abs(math.sin(3.1 * t + x0))) * rng.uniform(0.75, 1.05)
        box(bm, x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, TOP, L / n + 0.01, thick, h, rot)


# 궁전(Domus Augustana 쪽): 방 격자 — 일부 벽 없음
gx = [-1.6, -0.95, -0.3, 0.35, 1.0, 1.65]
gy = [0.15, 0.72, 1.3, 1.85]
for i in range(len(gx)):
    for j in range(len(gy) - 1):
        if rng.random() < 0.78:
            ruin_wall(gx[i], gy[j], gx[i], gy[j + 1], 0.5 if i in (0, 5) else 0.36)
for j in range(len(gy)):
    for i in range(len(gx) - 1):
        if rng.random() < 0.78 or j in (0, 3):
            ruin_wall(gx[i], gy[j], gx[i + 1], gy[j], 0.48 if j == 3 else 0.34)
# 방 하나 안 아치 문(어두운 구멍, 카메라 쪽 -y 면)
for x in (-1.37, 0.57):
    box(bm, x, 0.15, TOP, 0.62, 0.16, 0.62)
    arch_hole(x, 0.15 - 0.08, TOP + 0.02, 0.24, 0.42, (0, -1))
# 열주 안마당(peristyle): 기둥 고리 + 가운데 낮은 연못 테
cxp, cyp = -0.75, 1.05
for k in range(12):
    a = 2 * math.pi * k / 12
    hh = 0.62 if k % 4 else 0.3                   # 몇 기둥은 부러짐
    cyl(bm, cxp + 0.62 * math.cos(a), cyp + 0.42 * math.sin(a), TOP, 0.055, hh, 8)
box(bm, cxp, cyp, TOP, 0.55, 0.3, 0.06)
# 경기장 정원(Stadium Palatinum): 긴 네모 + 서쪽 반원 끝, 낮은 담 + 안쪽 기둥 줄
sx0, sx1, sy0, sy1 = -1.55, 1.55, -1.75, -0.75
ruin_wall(sx0, sy0, sx1, sy0, 0.32, 0.12)
ruin_wall(sx0, sy1, sx1, sy1, 0.42, 0.12)
ruin_wall(sx1, sy0, sx1, sy1, 0.5, 0.12)
rc = (sy1 - sy0) / 2; ccy = (sy0 + sy1) / 2
for k in range(9):
    a0 = math.pi / 2 + math.pi * k / 9; a1 = math.pi / 2 + math.pi * (k + 1) / 9
    ruin_wall(sx0 + rc * math.cos(a0), ccy + rc * math.sin(a0), sx0 + rc * math.cos(a1), ccy + rc * math.sin(a1), 0.4, 0.12)
for k in range(9):
    x = sx0 + 0.15 + k * (sx1 - sx0 - 0.3) / 8
    cyl(bm, x, sy0 + 0.17, TOP, 0.045, 0.34 if k % 3 else 0.18, 8)
    cyl(bm, x, sy1 - 0.17, TOP, 0.045, 0.34 if k % 2 else 0.2, 8)
box(bm, -0.05, ccy, TOP - 0.01, 1.6, 0.28, 0.05)          # 가운데 화단 테
# 언덕 비탈·뒤쪽의 우산소나무 몇 그루(줄기 + 납작한 우산 수관)
for (px, py, sc_) in ((-2.3, 1.4, 1.0), (-2.6, -0.4, 0.85), (-1.2, 2.35, 0.9), (0.6, 2.45, 0.8)):
    pz = hill_z(px, py) - 0.05
    cyl(pb, px, py, pz, 0.05 * sc_, 0.95 * sc_, 6)
    res = bmesh.ops.create_icosphere(pb, subdivisions=2, radius=1.0)
    for v in res['verts']:
        q = v.co.copy()
        v.co = Vector((px + q.x * 0.55 * sc_ * (1 + 0.1 * math.sin(5 * q.y)), py + q.y * 0.5 * sc_, pz + 0.95 * sc_ + q.z * 0.2 * sc_))
# 메시 둘(흰 몸체, 어두운 아치)
U.remove_obj('L04_palatine_new'); U.remove_obj('L04_palatine_arch'); U.remove_obj('L04_palatine_hill'); U.remove_obj('L04_palatine_pines')
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
me = bpy.data.meshes.new('L04_palatine_new'); bm.to_mesh(me); bm.free()
md = bpy.data.meshes.new('L04_palatine_arch'); dark.to_mesh(md); dark.free()
body = bpy.data.objects.new('L04_palatine_new', me); holes = bpy.data.objects.new('L04_palatine_arch', md)
REG = bpy.data.collections['40_REGION']
REG.objects.link(body); REG.objects.link(holes)
holes.parent = body
body.color = (0.95, 0.95, 0.95, 1); holes.color = (0.3, 0.3, 0.3, 1)
mh = bpy.data.meshes.new('L04_palatine_hill'); hb.to_mesh(mh); hb.free()
mp = bpy.data.meshes.new('L04_palatine_pines'); pb.to_mesh(mp); pb.free()
hill = bpy.data.objects.new('L04_palatine_hill', mh); pines = bpy.data.objects.new('L04_palatine_pines', mp)
REG.objects.link(hill); REG.objects.link(pines)
hill.parent = body; pines.parent = body
hill.color = (0.9, 0.9, 0.9, 1); pines.color = (0.62, 0.62, 0.62, 1)
for p in hill.data.polygons:
    p.use_smooth = True
for o in (body, holes, pines):
    for p in o.data.polygons:
        p.use_smooth = False
old = bpy.data.objects.get('L04_palatine')
OLD_BOX = (338.8, 1109.5, 401.3, 1170.0)   # r16 팔라티노 화면 상자(자리 고정)
if old:
    bpy.data.objects.remove(old, do_unlink=True)
body.name = 'L04_palatine'; holes.name = 'L04_palatine_arch'
body.location = U.pt_to_world((OLD_BOX[0] + OLD_BOX[2]) / 2, OLD_BOX[3] - 10, 0)
body.rotation_euler = (0, 0, 0)


def fit_with_child(ob, box_):
    for _ in range(6):
        bpy.context.view_layer.update()
        g = U.screen_bbox([ob, holes, hill, pines], 1)
        s = min((box_[2] - box_[0]) / (g[2] - g[0]), (box_[3] - box_[1]) / (g[3] - g[1]))
        ob.scale = ob.scale * s
        bpy.context.view_layer.update()
        g = U.screen_bbox([ob, holes, hill, pines], 1)
        du = (box_[0] + box_[2]) / 2 - (g[0] + g[2]) / 2; dv = box_[3] - g[3]
        base = U.pt_to_world((g[0] + g[2]) / 2, g[3], 0); mv = U.pt_to_world((g[0] + g[2]) / 2 + du, g[3] + dv, 0)
        ob.location = ob.location + (mv - base)
    bpy.context.view_layer.update()
    return [round(x, 1) for x in U.screen_bbox([ob, holes, hill, pines], 1)]


print('palatine old box', [round(x, 1) for x in OLD_BOX], 'new', fit_with_child(body, OLD_BOX), 'tris', U.tri_count(body) + U.tri_count(holes) + U.tri_count(hill) + U.tri_count(pines))
