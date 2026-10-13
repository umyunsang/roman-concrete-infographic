"""워커 B · I5(DETAIL 도해): ② 제작 원리 큐브가 겉면의 흰 알갱이 때문에 '주사위'로 읽힘(블라인드 심사 2회)
→ Li & Agrawala 절개도 문법: 카메라 쪽 위 모서리 1/8을 축 정렬로 잘라내고(계단식 절개), 단면만 어둡게 + 단면 속에 크고 작은 흰 석회 알갱이.
겉면 알갱이는 지시선('석회 알갱이')이 가리키는 하나만 남김. 화면 자리·크기 그대로(같은 부모 D2_making, 같은 국소 좌표). 한 번만 다시 만들어도 같은 결과."""
import math
import bpy
import bmesh
import numpy as np
from mathutils import Vector
U = bpy.data.texts['asset_utils.py'].as_module()
rng = np.random.default_rng(23)
e2 = bpy.data.objects['D2_making']
cube = bpy.data.objects['D2_cube']
C = cube.users_collection[0]
for n in ('D2_cut_body', 'D2_cut_faces', 'D2_cut_clasts', 'D2_cutter'):
    U.remove_obj(n)
# 1) 잘린 몸체: 정육면체 − (x>0, y<0, z>0.75) 팔분체
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.5)
for v in bm.verts:
    v.co.z += 0.75
me = bpy.data.meshes.new('D2_cut_tmp'); bm.to_mesh(me); bm.free()
body = bpy.data.objects.new('D2_cut_body', me); C.objects.link(body); body.parent = e2
bmc = bmesh.new(); bmesh.ops.create_cube(bmc, size=1.0)
for v in bmc.verts:
    v.co = Vector((0.4 + v.co.x * 0.8, -0.4 + v.co.y * 0.8, 1.15 + v.co.z * 0.8))
mc = bpy.data.meshes.new('D2_cutter'); bmc.to_mesh(mc); bmc.free()
cutter = bpy.data.objects.new('D2_cutter', mc); C.objects.link(cutter); cutter.parent = e2
cutter.hide_render = True
mod = body.modifiers.new('cut', 'BOOLEAN'); mod.operation = 'DIFFERENCE'; mod.object = cutter; mod.solver = 'EXACT'
bpy.context.view_layer.update()
deps = bpy.context.evaluated_depsgraph_get()
newme = bpy.data.meshes.new_from_object(body.evaluated_get(deps))
body.modifiers.remove(mod)
old = body.data; body.data = newme; newme.name = 'D2_cut_body'; bpy.data.meshes.remove(old)
U.remove_obj('D2_cutter')
bv = body.modifiers.new('bv', 'BEVEL'); bv.width = 0.04; bv.segments = 2; bv.limit_method = 'ANGLE'
body.color = cube.color[:]
if 'g_orig' in cube:
    body['g_orig'] = cube['g_orig']
for p in body.data.polygons:
    p.use_smooth = False
cube.hide_render = True
# 2) 단면 세 장(살짝 앞으로): x=0 면(y∈[-.75,0], z∈[.75,1.5]) 법선 +x / y=0 면(x∈[0,.75]) 법선 -y / z=0.75 바닥(x∈[0,.75], y∈[-.75,0]) 법선 +z
E = 0.006; I = 0.045    # 베벨 안쪽으로 조금 들임
faces = [
    ((0 + E, -0.75 + I, 0.75 + I), (0 + E, 0 - I, 0.75 + I), (0 + E, 0 - I, 1.5 - I), (0 + E, -0.75 + I, 1.5 - I)),
    ((0 + I, 0 - E, 0.75 + I), (0.75 - I, 0 - E, 0.75 + I), (0.75 - I, 0 - E, 1.5 - I), (0 + I, 0 - E, 1.5 - I)),
    ((0 + I, -0.75 + I, 0.75 + E), (0.75 - I, -0.75 + I, 0.75 + E), (0.75 - I, 0 - I, 0.75 + E), (0 + I, 0 - I, 0.75 + E)),
]
bm = bmesh.new()
for q, nrm in zip(faces, ((1, 0, 0), (0, -1, 0), (0, 0, 1))):
    f = bm.faces.new([bm.verts.new(v) for v in q])
    f.normal_update()
    if f.normal.dot(Vector(nrm)) < 0:
        f.normal_flip()
mf = bpy.data.meshes.new('D2_cut_faces'); bm.to_mesh(mf); bm.free()
fo = bpy.data.objects.new('D2_cut_faces', mf); C.objects.link(fo); fo.parent = e2
g0 = float(cube.get('g_orig', cube.color[0]))
fo['g_orig'] = max(0.0, g0 - 0.12); fo.color = (fo['g_orig'],) * 3 + (1,)
# 3) 단면 속 석회 알갱이(크고 작은 흰 원판, 겹치지 않게)
bm = bmesh.new()


def disc(c, n, t1, t2, r, seg=14):
    """얇은 원기둥(두께 0.012) — 단면 위로 살짝 볼록한 알갱이, 앞뒤 어느 쪽에서도 채워져 보임"""
    ring0 = [bm.verts.new(Vector(c) + Vector(n) * 0.004 + (Vector(t1) * math.cos(a) + Vector(t2) * math.sin(a)) * r) for a in np.linspace(0, 2 * math.pi, seg, endpoint=False)]
    ring1 = [bm.verts.new(Vector(c) + Vector(n) * 0.018 + (Vector(t1) * math.cos(a) + Vector(t2) * math.sin(a)) * r * 0.92) for a in np.linspace(0, 2 * math.pi, seg, endpoint=False)]
    top = bm.faces.new(ring1); top.normal_update()
    if top.normal.dot(Vector(n)) < 0:
        top.normal_flip()
    bm.faces.new(list(reversed(ring0)))      # 닫힌 원기둥(법선 계산이 뒤집히지 않게)
    for i in range(seg):
        j = (i + 1) % seg
        bm.faces.new((ring0[i], ring0[j], ring1[j], ring1[i]))


frames = [((1, 0, 0), (0, 1, 0), (0, 0, 1), lambda u, v: (0.0, -0.75 + u * 0.75, 0.75 + v * 0.75)),
          ((0, 0, 1), (1, 0, 0), (0, 1, 0), lambda u, v: (u * 0.75, -0.75 + v * 0.75, 0.75))]
for n, t1, t2, P in frames:
    placed = []
    for _ in range(200):
        r = float(rng.choice([0.035, 0.05, 0.07, 0.095], p=[0.35, 0.3, 0.22, 0.13]))
        u, v = rng.uniform(0.1, 0.9, 2)
        c = np.array(P(u, v))
        m = 0.06 + r
        if min(c[0] if n != (1, 0, 0) else 9, 0.75 - c[0] if n != (1, 0, 0) else 9) < m:
            continue
        if any(np.linalg.norm(c - q) < r + rq + 0.03 for q, rq in placed):
            continue
        placed.append((c, r))
        if len(placed) >= 13:
            break
    for c, r in placed:
        disc(c, n, t1, t2, r)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
mcl = bpy.data.meshes.new('D2_cut_clasts'); bm.to_mesh(mcl); bm.free()
co = bpy.data.objects.new('D2_cut_clasts', mcl); C.objects.link(co); co.parent = e2
co['g_orig'] = 1.0; co.color = (1, 1, 1, 1)
# 4) 겉면 알갱이: 지시선 끝(128,1007)에 가장 가까운 하나만 남김
import re
limes = [o for o in bpy.data.objects if re.fullmatch(r'D2_lime\d+', o.name)]   # 'D2_lime_kiln'(석회 가마)은 제외!
if bpy.data.objects.get('D2_lime_kiln'):
    bpy.data.objects['D2_lime_kiln'].hide_render = False
bpy.context.view_layer.update()
d = []
for o in limes:
    o.hide_render = False
    b = U.screen_bbox(o, 1); d.append((math.hypot((b[0] + b[2]) / 2 - 128, (b[1] + b[3]) / 2 - 1007), o))
d.sort(key=lambda x: x[0])
for k, (dist, o) in enumerate(d):
    o.hide_render = k > 0
print('D2 cutaway: kept lime', d[0][1].name, 'dist', round(d[0][0], 1), 'body', [round(x, 1) for x in U.screen_bbox([body, fo, co], 1)], 'old cube', [round(x, 1) for x in U.screen_bbox(cube, 1)])
