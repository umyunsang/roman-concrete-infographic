"""DETAIL 확대 모형 ①~④를 Blender 3D 오브젝트로 (Figma 최종 v6 도식을 3D로 옮김) — 평야 위, Figma 모형 자리에.
① 재료 원리: 바닷물 수조 속 콘크리트 큐브 + 면에서 자라는 흰 바늘 결정
② 제작 원리: 짙은 큐브에 박힌 흰 석회 알갱이 + 위로 오르는 열(물결 줄)
③ 구조 원리: 위로 갈수록 가볍고 작은 4단 벽(가벼운 벽돌·중간 돌·무거운 돌·기초 12m+) + 위에서 누르는 화살표 2개 + 지시선
④ 균열 원리: 큐브 3개(금 → 물이 스며 알갱이 녹음 → 흰 결정으로 메워짐) + 사이 화살표
회색 단계는 오브젝트 색(Workbench 색 방식 OBJECT, 나머지 오브젝트는 흰색). 컬렉션 50_DETAIL_MODEL.
Blender에서: exec(open(<이 파일>).read())
"""
import json
import math
import bpy
import bmesh
import numpy as np
from mathutils import Vector, Matrix

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/'
U = bpy.data.texts['asset_utils.py'].as_module()
exec(open(ROOT + 'scripts/assets/shapes2d.py').read())
C = U.coll('50_DETAIL_MODEL')
for o in list(C.objects):
    bpy.data.objects.remove(o, do_unlink=True)
rng = np.random.default_rng(3)
# 화면 위 = 세계 (-1,1)/√2, 화면 오른쪽 = (1,1)/√2 → 모형의 '앞면'이 카메라를 보게 z 회전 -45°(모서리 정면)
ROT = math.radians(0)


def box(name, size, loc, gray, parent, bevel=0.03, seg=2):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    ob = bpy.context.active_object; ob.name = name
    ob.scale = size; bpy.ops.object.transform_apply(scale=True)
    ob.location = loc
    if bevel:
        m = ob.modifiers.new('bv', 'BEVEL'); m.width = bevel; m.segments = seg
    _finish(ob, gray, parent)
    return ob


def _finish(ob, gray, parent):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    C.objects.link(ob)
    ob.parent = parent
    ob.color = (gray, gray, gray, 1)
    for p in ob.data.polygons:
        p.use_smooth = False


def empty(name):
    e = bpy.data.objects.new(name, None); C.objects.link(e); e.empty_display_size = 0.5
    return e


def kids(e):
    return [o for o in C.objects if o.parent == e and o.type == 'MESH']


def fit_group(e, want, iters=4):
    """빈 부모 e를 균일 축척·이동해 자식 메시 전체의 화면 상자를 want 안에(아래 맞춤)."""
    for _ in range(iters):
        bpy.context.view_layer.update()
        g = U.screen_bbox(kids(e), 1)
        s = min((want[2] - want[0]) / (g[2] - g[0]), (want[3] - want[1]) / (g[3] - g[1]))
        e.scale = e.scale * s
        bpy.context.view_layer.update()
        g = U.screen_bbox(kids(e), 1)
        du = (want[0] + want[2]) / 2 - (g[0] + g[2]) / 2; dv = want[3] - g[3]
        base = U.pt_to_world((g[0] + g[2]) / 2, g[3], 0); mv = U.pt_to_world((g[0] + g[2]) / 2 + du, g[3] + dv, 0)
        e.location = e.location + (mv - base)
    bpy.context.view_layer.update()
    return [round(x, 1) for x in U.screen_bbox(kids(e), 1)]


def ground_at(u, v):
    D = np.load(ROOT + 'assets/terrain_hf.npz'); G0 = float(D['u'][0, 0]); GS = float(D['u'][1, 0] - D['u'][0, 0])
    i = int(round((u - G0) / GS)); j = int(round((v - G0) / GS))
    return float(D['h'][i, j])


def crystal(name, base, direction, length, r, parent, gray=1.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=r, depth=length, location=(0, 0, 0))
    ob = bpy.context.active_object; ob.name = name
    bm = bmesh.new(); bm.from_mesh(ob.data)
    for v in bm.verts:
        if v.co.z > 0:
            v.co.x *= 0.15; v.co.y *= 0.15         # 뾰족한 바늘 결정
    bm.to_mesh(ob.data); bm.free()
    d = Vector(direction).normalized()
    ob.rotation_mode = 'QUATERNION'
    ob.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d)
    ob.location = Vector(base) + d * (length / 2)
    _finish(ob, gray, parent)
    return ob


def blob(name, loc, r, parent, gray=1.0, squash=1.0):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=r, location=loc)
    ob = bpy.context.active_object; ob.name = name; ob.scale = (1, 1, squash)
    _finish(ob, gray, parent)
    return ob


def crack_groove(name, face_center, normal, tangent, up, h, parent, gray=0.08, width=0.06, depth=0.04, zig=6):
    """큐브 면 위 지그재그 금: 얇은 띠(면에서 살짝 들어감)"""
    pts = []
    for k in range(zig + 1):
        t = k / zig
        off = (0.12 if k % 2 else -0.12) if 0 < k < zig else 0.0
        pts.append(Vector(face_center) + Vector(up) * (h * (t - 0.5)) + Vector(tangent) * off)
    bm = bmesh.new()
    n = Vector(normal)
    vs = []
    for p in pts:
        vs.append((bm.verts.new(p + Vector(tangent) * width / 2 + n * 0.005), bm.verts.new(p - Vector(tangent) * width / 2 + n * 0.005)))
    for (a1, b1), (a2, b2) in zip(vs[:-1], vs[1:]):
        bm.faces.new((a1, b1, b2, a2))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); C.objects.link(ob); ob.parent = parent
    ob.color = (gray, gray, gray, 1)
    return ob


Z = json.load(open(ROOT + 'sketch_v2/text_zones.json'))['objects']
res = {}

# ---------- ① 재료 원리 ----------
e1 = empty('D1_material')
box('D1_tank_floor', (2.4, 2.4, 0.12), (0, 0, 0.06), 0.85, e1)
for i, (sx, sy, lx, ly) in enumerate(((2.4, 0.12, 0, 1.14), (2.4, 0.12, 0, -1.14), (0.12, 2.4, 1.14, 0), (0.12, 2.4, -1.14, 0))):
    box('D1_tank_wall%d' % i, (sx, sy, 0.7), (lx, ly, 0.35), 0.85, e1, bevel=0.02)
water = box('D1_seawater', (2.16, 2.16, 0.5), (0, 0, 0.37), 0.62, e1, bevel=0)
cube = box('D1_concrete', (1.3, 1.3, 1.3), (0, 0, 0.12 + 0.65), 0.55, e1, bevel=0.05)
for k in range(26):
    face = rng.integers(0, 3)
    if face == 0:      # 윗면
        p = Vector((rng.uniform(-0.55, 0.55), rng.uniform(-0.55, 0.55), 1.42)); d = Vector((rng.normal(0, 0.25), rng.normal(0, 0.25), 1))
    elif face == 1:    # 카메라 쪽 앞면 (+x)
        p = Vector((0.66, rng.uniform(-0.55, 0.55), rng.uniform(0.75, 1.35))); d = Vector((1, rng.normal(0, 0.3), rng.normal(0.2, 0.3)))
    else:              # 카메라 쪽 다른 앞면 (-y)
        p = Vector((rng.uniform(-0.55, 0.55), -0.66, rng.uniform(0.75, 1.35))); d = Vector((rng.normal(0, 0.3), -1, rng.normal(0.2, 0.3)))
    crystal('D1_crystal%02d' % k, p, d, rng.uniform(0.22, 0.42), 0.05, e1)
res['D1'] = fit_group(e1, Z['D1_model'])

# ---------- ② 제작 원리 ----------
e2 = empty('D2_making')
box('D2_cube', (1.5, 1.5, 1.5), (0, 0, 0.75), 0.33, e2, bevel=0.05)
for k in range(16):
    face = k % 3
    if face == 0:
        loc = (rng.uniform(-0.6, 0.6), rng.uniform(-0.6, 0.6), 1.5)
    elif face == 1:
        loc = (0.75, rng.uniform(-0.6, 0.6), rng.uniform(0.15, 1.35))
    else:
        loc = (rng.uniform(-0.6, 0.6), -0.75, rng.uniform(0.15, 1.35))
    blob('D2_lime%02d' % k, loc, rng.uniform(0.07, 0.14), e2, gray=1.0, squash=0.7)
# 열: 위로 오르는 물결 줄 3개(가는 관)
for k, x in enumerate((-0.35, 0.05, 0.45)):
    pts = [Vector((x + 0.12 * math.sin(t * 2.2), -0.1 + x * 0.3, 1.75 + t * 0.32)) for t in np.linspace(0, 3.2, 24)]
    cu = bpy.data.curves.new('D2_heat%d' % k, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.025; cu.bevel_resolution = 1
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (p.x, p.y, p.z, 1)
    ob = bpy.data.objects.new('D2_heat%d' % k, cu); C.objects.link(ob); ob.parent = e2; ob.color = (0.25, 0.25, 0.25, 1)
res['D2'] = None   # 곡선은 screen_bbox 계산 전 메시로 바꿈
for o in [o for o in C.objects if o.parent == e2 and o.type == 'CURVE']:
    bpy.context.view_layer.objects.active = o
    with bpy.context.temp_override(object=o, active_object=o, selected_objects=[o], selected_editable_objects=[o]):
        bpy.ops.object.convert(target='MESH')
res['D2'] = fit_group(e2, Z['D2_model'])

# ---------- ③ 구조 원리 ----------
e3 = empty('D3_structure')
layers = [('D3_foundation', 1.9, 0.9, 0.22), ('D3_heavy', 1.6, 0.9, 0.42), ('D3_middle', 1.35, 0.9, 0.62), ('D3_light', 1.1, 0.95, 0.9)]
z = 0.0
tops = []
for name, w, h, g in layers:
    box(name, (w, w * 0.55, h), (0, 0, z + h / 2), g, e3, bevel=0.03)
    tops.append((name, z, h, w))
    z += h + 0.02
# 가벼운 벽돌 줄눈(가로 홈 3줄)
zl = tops[-1][1]
for k in range(1, 4):
    box('D3_brick_course%d' % k, (1.12, 1.1 * 0.55 + 0.02, 0.025), (0, 0, zl + k * 0.95 / 4), 0.6, e3, bevel=0)
# 위에서 누르는 화살표 2개(세운 막대 + 원뿔)
for k, x in enumerate((-0.25, 0.25)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.03, depth=0.7, location=(x, 0, z + 0.55))
    a = bpy.context.active_object; a.name = 'D3_press%d' % k; _finish(a, 0.08, e3)
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.09, radius2=0, depth=0.18, location=(x, 0, z + 0.12))
    c = bpy.context.active_object; c.name = 'D3_press_tip%d' % k; c.rotation_euler = (math.pi, 0, 0); _finish(c, 0.08, e3)
res['D3'] = fit_group(e3, [250, 1199, 317, 1337])

# ---------- ④ 균열 원리 ----------
e4 = empty('D4_crack')
xs = (-2.3, 0.0, 2.3)
# 큐브 3개를 화면 가로로 늘어놓기: 세계 방향 화면 오른쪽 = (1,1)/√2
R = Vector((1, 1, 0)).normalized()
for i, xx in enumerate(xs):
    c = R * xx
    box('D4_cube%d' % i, (1.2, 1.2, 1.2), (c.x, c.y, 0.6), 0.6, e4, bevel=0.04)
    # 카메라 쪽 앞면(+x 면) 금
    crack_groove('D4_crack%d' % i, (c.x + 0.6, c.y, 0.6), (1, 0, 0), (0, 1, 0), (0, 0, 1), 0.95, e4,
                 gray=(1.0 if i == 2 else 0.08), width=(0.08 if i == 2 else 0.06))
    if i < 2:   # 금 속 흰 석회 알갱이
        blob('D4_lime%d' % i, (c.x + 0.62, c.y + 0.05, 0.62), 0.11 if i == 0 else 0.08, e4, gray=1.0)
    if i == 1:  # 위에서 떨어지는 물방울
        for k, (dz, dy) in enumerate(((1.75, 0.1), (2.05, -0.05), (2.3, 0.15))):
            blob('D4_drop%d' % k, (c.x + 0.4, c.y + dy, dz), 0.06, e4, gray=0.35, squash=1.5)
# 사이 화살표(바닥 위 평평한 화살)
for i in range(2):
    a = R * (xs[i] + 0.8); b = R * (xs[i + 1] - 0.8)
    bm = bmesh.new()
    d = (b - a).normalized(); n = Vector((-d.y, d.x, 0))
    shaft_end = b - d * 0.25
    pts = [a + n * 0.05, shaft_end + n * 0.05, shaft_end + n * 0.16, b, shaft_end - n * 0.16, shaft_end - n * 0.05, a - n * 0.05]
    vs = [bm.verts.new((p.x, p.y, 0.62)) for p in pts]
    bm.faces.new(vs)
    me = bpy.data.meshes.new('D4_arrow%d' % i); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('D4_arrow%d' % i, me); C.objects.link(ob); ob.parent = e4; ob.color = (0.15, 0.15, 0.15, 1)
res['D4'] = fit_group(e4, Z['D4_model'])

# 땅 높이에 앉히기
for e, key in ((e1, 'D1_model'), (e2, 'D2_model'), (e3, None), (e4, 'D4_model')):
    g = U.screen_bbox(kids(e), 1)
    e.location.z = ground_at((g[0] + g[2]) / 2, g[3]) * 0.0

# 색 방식: OBJECT
bpy.context.scene.display.shading.color_type = 'OBJECT'
for win in bpy.context.window_manager.windows:
    for area in win.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.shading.color_type = 'OBJECT'
print(res)
