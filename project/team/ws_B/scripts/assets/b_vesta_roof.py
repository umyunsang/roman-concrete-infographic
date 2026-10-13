"""워커 B: 베스타 신전(원형 신전) 지붕 — Meshy 지붕이 각진 저폴리곤 + 삼각 파편(블라인드 심사)
→ 처마(z≈6.45) 위를 지우고, 64분할 매끈한 원뿔형 지붕(살짝 둥근 단면) + 꼭대기 장식을 절차로. 한 번만(o['b_roof_cut'])."""
import math
import bpy
import bmesh
import numpy as np
from mathutils import Vector
U = bpy.data.texts['asset_utils.py'].as_module()
o = bpy.data.objects['L03_forum_vesta']
M = o.matrix_world
if not o.get('b_roof_cut'):
    bm = bmesh.new(); bm.from_mesh(o.data)
    kill = [v for v in bm.verts if (M @ v.co).z > 6.45]
    bmesh.ops.delete(bm, geom=kill, context='VERTS')
    bm.to_mesh(o.data); bm.free(); o.data.update()
    o['b_roof_cut'] = True
    print('vesta roof verts removed', len(kill))
P = U.eval_world_coords(o, 1)
top = P[P[:, 2] > 5.6]
cx, cy = float(np.median(top[:, 0])), float(np.median(top[:, 1]))
R = float(np.percentile(np.hypot(top[:, 0] - cx, top[:, 1] - cy), 97)) + 0.12
z0 = float(P[:, 2].max()) - 0.05
U.remove_obj('L03_forum_vesta_roof')
bm = bmesh.new()
NS, NR = 64, 8
rings = []
for i in range(NR + 1):
    t = i / NR                      # 0 = 처마, 1 = 꼭대기
    r = R * (1 - t)
    z = z0 + 1.9 * (1 - (1 - t) ** 1.35)
    rings.append([bm.verts.new((cx + r * math.cos(2 * math.pi * k / NS), cy + r * math.sin(2 * math.pi * k / NS), z)) for k in range(NS)])
# 처마 끝 아래로 살짝 내려오는 테
eave = [bm.verts.new((cx + (R + 0.05) * math.cos(2 * math.pi * k / NS), cy + (R + 0.05) * math.sin(2 * math.pi * k / NS), z0 - 0.18)) for k in range(NS)]
for k in range(NS):
    bm.faces.new((eave[k], eave[(k + 1) % NS], rings[0][(k + 1) % NS], rings[0][k]))
for i in range(NR):
    for k in range(NS):
        bm.faces.new((rings[i][k], rings[i][(k + 1) % NS], rings[i + 1][(k + 1) % NS], rings[i + 1][k]))
bot = bm.verts.new((cx, cy, z0 - 0.18))
for k in range(NS):
    bm.faces.new((bot, eave[(k + 1) % NS], eave[k]))
# 안쪽 원통 벽(cella): 열주 사이로 비어 보이던 것(원래 지붕 밑 그늘이 벽처럼 보였음)
fl = float(np.percentile(P[(np.hypot(P[:, 0] - cx, P[:, 1] - cy) < 2.5)][:, 2], 50)) if (np.hypot(P[:, 0] - cx, P[:, 1] - cy) < 2.5).any() else 1.8
res = bmesh.ops.create_cone(bm, cap_ends=False, segments=48, radius1=R * 0.7, radius2=R * 0.7, depth=z0 - fl)
for v in res['verts']:
    v.co += Vector((cx, cy, fl + (z0 - fl) / 2))
# 꼭대기 장식(작은 기둥 + 머리)
res = bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.22, radius2=0.12, depth=0.55)
for v in res['verts']:
    v.co += Vector((cx, cy, z0 + 1.9 + 0.2))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
me = bpy.data.meshes.new('L03_forum_vesta_roof'); bm.to_mesh(me); bm.free()
roof = bpy.data.objects.new('L03_forum_vesta_roof', me)
bpy.data.collections['40_REGION'].objects.link(roof)
roof.color = (0.9, 0.9, 0.9, 1)
for p in me.polygons:
    p.use_smooth = True
print('vesta roof R', round(R, 2), 'z0', round(z0, 2), 'floor', round(fl, 2), 'screen', [round(x, 1) for x in U.screen_bbox([o, roof], 1)])
