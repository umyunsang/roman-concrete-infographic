"""워커 A — 팔라티노 언덕 궁전 유적 재제작(비평 7: C1 '계단 피라미드(지구라트)처럼 보인다').
계단식 상자 3단 → 자연스러운 둥근 언덕(매끈한 음영) + 카메라 쪽 비탈에 2층 아치 기초벽(Domus Severiana 하부 구조)
+ 언덕 위 무너진 궁전: 방 벽(높이 들쭉날쭉)·반원 벽감(exedra)·열주 기둥 그루터기·창 아치가 뚫린 높은 벽 조각.
어두운 아치 구멍은 자식 물체 L04_palatine_arch(0.38)로(Workbench 회색 방식).
기존 두 물체의 화면 상자에 그대로 맞춤(물체 자리 이동 금지).
Blender에서: exec(open(<이 파일>).read())
"""
import math
import bpy
import bmesh
import numpy as np
from mathutils import Vector, noise

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_A/'
U = bpy.data.texts['asset_utils.py'].as_module()
rng = np.random.default_rng(23)

old = [o for o in (bpy.data.objects.get('L04_palatine'), bpy.data.objects.get('L04_palatine_arch')) if o]
bpy.context.view_layer.update()
BOX = U.screen_bbox(old, 1) if old else (339, 1105, 404, 1170)
print('palatine old bbox', [round(x, 1) for x in BOX])

hill = bmesh.new(); body = bmesh.new(); dark = bmesh.new()

# ---- 1. 언덕: 아치 옹벽(+x, -y 면) 뒤쪽만 흙 언덕 — 뒤·왼쪽으로 부드럽게 내려가는 비탈(매끈한 음영) ----
XF = 2.15            # +x 쪽 벽 면
YF = -1.85           # -y 쪽 벽 면
RX, RY, HT = 3.4, 3.1, 1.3
CX, CY = -0.2, 0.2
NR, NA = 16, 56
grid = []
for i in range(NR + 1):
    t = i / NR
    ring = []
    for j in range(NA):
        a = 2 * math.pi * j / NA
        x, y = CX + RX * t * math.cos(a), CY + RY * t * math.sin(a)
        prof = 1.0 if t < 0.5 else max(0.0, math.cos((t - 0.5) / 0.5 * math.pi / 2)) ** 1.3
        n = noise.noise(Vector((x * 0.8, y * 0.8, 3.3))) * 0.16 * min(1.0, 2 * t)
        z = HT * prof + (n if 0.3 < t < 0.97 else 0.0)
        # 옹벽 앞(카메라 쪽)은 흙 없음 — 벽 두께 안(0.3 뒤)에서 잘라 벽이 단면을 가림
        if x > XF - 0.85:
            z = -0.2
        if i == NR:
            z = -0.15
        ring.append(hill.verts.new((x, y, z)))
    grid.append(ring)
c0 = hill.verts.new((CX, CY, HT))
for j in range(NA):
    hill.faces.new((c0, grid[1][j], grid[1][(j + 1) % NA]))
for i in range(1, NR):
    for j in range(NA):
        hill.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][(j + 1) % NA], grid[i][(j + 1) % NA]))
TOP = HT


def box(b, cx, cy, z0, sx, sy, sz, rot=0.0):
    r = bmesh.ops.create_cube(b, size=1.0)
    ca, sa = math.cos(rot), math.sin(rot)
    for v in r['verts']:
        x, y = v.co.x * sx, v.co.y * sy
        v.co = Vector((cx + x * ca - y * sa, cy + x * sa + y * ca, z0 + (v.co.z + 0.5) * sz))


def prism_x(b, x0, x1, poly):
    """x0~x1 두께, poly: (y, z) 윤곽 → x 방향으로 세운 판(아치 벽)"""
    f = [b.verts.new((x0, y, z)) for y, z in poly]
    k = [b.verts.new((x1, y, z)) for y, z in poly]
    b.faces.new(list(reversed(f))); b.faces.new(k)
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        b.faces.new((f[i], f[j], k[j], k[i]))


def prism_y(b, y0, y1, poly):
    """y0~y1 두께, poly: (x, z) 윤곽"""
    f = [b.verts.new((x, y0, z)) for x, z in poly]
    k = [b.verts.new((x, y1, z)) for x, z in poly]
    b.faces.new(f); b.faces.new(list(reversed(k)))
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        b.faces.new((f[i], k[i], k[j], f[j]))


def arch_profile(a0, a1, z0, h, m=8):
    """폭 a0~a1, 바닥 z0, 아치 꼭대기 z0+h 인 구멍 윤곽(직사각+반원)"""
    w = a1 - a0; r = w / 2; c = (a0 + a1) / 2; zs = z0 + h - r
    return [(a0, z0), (a1, z0), (a1, zs)] + [(c + r * math.cos(t), zs + r * math.sin(t)) for t in np.linspace(0, math.pi, m)[1:-1]] + [(a0, zs)]


def arcade_x(b, xf, y0, y1, z0, z1, n, depth, tier_h):
    """x = xf 면(카메라 쪽 +x)에 아치 벽: n칸, 층 높이 tier_h — 기둥·아치 사이 벽을 조각 프리즘으로"""
    w = (y1 - y0) / n; pier = w * 0.28
    for k in range(n):
        a0 = y0 + k * w + pier / 2; a1 = y0 + (k + 1) * w - pier / 2
        r = (a1 - a0) / 2; zs = z0 + tier_h * 0.78 - r
        # 기둥(왼쪽)
        prism_x(b, xf - depth, xf, [(y0 + k * w - (pier / 2 if k else 0), z0), (a0, z0), (a0, z1), (y0 + k * w - (pier / 2 if k else 0), z1)])
        # 아치 위 벽(스팬드럴): 아치 윗선 ~ z1
        arc = [(a0 + r - r * math.cos(t), zs + r * math.sin(t)) for t in np.linspace(0, math.pi, 9)]
        prism_x(b, xf - depth, xf, arc + [(a1, z1), (a0, z1)])
        # 어두운 구멍(벽 안쪽 판)
        hole = [dark.verts.new((xf - 0.09, y, z)) for y, z in reversed(arch_profile(a0, a1, z0, tier_h * 0.78))]
        dark.faces.new(hole)
    prism_x(b, xf - depth, xf, [(y1 - pier / 2, z0), (y1, z0), (y1, z1), (y1 - pier / 2, z1)])


def arcade_y(b, yf, x0, x1, z0, z1, n, depth, tier_h):
    """y = yf 면(카메라 쪽 -y)"""
    w = (x1 - x0) / n; pier = w * 0.28
    for k in range(n):
        a0 = x0 + k * w + pier / 2; a1 = x0 + (k + 1) * w - pier / 2
        r = (a1 - a0) / 2; zs = z0 + tier_h * 0.78 - r
        prism_y(b, yf, yf + depth, [(x0 + k * w - (pier / 2 if k else 0), z0), (a0, z0), (a0, z1), (x0 + k * w - (pier / 2 if k else 0), z1)])
        arc = [(a0 + r - r * math.cos(t), zs + r * math.sin(t)) for t in np.linspace(0, math.pi, 9)]
        prism_y(b, yf, yf + depth, arc + [(a1, z1), (a0, z1)])
        hole = [dark.verts.new((x, yf + 0.09, z)) for x, z in arch_profile(a0, a1, z0, tier_h * 0.78)]
        dark.faces.new(hole)
    prism_y(b, yf, yf + depth, [(x1 - pier / 2, z0), (x1, z0), (x1, z1), (x1 - pier / 2, z1)])


# ---- 2. 아치 옹벽(2층, Domus Severiana 하부 구조) — 언덕 +x 비탈을 깎아 세운 벽 ----
T1 = 0.7
arcade_x(body, XF, -2.0, 1.7, 0.0, T1, 6, 0.55, T1)
arcade_x(body, XF - 0.22, -1.7, 1.4, T1, HT + 0.05, 5, 0.32, HT + 0.05 - T1)
box(body, XF - 0.06, -0.15, T1, 0.24, 3.7, 0.06)            # 1층 위 띠
box(body, XF - 0.36, -0.15, HT + 0.05, 0.4, 3.1, 0.07)      # 2층 위 처마
# 옹벽 양 끝 마구리(비탈 속으로)
for yy in (-2.0, 1.7):
    box(body, XF - 0.6, yy, 0.0, 1.2, 0.2, T1 * (0.9 if yy > 0 else 1.0))
PL = HT
# ---- 3. 언덕 위 무너진 궁전 ----
Z0 = PL


def wall(x0, y0, x1, y1, h, th=0.16, broken=True):
    L = math.hypot(x1 - x0, y1 - y0); rot = math.atan2(y1 - y0, x1 - x0)
    n = max(2, int(L / 0.35))
    for k in range(n):
        t = (k + 0.5) / n
        hh = h * (0.45 + 0.55 * abs(noise.noise(Vector((x0 + t * 3.1, y0 + t * 2.3, 7.7)))) * 1.6) if broken else h
        hh = min(h, max(0.18, hh))
        box(body, x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, Z0 - 0.3, L / n + 0.01, th, hh + 0.3, rot)


# 방들(직사각 방 격자) — 뒤쪽은 높게, 앞쪽은 낮게 무너짐
wall(-1.5, -1.1, 1.45, -1.1, 0.5)
wall(-1.5, 0.15, 1.45, 0.15, 0.72)
wall(-1.5, 1.3, 1.1, 1.3, 0.95)
wall(-1.5, -1.1, -1.5, 1.3, 0.85)
wall(-0.45, -1.1, -0.45, 1.3, 0.68)
wall(0.55, -1.1, 0.55, 0.15, 0.48)
# 반원 벽감(exedra) — 앞쪽 방 가운데, 카메라를 봄
for k in range(9):
    a = math.pi * (0.5 + k / 8)
    box(body, 0.95 + 0.5 * math.cos(a + math.pi / 2), 0.8 + 0.5 * math.sin(a + math.pi / 2), Z0 - 0.2, 0.22, 0.13, 0.82, a)
# 열주(peristyle) 기둥 그루터기 — 안뜰 둘레
for (x, y) in [(-0.25 + 0.3 * k, -0.85) for k in range(5)] + [(-0.25 + 0.3 * k, -0.1) for k in range(5)]:
    hh = 0.25 + 0.45 * rng.random()
    r = bmesh.ops.create_cone(body, cap_ends=True, segments=8, radius1=0.065, radius2=0.06, depth=hh)
    for v in r['verts']:
        v.co += Vector((x, y, Z0 - 0.1 + hh / 2))
# 높이 남은 벽 조각(창 아치 2개) — 뒤쪽 실루엣
prism_y(body, 1.22, 1.4, [(-1.5, Z0 - 0.3), (0.2, Z0 - 0.3), (0.2, Z0 + 1.1), (-0.2, Z0 + 1.4), (-0.8, Z0 + 1.55), (-1.5, Z0 + 1.25)])
for a0, a1 in ((-1.25, -0.9), (-0.6, -0.25)):
    hole = [dark.verts.new((x, 1.215, z)) for x, z in arch_profile(a0, a1, Z0 + 0.55, 0.62)]
    dark.faces.new(hole)
# ---- 물체로 ----
for nm in ('L04_palatine', 'L04_palatine_arch', 'L04_palatine_hill'):
    U.remove_obj(nm)
bmesh.ops.remove_doubles(body, verts=body.verts, dist=1e-5)
bmesh.ops.recalc_face_normals(body, faces=body.faces)
for b_ in (hill, body):
    pass
me_b = bpy.data.meshes.new('L04_palatine'); body.to_mesh(me_b); body.free()
me_h = bpy.data.meshes.new('L04_palatine_hill'); hill.to_mesh(me_h); hill.free()
me_d = bpy.data.meshes.new('L04_palatine_arch'); dark.to_mesh(me_d); dark.free()
# 언덕은 몸체에 합침(같은 물체 → 이음 윤곽선 없음), 매끈 음영은 면별로
bm = bmesh.new(); bm.from_mesh(me_b); nb = len(bm.faces)
bm.from_mesh(me_h)
bm.to_mesh(me_b); bm.free()
for i, p in enumerate(me_b.polygons):
    p.use_smooth = i >= nb
bpy.data.meshes.remove(me_h)
REG = bpy.data.collections['40_REGION']
ob = bpy.data.objects.new('L04_palatine', me_b); holes = bpy.data.objects.new('L04_palatine_arch', me_d)
REG.objects.link(ob); REG.objects.link(holes)
holes.parent = ob
ob.color = (0.84, 0.84, 0.84, 1); holes.color = (0.30, 0.30, 0.30, 1)
for p in me_d.polygons:
    p.use_smooth = False
cu, cv = (BOX[0] + BOX[2]) / 2, BOX[3] - 6
ob.location = U.pt_to_world(cu, cv, 0)
ob.rotation_euler = (0, 0, 0)


def fit(ob, box_):
    for _ in range(6):
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


print('palatine new bbox', fit(ob, BOX), 'tris', U.tri_count(ob) + U.tri_count(holes))
