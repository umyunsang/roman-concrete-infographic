"""1차 회색 프록시: Figma 최종안 화면 좌표(pt)에서 거꾸로 푼 덩어리 배치.

정사영 진짜 아이소메트릭에서
- 바닥 a×b(세계 X·Y축), 높이 h인 상자: 화면 폭 = 0.7071(a+b), 화면 높이 = 0.4082(a+b) + 0.8165h
- 반지름 r, 높이 h인 원기둥: 화면 폭 = 2r, 화면 높이 = 0.5774r + 0.8165h
길이 단위는 'pt 단위'(화면 평면 1pt)로 계산한 뒤 PT(0.1)를 곱해 세계 단위로 쓴다.
"""
import bpy, bmesh, math
from mathutils import Vector

exec(bpy.data.texts['anchors.py'].as_string())   # pt_to_world, world_to_pt, PT

S_BOX = 0.70711   # (a+b) → 화면 폭
V_BOX = 0.40825   # (a+b) → 화면 높이 중 바닥 마름모 몫
V_UP = 0.81650    # h → 화면 높이


def coll(name):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c


def clear(c):
    for ob in list(c.objects):
        bpy.data.objects.remove(ob, do_unlink=True)


def _link(ob, c):
    for cc in ob.users_collection:
        cc.objects.unlink(ob)
    c.objects.link(ob)


def box_from_bbox(name, bbox, c, ratio=1.0, h=None, base_h=0.0):
    """화면 경계 상자 (x0,y0,x1,y1)[pt]에 맞는 상자. ratio = a/b(세계 X/Y 길이 비).
    h, base_h는 pt 단위(세계 높이 = 값 × PT). bbox는 base_h 높이에 놓인 물체의 화면 상자."""
    x0, y0, x1, y1 = bbox
    s = (x1 - x0) / S_BOX                 # a+b (pt 단위)
    if h is None:
        h = max(1.0, ((y1 - y0) - V_BOX * s) / V_UP)
    b = s / (1 + ratio); a = s - b
    base = pt_to_world((x0 + x1) / 2, y1 - V_BOX * s / 2, base_h * PT)
    bpy.ops.mesh.primitive_cube_add(size=1, location=base + Vector((0, 0, h * PT / 2)))
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (a * PT, b * PT, h * PT)
    _link(ob, c)
    return ob


def cyl_from_bbox(name, bbox, c, h=None, base_h=0.0, cone=False, ellipse=1.0, verts=48):
    """화면 경계 상자에 맞는 원기둥(또는 원뿔). ellipse = 세계 Y/X 반지름 비."""
    x0, y0, x1, y1 = bbox
    r = (x1 - x0) / 2
    if h is None:
        h = max(1.0, ((y1 - y0) - 0.57735 * r * 2 * 0.5 * 2) / V_UP) if not cone else max(1.0, ((y1 - y0) - 0.57735 * r) / V_UP)
    base = pt_to_world((x0 + x1) / 2, y1 - 0.57735 * r * ellipse, base_h * PT)
    if cone:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r * PT, depth=h * PT, location=base + Vector((0, 0, h * PT / 2)))
    else:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r * PT, depth=h * PT, location=base + Vector((0, 0, h * PT / 2)))
    ob = bpy.context.active_object
    ob.name = name
    ob.scale.y = ellipse
    ob.rotation_euler.z = math.radians(45)   # 로컬 X = 세계 X+Y(화면 수평), 로컬 Y = 화면 세로 방향 대각
    _link(ob, c)
    return ob


def ribbon(name, pts, c, width, h=0.0, thick=0.3, z_off=0.0):
    """화면 점 열(세계 높이 h 평면)을 따라가는 띠(강·길). h는 세계 단위(작은 값)."""
    P = [pt_to_world(u, v, h) for u, v in pts]
    bm = bmesh.new()
    left, right = [], []
    for i, p in enumerate(P):
        d = (P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]); d.z = 0; d.normalize()
        n = Vector((-d.y, d.x, 0)) * (width * PT / 2)
        left.append(bm.verts.new(p + n + Vector((0, 0, z_off))))
        right.append(bm.verts.new(p - n + Vector((0, 0, z_off))))
    for i in range(len(P) - 1):
        bm.faces.new((left[i], left[i + 1], right[i + 1], right[i]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); c.objects.link(ob)
    if thick:
        m = ob.modifiers.new('두께', 'SOLIDIFY'); m.thickness = thick
    return ob


def wall_ring(name, pts, c, wall_h, width):
    """성벽 고리: 화면 점(성벽 윗면 높이 wall_h)에서 아래로 세운 벽."""
    P = [pt_to_world(u, v, wall_h * PT) for u, v in pts]
    bm = bmesh.new()
    for i in range(len(P)):
        p, q = P[i], P[(i + 1) % len(P)]
        d = q - p; d.z = 0; L = d.length; d.normalize()
        mid = (p + q) / 2
        ang = math.atan2(d.y, d.x)
        bmesh.ops.create_cube(bm, size=1.0, matrix=(
            __import__('mathutils').Matrix.Translation(Vector((mid.x, mid.y, wall_h * PT / 2)))
            @ __import__('mathutils').Matrix.Rotation(ang, 4, 'Z')
            @ __import__('mathutils').Matrix.Diagonal(Vector((L, width * PT, wall_h * PT, 1)))))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); c.objects.link(ob)
    return ob


def build():
    C = coll('10_PROXY'); clear(C)
    # 땅·바다
    ribbon('PX_ground', [(-200, 900), (1400, 900)], C, width=3000, h=0, thick=0.2, z_off=-0.25)
    ribbon('PX_sea_band', [(-60, 1600), (400, 1640), (900, 1700)], C, width=520, h=-0.5, thick=0.1)
    ribbon('PX_tiber', [(150, 610), (250, 700), (300, 800), (300, 900), (280, 1000), (230, 1120), (150, 1250), (60, 1395)], C, width=45, h=0.05, thick=0.05)
    # 산맥(원뿔)
    for i, bb in enumerate([(0, 180, 160, 420), (110, 150, 310, 395), (280, 150, 500, 300), (500, 150, 720, 280),
                            (600, 150, 820, 290), (730, 150, 980, 330), (840, 160, 1110, 390), (1050, 200, 1191, 420)]):
        cyl_from_bbox(f'PX_mtn_{i}', bb, C, cone=True, verts=7)
    # 계단식 언덕(상자 3층)
    for nm, bb, layers in [('left', (0, 400, 180, 610), 3), ('right', (950, 360, 1191, 545), 3),
                           ('palatine', (355, 800, 580, 960), 3), ('privernum', (985, 1008, 1175, 1148), 3)]:
        x0, y0, x1, y1 = bb
        for k in range(layers):
            shrink = k * 0.18 * (x1 - x0) / 2
            box_from_bbox(f'PX_hill_{nm}_{k}', (x0 + shrink, y0 + shrink * 0.6, x1 - shrink, y1 - shrink * 0.2), C, h=12, base_h=k * 12)
    # 콜로세움(타원 원기둥): 윗테두리 y 613~840, x 460~820, 벽 화면 높이 ≈ 120
    cyl_from_bbox('PX_colosseum', (460, 613, 820, 960), C, h=147, ellipse=1.09)
    # 성벽 고리(윗면 높이 25)
    ring = [(320, 662), (468, 590), (700, 568), (890, 640), (970, 775), (910, 925), (720, 1020), (497, 1005), (355, 910), (315, 782)]
    wall_ring('PX_wall_ring', ring, C, wall_h=25, width=14)
    # 수도교: 바닥선 (805,383+150)~(1010,275+150), 화면 높이 ≈ 75
    box_from_bbox('PX_aqueduct_box', (797, 340, 1012, 535), C, ratio=0.06)
    # 가마·항구·폼페이·화산·실험실
    cyl_from_bbox('PX_kiln', (135, 650, 175, 700), C, h=40)
    box_from_bbox('PX_breakwater', (138, 1405, 345, 1525), C, ratio=0.12, h=8)
    box_from_bbox('PX_harbor_tower', (330, 1405, 357, 1460), C, h=45)
    box_from_bbox('PX_pompeii', (812, 1400, 948, 1482), C, h=12)
    cyl_from_bbox('PX_vesuvius', (890, 1365, 1500, 1900), C, cone=True, verts=9)
    box_from_bbox('PX_lab_island', (552, 1527, 648, 1601), C, h=25, base_h=8)
    # 주택 묶음(작은 상자)
    for i, bb in enumerate([(340, 690, 440, 780), (870, 700, 950, 830), (760, 840, 920, 910), (625, 920, 730, 980),
                            (460, 950, 510, 990), (760, 980, 820, 1030)]):
        box_from_bbox(f'PX_houses_{i}', bb, C, h=10)
    return C


C = build()
print('proxies', len(C.objects))
