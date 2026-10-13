"""헤더(제목·BASIC) 도형을 Blender 3D로 (15:26 사용자: 오버레이는 글만)
- 제목 뒤 '세 아치 개선문'(Figma 347–845 × 19–235): 아치 3개가 뚫린 3D 개선문, 정면이 카메라를 봄(세워짐 → 위에서 30° 내려다봄)
- BASIC 왼쪽: 석회(흰 원뿔) + 화산재(짙은 원뿔) + 돌·벽돌 조각(작은 큐브 3개) → 틀에 부어 굳힘(나무 틀 상자 + 흰 알갱이)
- BASIC 오른쪽: 로마 때 기록(책 2권) · 오늘의 연구(시료 원통 + 돋보기) · 살펴볼 건물(콜로세움 축소 — 본체와 메시 공유)
모두 카메라 앞(깊이 150 근처)에 띄움 → 땅·산에 가리지 않음, 그림자 안 드리움. 컬렉션 85_HEADER.
Blender에서: exec(open(<이 파일>).read())
"""
import math
import bpy
import bmesh
import numpy as np
from mathutils import Vector, Matrix

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_A/'
U = bpy.data.texts['asset_utils.py'].as_module()
C = U.coll('85_HEADER')
for o in list(C.objects):
    bpy.data.objects.remove(o, do_unlink=True)
cam = bpy.data.objects['CAM_iso']
bpy.context.view_layer.update()
CP = cam.matrix_world.translation.copy()
FWD = (cam.matrix_world.to_3x3() @ Vector((0, 0, -1))).normalized()
TOWARD = Vector((-FWD.x, -FWD.y, 0)).normalized()          # 수평으로 카메라 쪽
YAW = math.atan2(TOWARD.y, TOWARD.x)                         # 오브젝트 정면(-Y)을 카메라 쪽으로 돌릴 각


def link(ob, gray):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    C.objects.link(ob)
    ob.color = (gray, gray, gray, 1)
    try:
        ob.visible_shadow = False
    except Exception:
        pass
    if ob.type == 'MESH':
        for p in ob.data.polygons:
            p.use_smooth = False
    return ob


def apply_mods(ob):
    for m in list(ob.modifiers):
        with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
            bpy.ops.object.modifier_apply(modifier=m.name)


def cube(name, size, loc, gray, bevel=0.02):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob = bpy.context.active_object; ob.name = name; ob.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        m = ob.modifiers.new('bv', 'BEVEL'); m.width = bevel; m.segments = 2
    return link(ob, gray)


def fit_near(objs, box, depth=150.0, iters=6):
    """objs(같은 부모 없이 함께 움직임)를 카메라 앞 depth 근처에서 화면 상자 box에 맞춤(균일 축척, 가운데 맞춤)."""
    piv = Vector(np.mean([np.array(o.location) for o in objs], axis=0))
    target = CP + FWD * depth
    for o in objs:
        o.location = o.location - piv + target
    piv = target.copy()
    m = cam.matrix_world.to_3x3()
    R, UPV = m @ Vector((1, 0, 0)), m @ Vector((0, 1, 0))
    for _ in range(iters):
        bpy.context.view_layer.update()
        g = U.screen_bbox(objs, 1)
        s = min((box[2] - box[0]) / (g[2] - g[0]), (box[3] - box[1]) / (g[3] - g[1]))
        for o in objs:
            o.location = piv + (o.location - piv) * s
            o.scale = o.scale * s
        bpy.context.view_layer.update()
        g = U.screen_bbox(objs, 1)
        du = (box[0] + box[2]) / 2 - (g[0] + g[2]) / 2; dv = (box[1] + box[3]) / 2 - (g[1] + g[3]) / 2
        # 이 깊이에서 1pt의 세계 길이
        a = U.pts_to_world(np.array([[600.0, 800.0]]), 0.0)[0]
        ppt = (depth * 2 * math.tan(cam.data.angle_y / 2)) / 1684.0 if cam.data.type == 'PERSP' else cam.data.ortho_scale / 1684.0
        mv = R * (du * ppt) - UPV * (dv * ppt)
        for o in objs:
            o.location = o.location + mv
        piv = piv + mv
    bpy.context.view_layer.update()
    return [round(x, 1) for x in U.screen_bbox(objs, 1)]


def face_camera(ob, extra=0.0):
    ob.rotation_euler = (0, 0, YAW + math.pi / 2 + extra)


out = {}
# ---------- 개선문 ----------
W, H, Dp = 10.0, 4.34, 1.1
gate = cube('H_gate_body', (W, Dp, H), (0, 0, H / 2), 0.93, bevel=0.03)
cutters = []
for (cx, w, h, spring) in ((-3.47, 1.6, 0.92, 0.3), (0.0, 3.2, 1.25, 0.55), (3.47, 1.6, 0.92, 0.3)):
    # 아랫단 안에 들어가는 활 모양 아치: 너비 w, 꼭대기 h, 홍예 시작 높이 spring
    sag = h - spring; r = (w * w / 4 + sag * sag) / (2 * sag); zc = h - r
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=r, depth=Dp * 3, location=(cx, 0, zc), rotation=(math.pi / 2, 0, 0))
    cyl = bpy.context.active_object
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, 0, spring / 2 - 0.05)); bx = bpy.context.active_object
    bx.scale = (w, Dp * 3, spring + 0.1); bpy.ops.object.transform_apply(scale=True)
    # 원기둥이 아치 너비 밖으로 넓게 깎지 않도록 너비 w 상자와 교집합
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, 0, (spring + h) / 2)); lim = bpy.context.active_object
    lim.scale = (w, Dp * 3.2, h - spring + 0.02); bpy.ops.object.transform_apply(scale=True)
    mi = cyl.modifiers.new('lim', 'BOOLEAN'); mi.operation = 'INTERSECT'; mi.object = lim; mi.solver = 'EXACT'
    with bpy.context.temp_override(object=cyl, active_object=cyl, selected_objects=[cyl]):
        bpy.ops.object.modifier_apply(modifier='lim')
    bpy.data.objects.remove(lim, do_unlink=True)
    cutters += [cyl, bx]
for ct in cutters:
    m = gate.modifiers.new('cut', 'BOOLEAN'); m.operation = 'DIFFERENCE'; m.object = ct; m.solver = 'EXACT'
    apply_mods(gate)
for ct in cutters:
    bpy.data.objects.remove(ct, do_unlink=True)
parts = [gate]
for z in (2.38, 1.46):        # 처마 띠 두 줄(앞으로 돌출)
    parts.append(cube('H_gate_cornice%d' % int(z * 100), (W + 0.2, Dp + 0.25, 0.13), (0, 0, z), 0.8, bevel=0.015))
parts.append(cube('H_gate_base', (W + 0.3, Dp + 0.35, 0.12), (0, 0, 0.06), 0.75, bevel=0.015))
for x in (-4.55, -2.45, 2.45, 4.55):  # 벽기둥(아랫단)
    parts.append(cube('H_gate_pilaster%d' % int(x * 10), (0.32, Dp + 0.14, 1.36), (x, 0, 0.7), 0.85, bevel=0.01))
parts.append(cube('H_gate_keystone', (0.42, Dp + 0.16, 0.36), (0, 0, 1.24), 0.7, bevel=0.01))
gempty = bpy.data.objects.new('H_gate', None); C.objects.link(gempty)
for p in parts:
    p.parent = gempty
face_camera(gempty)
out['gate'] = fit_near([gempty] + parts, (347, 19, 845, 235)) if False else None
# 부모를 움직이는 방식으로 맞춤
def fit_parent(e, box, depth=150.0):
    e.location = CP + FWD * depth
    m = cam.matrix_world.to_3x3(); R, UPV = m @ Vector((1, 0, 0)), m @ Vector((0, 1, 0))
    kids_ = [o for o in C.objects if o.parent == e and o.type == 'MESH']
    for _ in range(6):
        bpy.context.view_layer.update()
        g = U.screen_bbox(kids_, 1)
        s = min((box[2] - box[0]) / (g[2] - g[0]), (box[3] - box[1]) / (g[3] - g[1]))
        e.scale = e.scale * s
        bpy.context.view_layer.update()
        g = U.screen_bbox(kids_, 1)
        dep = (e.location - CP).dot(FWD)
        ppt = (dep * 2 * math.tan(cam.data.angle_y / 2)) / 1684.0
        du = (box[0] + box[2]) / 2 - (g[0] + g[2]) / 2; dv = (box[1] + box[3]) / 2 - (g[1] + g[3]) / 2
        e.location = e.location + R * (du * ppt) - UPV * (dv * ppt)
    bpy.context.view_layer.update()
    return [round(x, 1) for x in U.screen_bbox(kids_, 1)]


# 16:36 개선문 정면이 카메라 시선과 수직이 되게(윗면이 안 보여 제목이 정면에 앉음)
gempty.rotation_mode = 'QUATERNION'
for _ in range(2):
    out['gate'] = fit_parent(gempty, (347, 19, 845, 235))
    gempty.rotation_quaternion = (CP - gempty.location).normalized().to_track_quat('-Y', 'Z')
out['gate'] = fit_parent(gempty, (347, 19, 845, 235))


def group(name, builders, box, rot=0.0):
    e = bpy.data.objects.new(name, None); C.objects.link(e)
    for p in builders:
        p.parent = e
    e.rotation_euler = (0, 0, YAW + math.pi / 2 + rot)
    return fit_parent(e, box)


# ---------- BASIC 왼쪽 ----------
def cone(name, r, h, gray, rough=0.0, seed=0):
    bpy.ops.mesh.primitive_cone_add(vertices=40, radius1=r, radius2=0.0, depth=h, location=(0, 0, h / 2))
    ob = bpy.context.active_object; ob.name = name
    if rough:
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.subdivide(number_cuts=6); bpy.ops.object.mode_set(mode='OBJECT')
        rng = np.random.default_rng(seed)
        for v in ob.data.vertices:
            if v.co.z > 0.01:
                v.co.x *= 1 + rng.uniform(-rough, rough); v.co.y *= 1 + rng.uniform(-rough, rough)
    return link(ob, gray)


out['lime'] = group('H_lime', [cone('H_lime_pile', 1.0, 0.85, 1.0, 0.05, 1)], (24, 91, 76, 135))
out['ash'] = group('H_ash', [cone('H_ash_pile', 1.0, 0.85, 0.42, 0.05, 2)], (98, 91, 150, 135))
st = [cube('H_stone%d' % i, s, l, g, bevel=0.03) for i, (s, l, g) in enumerate((((0.8, 0.8, 0.6), (0, 0, 0.3), 0.8), ((0.7, 0.7, 0.55), (0.85, 0.15, 0.28), 0.65), ((0.6, 0.9, 0.5), (0.3, 0.95, 0.25), 0.9)))]
out['stones'] = group('H_stones', st, (177, 100, 217, 134))
mold = [cube('H_mold_box', (2.2, 1.5, 0.9), (0, 0, 0.45), 0.4, bevel=0.03)]
for i, (x, y) in enumerate(((-0.5, -0.2), (0.2, 0.3), (0.6, -0.4), (-0.1, 0.5), (0.8, 0.3))):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.11, location=(x, y, 0.92))
    mold.append(link(bpy.context.active_object, 1.0)); mold[-1].name = 'H_mold_lime%d' % i
for i, (sx, sy, x, y) in enumerate(((2.4, 0.1, 0, -0.8), (2.4, 0.1, 0, 0.8), (0.1, 1.7, -1.15, 0), (0.1, 1.7, 1.15, 0))):
    mold.append(cube('H_mold_plank%d' % i, (sx, sy, 1.0), (x, y, 0.5), 0.72, bevel=0.01))
out['mold'] = group('H_mold', mold, (248, 74, 328, 144))

# ---------- BASIC 오른쪽 ----------
books = [cube('H_book1', (0.35, 1.6, 2.2), (0, 0, 1.1), 0.55, bevel=0.03), cube('H_book2', (0.35, 1.5, 2.0), (0.45, 0.05, 1.0), 0.8, bevel=0.03),
         cube('H_book1_pages', (0.3, 1.5, 2.12), (0.03, 0.06, 1.1), 1.0, bevel=0)]
out['books'] = group('H_books', books, (861, 54, 919, 139))
bpy.ops.mesh.primitive_cylinder_add(vertices=40, radius=0.5, depth=1.9, location=(0, 0, 0.95))
core = link(bpy.context.active_object, 0.75); core.name = 'H_core_sample'
for i, z in enumerate((0.55, 1.1, 1.5)):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.51, minor_radius=0.02, location=(0, 0, z))
    t = link(bpy.context.active_object, 0.4); t.name = 'H_core_band%d' % i
bpy.ops.mesh.primitive_torus_add(major_radius=0.45, minor_radius=0.07, location=(0.75, -0.3, 2.0), rotation=(math.pi / 2, 0, 0))
lens = link(bpy.context.active_object, 0.15); lens.name = 'H_lens_ring'
bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.07, depth=0.8, location=(1.18, -0.3, 1.55), rotation=(0, math.radians(-40), 0))
handle = link(bpy.context.active_object, 0.15); handle.name = 'H_lens_handle'
res_parts = [o for o in C.objects if o.name.startswith(('H_core', 'H_lens'))]
out['research'] = group('H_research', res_parts, (976, 61, 1035, 130))
col = bpy.data.objects['COL_ruined']
mini = bpy.data.objects.new('H_colosseum_mini', col.data)   # 메시 공유(메모리 추가 없음)
C.objects.link(mini); mini.rotation_euler = (0, 0, 0)
mini.color = (1, 1, 1, 1)
try:
    mini.visible_shadow = False
except Exception:
    pass
out['colosseum'] = group('H_colosseum', [mini], (1085, 87, 1151, 139), rot=0.0)
print(out)
