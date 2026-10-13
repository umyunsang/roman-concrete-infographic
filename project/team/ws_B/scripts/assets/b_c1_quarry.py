"""워커 B · I4(장면 전달): CORE ① '화산재 채취'가 수레·항아리 때문에 시장처럼 읽힘 → 장면 뒤(화면 위쪽 산기슭)에
화산재(포촐라나) 채석장 = 둥근 언덕을 계단식으로 파낸 구덩이(드러난 어두운 응회암 벽) + 어두운 화산재 더미 둘. 절차 제작.
물체 자리는 그대로(C1 장면 뒤 빈 산기슭), 45_CORE_SCENES에 넣어 감사(글↔물체)를 받음."""
import math
import bpy
import bmesh
import numpy as np
from mathutils import Vector
U = bpy.data.texts['asset_utils.py'].as_module()
rng = np.random.default_rng(31)
C0 = np.array([-50.5, 79.5])          # 세계 좌표 중심(C1 장면 뒤)
A, B, STEP = 8.0, 5.5, 0.18


def mound(a, b):
    ang = math.atan2(b, a)
    wob = 1 + 0.08 * math.sin(3 * ang + 0.4) + 0.05 * math.sin(5 * ang + 1.7)
    r = math.sqrt((a / (A * wob)) ** 2 + (b / (B * wob)) ** 2)
    t = min(1.0, max(0.0, (1.0 - r) / 0.75))
    return 2.7 * t * t * (3 - 2 * t)


def pit(a, b):
    """계단식 구덩이: 앞(-b)으로 열림, 뒤로 갈수록 한 단씩 높아짐. 구덩이 밖이면 None"""
    half = 4.2 + 0.3 * math.sin(b * 0.9)
    if abs(a) > half or b > 2.4:
        return None
    lvl = math.floor((b + 6.0) / 2.1)
    return 0.05 + 0.62 * lvl


na, nb = int(2 * A / STEP) + 1, int(2 * B / STEP) + 1
bm_l, bm_d = bmesh.new(), bmesh.new()
H = np.zeros((na, nb)); IN = np.zeros((na, nb), bool)
for i in range(na):
    for j in range(nb):
        a, b = -A + i * STEP, -B + j * STEP
        h = mound(a, b); p = pit(a, b)
        if p is not None and p < h:
            H[i, j] = p; IN[i, j] = True
        else:
            H[i, j] = h


def W(i, j):
    a, b = -A + i * STEP, -B + j * STEP
    return (C0[0] + a, C0[1] + b, H[i, j] - 0.06)


vl, vd = {}, {}
for i in range(na - 1):
    for j in range(nb - 1):
        hs = [H[i, j], H[i + 1, j], H[i + 1, j + 1], H[i, j + 1]]
        if max(hs) < 0.02:
            continue
        dark = IN[i, j] or IN[i + 1, j] or IN[i + 1, j + 1] or IN[i, j + 1]
        bmx, vv = (bm_d, vd) if dark else (bm_l, vl)
        q = []
        for (ii, jj) in ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)):
            if (ii, jj) not in vv:
                vv[ii, jj] = bmx.verts.new(W(ii, jj))
            q.append(vv[ii, jj])
        bmx.faces.new(q)
# 화산재 더미 둘(구덩이 앞, 수레 쪽)
heaps = bmesh.new()
for (dx, dy, r, h) in ((11.0, -2.2, 1.15, 0.8), (12.9, -0.5, 0.9, 0.6)):   # C1 장면 오른쪽 옆, 화면 가로로 나란히 — 둥근 화산재 더미
    res = bmesh.ops.create_icosphere(heaps, subdivisions=3, radius=1.0)
    for v in res['verts']:
        p_ = v.co.copy()
        zz = max(p_.z, -0.05)
        k = 1 + 0.07 * math.sin(5 * math.atan2(p_.y, p_.x) + dx)
        v.co = Vector((C0[0] + dx + p_.x * r * k, C0[1] + dy + p_.y * r * k, zz * h - 0.04))
objs = []
for name, b_, g in (('C1_quarry_hill', bm_l, 0.8), ('C1_quarry_cut', bm_d, 0.5), ('C1_quarry_ash', heaps, 0.42)):
    U.remove_obj(name)
    me = bpy.data.meshes.new(name); b_.to_mesh(me); b_.free()
    o = bpy.data.objects.new(name, me); U.coll('45_CORE_SCENES').objects.link(o)
    o.color = (g, g, g, 1)
    for p in me.polygons:
        p.use_smooth = name == 'C1_quarry_hill'
    objs.append(o)
print('quarry screen', [round(x, 1) for x in U.screen_bbox(objs, 1)], 'tris', sum(U.tri_count(o) for o in objs))
import json
T = json.load(open('/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_B/loop/figma_texts.json'))
q = np.concatenate([U.project_pts(U.eval_world_coords(o, 1)) for o in objs])
for t in T:
    x0, y0, x1, y1 = t['b']
    k = int(((q[:, 0] > x0 - 3) & (q[:, 0] < x1 + 3) & (q[:, 1] > y0 - 3) & (q[:, 1] < y1 + 3)).sum())
    if k:
        print('QUARRY TEXT HIT', t['c'][:12], k)
