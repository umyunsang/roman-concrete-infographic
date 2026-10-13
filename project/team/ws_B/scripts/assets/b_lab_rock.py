"""워커 B: 실험실 섬 — 바닥을 늘이니 고드름 같은 바위 뿔이 됨 → 늘인 것 되돌리고(정확한 역변환),
수면에서 솟은 넓고 낮은 바위 둔덕(S_lab_island_rock)을 받침으로 둠: 섬이 물에서 솟은 바위 위에 앉아 보이게."""
import math
import bpy
import bmesh
import numpy as np
from mathutils import Vector
U = bpy.data.texts['asset_utils.py'].as_module()
o = bpy.data.objects['S_lab_island']
if o.get('b_sunk') and not o.get('b_unsunk'):
    me = o.data; M = np.array(o.matrix_world); Mi = np.linalg.inv(M)
    co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    W = co @ M[:3, :3].T + M[:3, 3]
    zmin, band, D = 0.009, 0.5, 0.009 + 0.85
    zn = W[:, 2]
    m = zn < zmin + band
    W[m, 2] = (zn[m] + D + D * zmin / band) / (1 + D / band)
    me.vertices.foreach_set('co', (W @ Mi[:3, :3].T + Mi[:3, 3]).ravel()); me.update()
    o['b_unsunk'] = True
    print('lab island restored, zmin', round(float(W[:, 2].min()), 3))
# 바위 섬 받침: 섬 아래 뒤집힌 원뿔(z 0→2, 반지름 0.5→2.6)을 감싸며 물속(-0.85)까지 내려가는 울퉁불퉁한 바위 둔덕
# (화면 가로 = 세계 (1,1) 방향은 넓게 3.3, 화면 세로 = (1,-1) 방향은 2.5 — 아래 연표 글 상자에 닿지 않게)
P = U.eval_world_coords(o, 1)
cx, cy = (P[:, 0].max() + P[:, 0].min()) / 2, (P[:, 1].max() + P[:, 1].min()) / 2
ea = np.array([1.0, 1.0]) / math.sqrt(2); eb = np.array([1.0, -1.0]) / math.sqrt(2)
U.remove_obj('S_lab_island_rock')
bm = bmesh.new()
rng = np.random.default_rng(3)
NR, NA = 12, 48
rings = []
for i in range(NR + 1):
    t = i / NR
    z = 1.15 - 1.75 * t ** 1.6
    RA = 2.05 + 1.55 * t ** 0.8; RB = 2.05 + 0.6 * t ** 0.8   # 워커 B: 곶 위 둔덕 — 섬 원뿔 아랫부분을 묻음
    ring = []
    for j in range(NA):
        a = 2 * math.pi * j / NA
        wob = 1 + (0.06 * math.sin(3 * a + 0.5) + 0.04 * math.sin(7 * a + 1.3) + rng.uniform(-0.025, 0.025)) * min(1.0, t * 3)
        d = (ea * RA * math.cos(a) + eb * RB * math.sin(a)) * wob
        zz = z + (0.05 * math.sin(5 * a + 3 * t) + rng.uniform(-0.03, 0.03)) * (0.05 < t < 0.95)
        ring.append(bm.verts.new((cx + d[0], cy + d[1], zz)))
    rings.append(ring)
top = bm.verts.new((cx, cy, 1.17))
for j in range(NA):
    bm.faces.new((top, rings[0][j], rings[0][(j + 1) % NA]))
for i in range(NR):
    for j in range(NA):
        bm.faces.new((rings[i][j], rings[i + 1][j], rings[i + 1][(j + 1) % NA], rings[i][(j + 1) % NA]))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
me = bpy.data.meshes.new('S_lab_island_rock'); bm.to_mesh(me); bm.free()
rock = bpy.data.objects.new('S_lab_island_rock', me)
bpy.data.collections['40_REGION'].objects.link(rock)
rock.color = (0.97, 0.97, 0.97, 1)
for p in me.polygons:
    p.use_smooth = True
print('rock', [round(x, 1) for x in U.screen_bbox(rock, 1)], 'island', [round(x, 1) for x in U.screen_bbox(o, 1)])
