"""티베르강 로마 돌다리(B_pons1, B_pons2…) — 넓은 CORE 길(R_core_road)이 강을 건너는 곳마다 (18:00·18:04 사용자)
아치 여러 개 + 교각 + 상판(양 끝 경사로) + 난간. 옆면 윤곽을 조각 다각형으로 나눠 두께 방향으로 세움.
Blender에서: exec(open(<이 파일>).read())
"""
import json
import math
import bpy
import bmesh
import numpy as np
from mathutils import Vector

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_B/'
U = bpy.data.texts['asset_utils.py'].as_module()
P = json.load(open(ROOT + 'assets/terrain_polys.json'))
RIV = np.asarray(P['river'][0][0])
ROAD = np.asarray(json.load(open(ROOT + 'assets/core_road_uv.json')), float)
C = U.coll('35_FIELDS_ROADS')


def inside(ring, x, y):
    c = False
    for (ax, ay), (bx, by) in zip(ring, np.roll(ring, -1, axis=0)):
        if (ay > y) != (by > y) and x < (bx - ax) * (y - ay) / (by - ay + 1e-12) + ax:
            c = not c
    return c


def build_bridge(tag, A_uv, B_uv, WID=3.0, ZW=-0.45):
    A = Vector(U.pt_to_world(*A_uv, 0.0)); B = Vector(U.pt_to_world(*B_uv, 0.0))
    d = B - A; L = d.length; t = d.normalized(); n = Vector((-t.y, t.x, 0))
    PIER, ABUT = 0.55, 0.5
    NA = max(2, int(round(L / 2.4)))
    span = (L - 2 * ABUT - (NA - 1) * PIER) / NA
    r = span / 2
    z_spring = ZW + 0.05
    deck_bot = z_spring + r + 0.12
    deck_top = deck_bot + 0.28

    def W(s, z, side):
        p = A + t * s + n * (side * WID / 2)
        return Vector((p.x, p.y, z))

    bm = bmesh.new()

    def prism(poly):
        front = [bm.verts.new(W(s, z, -1)) for s, z in poly]
        back = [bm.verts.new(W(s, z, +1)) for s, z in poly]
        bm.faces.new(front); bm.faces.new(list(reversed(back)))
        k = len(poly)
        for i in range(k):
            j = (i + 1) % k
            bm.faces.new((front[i], front[j], back[j], back[i]))

    def arc(s0, s1, a0, a1, m=10):
        c = (s0 + s1) / 2
        return [(c + r * math.cos(a), z_spring + r * math.sin(a)) for a in np.linspace(a0, a1, m)]

    arches = []
    s = ABUT
    for _ in range(NA):
        arches.append((s, s + span)); s += span + PIER
    zb = ZW - 0.3
    first, last = arches[0], arches[-1]
    prism([(-0.6, zb), (first[0], zb), (first[0], z_spring)] + arc(*first, math.pi, math.pi / 2)[1:] + [(first[0] + r, deck_bot), (-0.6, deck_bot)])
    for a_, b_ in zip(arches[:-1], arches[1:]):
        prism([(a_[1], zb), (b_[0], zb), (b_[0], z_spring)] + arc(*b_, math.pi, math.pi / 2)[1:] + [(b_[0] + r, deck_bot), (a_[1] - r, deck_bot)] + arc(*a_, math.pi / 2, 0)[1:])
    prism([(last[1], zb), (L + 0.6, zb), (L + 0.6, deck_bot), (last[1] - r, deck_bot)] + arc(*last, math.pi / 2, 0)[1:])
    prism([(-1.8, 0.02), (-0.6, deck_bot), (L + 0.6, deck_bot), (L + 1.8, 0.02), (L + 1.8, 0.16), (L + 0.6, deck_top), (-0.6, deck_top), (-1.8, 0.16)])   # R11 경사로 끝이 길 포장석(0.12)을 덮게
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    name = 'B_pons' + tag
    U.remove_obj(name)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); C.objects.link(ob); ob.color = (1, 1, 1, 1)
    for p_ in ob.data.polygons:
        p_.use_smooth = False
    for side in (-1, 1):
        off = side * (WID / 2 - 0.09)

        def V(s_, z_):
            p = A + t * s_ + n * off
            return Vector((p.x, p.y, z_))
        bm2 = bmesh.new()
        vs = [bm2.verts.new(V(*q)) for q in ((-0.6, deck_top), (L + 0.6, deck_top), (L + 0.6, deck_top + 0.32), (-0.6, deck_top + 0.32))]
        f = bm2.faces.new(vs)
        ext = bmesh.ops.extrude_face_region(bm2, geom=[f])
        for g in ext['geom']:
            if isinstance(g, bmesh.types.BMVert):
                g.co += n * (0.16 * (-side))
        bmesh.ops.recalc_face_normals(bm2, faces=bm2.faces)
        nm = '%s_parapet%d' % (name, 0 if side < 0 else 1)
        U.remove_obj(nm)
        me2 = bpy.data.meshes.new(nm); bm2.to_mesh(me2); bm2.free()
        o2 = bpy.data.objects.new(nm, me2); C.objects.link(o2); o2.color = (1, 1, 1, 1)
    print(name, 'L', round(L, 2), 'arches', NA, [round(x, 1) for x in U.screen_bbox(ob, 1)])


for k in [o.name for o in bpy.data.objects if o.name.startswith('B_pons')]:
    U.remove_obj(k)
seg = np.r_[0, np.cumsum(np.hypot(*np.diff(ROAD, axis=0).T))]
ss = np.arange(0, seg[-1], 0.5)
pts = np.c_[np.interp(ss, seg, ROAD[:, 0]), np.interp(ss, seg, ROAD[:, 1])]
wet = np.array([inside(RIV, x, y) for x, y in pts])
runs = []
i = 0
while i < len(wet):
    if wet[i]:
        j = i
        while j < len(wet) and wet[j]:
            j += 1
        runs.append((max(0, i - 14), min(len(pts) - 1, j + 13)))       # 둑 위로 7pt씩 걸침
        i = j
    else:
        i += 1
for k, (i0, i1) in enumerate(runs):
    build_bridge(str(k + 1), tuple(pts[i0]), tuple(pts[i1]))
