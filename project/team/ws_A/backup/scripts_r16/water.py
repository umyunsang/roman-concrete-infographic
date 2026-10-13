"""바다·강 표현 (14:58 사용자: "바다표현이랑 강표현도 해야해")
디오라마식 물: 수면은 잔잔하게(바둑판처럼 보이던 큰 물결 제거) + 위에 얹는 표현 요소
- 바다: 해안선과 나란한 짧은 물결 획(~ 모양 돋을 띠), 해안 가까울수록 촘촘 / 해안을 따라 흰 파도 띠(굽이치는 둑)
- 강: 흐름 방향을 따르는 가는 물결 선(대시)
모두 낮은 지형(low_terrain). Blender에서: exec(open(<이 파일>).read())
"""
import json
import math
import bpy
import numpy as np

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_A/'
U = bpy.data.texts['asset_utils.py'].as_module()
rng = np.random.default_rng(5)
P = json.load(open(ROOT + 'assets/terrain_polys.json'))
SEA = np.asarray(P['sea'][0][0]); RIV = np.asarray(P['river'][0][0])
ZONES = [z for k, z in json.load(open(ROOT + 'sketch_v2/text_zones.json'))['zones'].items() if k not in ('TITLE_BAND',)]
# FTXT: v7 실제 글 상자 — 물결 획이 글 밑에 오지 않게(완전히 비움)
FTXT = [[t['b'][0] - 8, t['b'][1] - 6, t['b'][2] + 8, t['b'][3] + 6] for t in json.load(open(ROOT + 'loop/figma_texts.json'))]
SEA_Z, RIVER_Z = -0.7, -0.4


def inside(ring, x, y):
    res = np.zeros(np.shape(x), bool)
    xi, yi = ring[:, 0], ring[:, 1]; xj, yj = np.roll(xi, 1), np.roll(yi, 1)
    for a, b, c, d in zip(xi, yi, xj, yj):
        cond = (b > y) != (d > y)
        with np.errstate(divide='ignore', invalid='ignore'):
            xint = (c - a) * (y - b) / (d - b + 1e-12) + a
        res ^= cond & (x < xint)
    return res


def nearest_seg(ring, x, y):
    """가장 가까운 테두리 선분의 (거리, 단위 방향벡터)"""
    A = ring[:-1]; B = ring[1:]; d = B - A; L2 = (d ** 2).sum(1) + 1e-12
    t = np.clip(((x - A[:, 0]) * d[:, 0] + (y - A[:, 1]) * d[:, 1]) / L2, 0, 1)
    q = A + t[:, None] * d
    dist = np.hypot(q[:, 0] - x, q[:, 1] - y); k = int(np.argmin(dist))
    return dist[k], d[k] / math.sqrt(L2[k])


V, F = [], []


def stroke(pts_uv, z, width, height):
    """화면 pt 폴리라인 → 땅(z) 위 가는 돋을 띠(삼각 단면)."""
    W = U.pts_to_world(np.asarray(pts_uv, float), 0.0)[:, :2]
    if len(W) < 2:
        return
    T = np.gradient(W, axis=0); T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-9
    N = np.c_[-T[:, 1], T[:, 0]]
    n = len(W); b = sum(len(v) for v in V)
    taper = np.sin(np.linspace(0.15, math.pi - 0.15, n))       # 양끝 가늘게
    L = W + N * (width / 2) * taper[:, None]; R = W - N * (width / 2) * taper[:, None]
    top = np.c_[W, np.full(n, z + height) * 1.0]
    top[:, 2] = z + height * taper
    V.append(np.r_[np.c_[L, np.full(n, z)], top, np.c_[R, np.full(n, z)]])
    for i in range(n - 1):
        F.append((b + i, b + i + 1, b + n + i + 1, b + n + i))
        F.append((b + n + i, b + n + i + 1, b + 2 * n + i + 1, b + 2 * n + i))


_FP = json.load(open(ROOT + 'assets/object_footprints.json'))
SEA_OBJ = [_FP[k] for k in ('L09_portus_lighthouse', 'L09_portus_mole', 'L12_harbor_pilae', 'S_lab_island') if k in _FP]
SEA_OBJ_BOX = []
for _n in ('L09_portus_lighthouse', 'L09_portus_mole', 'L12_harbor_pilae', 'S_lab_island'):
    _o = bpy.data.objects.get(_n)
    if _o:
        SEA_OBJ_BOX.append(U.screen_bbox(_o, 2))
# PINSEG(R8): SUPPORT 점선 핀 둘레 8pt엔 물결 없음
PINSEG = [((240, 1533), (198, 1497)), ((590, 1497.8), (590, 1536.9)), ((724, 1545), (724, 1482)), ((897, 1062), (1024, 1062))]


def near_pin(x, y, d=8.0):
    for (ax, ay), (bx, by) in PINSEG:
        dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy
        t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / L2))
        if math.hypot(x - (ax + t * dx), y - (ay + t * dy)) < d:
            return True
    return False


# ---- 바다 물결 획 ----
COAST = SEA[(SEA[:, 0] > -5) & (SEA[:, 0] < 1196) & (SEA[:, 1] < 1640)]
n_sea = 0
for v in np.arange(1335, 1700, 13.0):
    for u in np.arange(-4, 1200, 30.0):
        x = u + rng.uniform(-12, 12) + (v % 26) * 0.6; y = v + rng.uniform(-4, 4)
        if not inside(SEA, x, y) or y > 1690:
            continue
        dist, tdir = nearest_seg(COAST, x, y)                  # 프레임 여백 테두리가 아니라 실제 해안선 기준
        if dist < 7:
            continue
        near = math.exp(-dist / 60.0)
        if rng.random() > 0.25 + 0.6 * near:
            continue
        if any(z[0] - 2 < x < z[2] + 2 and z[1] - 2 < y < z[3] + 2 for z in ZONES) and rng.random() < 0.6:
            continue
        if any(z[0] - 12 < x < z[2] + 12 and z[1] - 10 < y < z[3] + 10 for z in FTXT) or y > 1600 or near_pin(x, y, 12):
            continue   # R5 연표 띠(1600 아래)·글 상자 둘레엔 물결 없음
        if tdir[0] < 0:
            tdir = -tdir
        ln = rng.uniform(10, 18) * (0.8 + 0.4 * near)
        s = np.linspace(-0.5, 0.5, 9)
        pts = np.c_[x + tdir[0] * s * ln - tdir[1] * 1.6 * np.sin(s * 2 * math.pi),
                    y + tdir[1] * s * ln + tdir[0] * 1.6 * np.sin(s * 2 * math.pi)]
        # STROKE_ALL(R10): 획의 어느 점이라도 핀 8pt·글 상자 안이면 버림
        if any(near_pin(px, py, 8) or any(z[0] - 4 < px < z[2] + 4 and z[1] - 4 < py < z[3] + 4 for z in FTXT) or any(b[0] - 6 < px < b[2] + 6 and b[1] - 6 < py < b[3] + 6 for b in SEA_OBJ_BOX) for px, py in pts):   # R15 바다 위 시설 둘레도
            continue
        stroke(pts, SEA_Z + 0.02, 0.32, 0.09)
        n_sea += 1

# ---- 해안 파도 띠: 바다 다각형 중 실제 해안 구간(화면 안)만, 바다 쪽으로 4pt ----
coast = SEA[(SEA[:, 0] > -5) & (SEA[:, 0] < 1196) & (SEA[:, 1] < 1640)]
if len(coast) > 3:
    seg = np.r_[0, np.cumsum(np.hypot(*np.diff(coast, axis=0).T))]
    s = np.arange(0, seg[-1], 2.0)
    C = np.c_[np.interp(s, seg, coast[:, 0]), np.interp(s, seg, coast[:, 1])]
    T = np.gradient(C, axis=0); T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-9
    Nn = np.c_[-T[:, 1], T[:, 0]]
    if inside(SEA, *(C[len(C) // 2] + Nn[len(C) // 2] * 6)) is False or not inside(SEA, *(C[len(C) // 2] + Nn[len(C) // 2] * 6)):
        Nn = -Nn
    for off, amp, hgt in ((4.5, 1.2, 0.12), (9.0, 1.8, 0.07)):
        wob = amp * np.sin(s / 7.0 + off)
        pts = C + Nn * (off + wob)[:, None]
        # R7SURF: 글 상자 둘레에서는 파도 띠를 끊음
        bad = np.array([any(z[0] - 6 < x < z[2] + 6 and z[1] - 6 < y < z[3] + 6 for z in FTXT) or near_pin(x, y) for x, y in pts])
        runs, cur = [], []
        for pt, b_ in zip(pts, bad):
            if b_:
                if len(cur) > 2: runs.append(np.array(cur))
                cur = []
            else:
                cur.append(pt)
        if len(cur) > 2: runs.append(np.array(cur))
        for rr in runs:
            stroke(rr, SEA_Z + 0.02, 0.3, hgt)
        continue
        # 오브젝트(바다 위 시설) 근처는 끊기 — 화면에서 오브젝트 상자 안이면 제외
        stroke(pts, SEA_Z + 0.02, 0.3, hgt)

# ---- 강 흐름 선 ----
n_riv = 0
for v in np.arange(-40, 1400, 9.0):
    for u in np.arange(20, 360, 9.0):
        x = u + rng.uniform(-3, 3); y = v + rng.uniform(-3, 3)
        if not inside(RIV, x, y):
            continue
        dist, tdir = nearest_seg(RIV, x, y)
        if dist < 3.5 or rng.random() > 0.55:
            continue
        ln = rng.uniform(6, 11)
        s = np.linspace(-0.5, 0.5, 6)
        pts = np.c_[x + tdir[0] * s * ln, y + tdir[1] * s * ln]
        stroke(pts, RIVER_Z + 0.02, 0.16, 0.05)
        n_riv += 1

U.remove_obj('W_water_marks')
ob = U.mesh_from_arrays('W_water_marks', np.concatenate(V), F, U.coll('30_TERRAIN'))
for p in ob.data.polygons:
    p.use_smooth = True
ob['low_terrain'] = True

# 수면 자체는 잔잔하게: 바다·강 메시의 높이를 평평하게(아주 약한 너울만)
for name, z0, amp in ():   # R6 수면은 평평(terrain.py tri_surface)
    o = bpy.data.objects.get(name)
    if not o:
        continue
    co = np.empty(len(o.data.vertices) * 3); o.data.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    co[:, 2] = z0 + amp * np.sin(co[:, 0] * 0.35 + co[:, 1] * 0.21)
    o.data.vertices.foreach_set('co', co.ravel()); o.data.update()
print('sea strokes', n_sea, 'river strokes', n_riv, 'tris', U.tri_count(ob))
