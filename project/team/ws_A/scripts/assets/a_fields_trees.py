"""워커 A — 밭·나무 재작성(비평 3·4: C1·C4, F후보). fill_plains.py 2·3절 대신 exec로 불림(U·rng·h_xy·wet_uv·near_obj·poly_dist·build·ROADS·ROAD_W·ZONES 공유).

밭(켄투리아티오)
- 판을 땅에 붙임: 바닥 띄움 0.05→0.025, 가장자리 둑(0.11 돋음) 없앰 → '공중에 뜬 판' 인상 제거
- 지역마다 격자 방향·구획 크기를 달리함(로마 식민시마다 centuriatio 방향이 달랐음) → 같은 판 무늬 반복 깨기
- 구획 성격: 섞어짓기 / 통밀밭 / 목초지 / 올리브 과수원 / 숲(소나무 무리) — 큰 덩어리와 작은 띠가 섞이게
- 포도: 못판 같은 기둥 격자 → 이랑 따라 이어진 낮은 덩굴 줄(F_vine_rows, 높이·굵기 흔들림)
- 올리브: 1.1 격자 단추 → 줄 방향·간격·크기를 흔든 작은 나무(줄기+둥근 수관, F_olive_trees), 15% 빠짐
- 구획 경계(limes) 일부에 생울타리(F_hedge, 울퉁불퉁한 낮은 둑 모양 수풀)
물체: F_centuriatio(이랑 밭 0.80) · F_pasture(0.92) · F_orchard(과수원 바닥 0.86) · F_vine_rows · F_olive_trees · F_hedge
나무
- 사이프러스: 줄기 + 둥근 밑동 수관(끝이 뾰족하게 떠서 밭을 뚫던 것 제거), 줄기는 땅속 0.25까지
- 밭 띠 위에는 나무를 심지 않음(STRIPS 검사)
- 길가: 일정 간격(리듬) — CORE 길 뒤쪽 편 사이프러스 가로수, 아피아 가도 소나무·사이프러스 교대, 오스티아 가도 소나무
- 구릉·숲 구획: 우산소나무 무리
"""
import json
import math
import bpy
import bmesh
import numpy as np
from mathutils import Vector, noise

# ---------------- 공용 ----------------
lo = U.pts_to_world(np.array([[0, 0], [1191, 0], [1191, 1684], [0, 1684]], float), 0.0)[:, :2]
LIMES = 0.5
SUB = 2.6
KEYS = ('F_centuriatio', 'F_pasture', 'F_orchard', 'F_vine_rows', 'F_olive_trees', 'F_hedge')
MV = {k: [] for k in KEYS}; MF = {k: [] for k in KEYS}; MN = {k: 0 for k in KEYS}


def add_mesh(key, V_, F_):
    V_ = np.asarray(V_, float); o_ = MN[key]
    MV[key].append(V_); MF[key].extend([tuple(int(x) + o_ for x in f) for f in (F_.tolist() if hasattr(F_, 'tolist') else F_)]); MN[key] += len(V_)


def add_grid(key, X, Y, Z):
    na, nb = X.shape
    I = np.arange(na * nb).reshape(na, nb)
    add_mesh(key, np.stack([X, Y, Z], -1).reshape(-1, 3), np.stack([I[:-1, :-1], I[1:, :-1], I[1:, 1:], I[:-1, 1:]], -1).reshape(-1, 4))


_TZ = json.load(open(ROOT + 'sketch_v2/text_zones.json'))
TALL_BOX = []
for _cn in ('20_LANDMARK', '40_REGION', '45_CORE_SCENES', '50_DETAIL_MODEL'):
    _c = bpy.data.collections.get(_cn)
    for _o in (_c.objects if _c else []):
        if _o.type == 'MESH' and not _o.hide_render and not _o.name.startswith(('L05_aqua', 'L01_')):
            TALL_BOX.append(U.screen_bbox(_o, 4))
PATH_PTS = np.concatenate([np.asarray(p, float) for p in json.load(open(ROOT + 'assets/core_path_uv.json'))])
SIMPLE_ZONES = [z for k, z in _TZ['zones'].items() if k.startswith(('CORE', 'DETAIL', 'SUPPORT'))] + \
               [_TZ['objects'][k] for k in ('D1_model', 'D2_model', 'D4_model')] + [[250, 1199, 412, 1337]] + \
               [[t['b'][0] - 8, t['b'][1] - 6, t['b'][2] + 8, t['b'][3] + 6] for t in json.load(open(ROOT + 'loop/figma_texts.json')) if t['kind'] not in ('header', 'title', 'timeline')]
SZ = np.array(SIMPLE_ZONES, float)
TB = np.array(TALL_BOX, float)
ROAD_ARR = [np.asarray(p, float) for p in ROADS.values()]


def in_frame_world(xy, pad=0.0):
    """세계 xy가 화면 프레임 사다리꼴(땅 z=0) 안인가 — 카메라 뒤·지평선 너머 점이 투영에서 엉뚱한 화면 좌표로 들어오던 것 막음"""
    xy = np.asarray(xy, float).reshape(-1, 2)
    P = lo; n = len(P); ins = np.ones(len(xy), bool)
    c = P.mean(0)
    for i in range(n):
        a, b = P[i], P[(i + 1) % n]
        e = b - a; nrm = np.array([-e[1], e[0]])
        if np.dot(c - a, nrm) < 0:
            nrm = -nrm
        ins &= ((xy - a) @ nrm) / np.linalg.norm(nrm) >= pad
    return ins


def uv_of(xy):
    xy = np.asarray(xy, float).reshape(-1, 2)
    return U.project_pts(np.c_[xy, np.zeros(len(xy))])


def road_d(u, v):
    return np.minimum.reduce([poly_dist(p, u, v) for p in ROAD_ARR])


def box_hit(boxes, u0, v0, u1, v1, pad):
    if len(boxes) == 0:
        return False
    return bool(((u1 > boxes[:, 0] - pad) & (u0 < boxes[:, 2] + pad) & (v1 > boxes[:, 1] - pad) & (v0 < boxes[:, 3] + pad)).any())


def rect_ok(c4uv, pad_zone=12.0, road_min=14.0, g9uv=None):
    """화면 상자 검사(글 자리·키 큰 물체·물·길·옛 점선 길)."""
    u0, v0 = c4uv[:, 0].min(), c4uv[:, 1].min(); u1, v1 = c4uv[:, 0].max(), c4uv[:, 1].max()
    if box_hit(SZ, u0, v0, u1, v1, pad_zone) or box_hit(TB, u0, v0, u1, v1, 3):
        return False
    if wet_uv(c4uv[:, 0], c4uv[:, 1]).any():
        return False
    g = c4uv if g9uv is None else g9uv
    if road_d(g[:, 0], g[:, 1]).min() < road_min:
        return False
    _in = (PATH_PTS[:, 0] > u0 - 10) & (PATH_PTS[:, 0] < u1 + 10) & (PATH_PTS[:, 1] > v0 - 10) & (PATH_PTS[:, 1] < v1 + 10)
    if _in.any():
        return False
    return (u0 > 3) and (u1 < 1188) and (v0 > 432) and (v1 < 1676)


STRIPS = []      # (cx, cy, ax, ay, w, L) — 나무가 밭을 뚫지 않게
HASH = {}        # 공간 해시(4단위 칸) → STRIPS 번호


def _corners(cx, cy, ax, ay, w, L):
    bx, by = -ay, ax
    return np.array([[cx + sb * ax * L / 2 + sa * bx * w / 2, cy + sb * ay * L / 2 + sa * by * w / 2] for sa, sb in ((-1, -1), (1, -1), (1, 1), (-1, 1))])


def _sat(P, Q):
    for poly in (P, Q):
        for i in range(4):
            e = poly[(i + 1) % 4] - poly[i]; nrm = np.array([-e[1], e[0]])
            a = P @ nrm; b = Q @ nrm
            if a.max() <= b.min() + 1e-6 or b.max() <= a.min() + 1e-6:
                return False
    return True


def overlaps_any(cx, cy, ax, ay, w, L, grow=0.05):
    P = _corners(cx, cy, ax, ay, w + grow, L + grow)
    keys = {(int(math.floor(x / 4.0)), int(math.floor(y / 4.0))) for x, y in P} | {(int(math.floor(cx / 4.0)), int(math.floor(cy / 4.0)))}
    cand = set()
    for (i, j) in keys:
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                cand |= HASH.get((i + di, j + dj), set())
    for k in cand:
        if _sat(P, _corners(*STRIPS[k])):
            return True
    return False


def register(cx, cy, ax, ay, w, L):
    k = len(STRIPS); STRIPS.append((cx, cy, ax, ay, w, L))
    for x, y in np.r_[_corners(cx, cy, ax, ay, w, L), [[cx, cy]]]:
        HASH.setdefault((int(math.floor(x / 4.0)), int(math.floor(y / 4.0))), set()).add(k)
WOOD = []        # 숲 구획 중심(세계 xy)과 축


# 올리브 나무 틀(수관 몇 가지)
def _ico(sub):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1.0)
    V_ = np.array([v.co[:] for v in bm.verts]); F_ = np.array([[v.index for v in f.verts] for f in bm.faces]); bm.free()
    return V_, F_


ICO1 = _ico(1); ICO2 = _ico(2)
OLV = []
for k in range(4):
    V_, F_ = ICO2
    V_ = V_.copy()
    for i in range(len(V_)):
        V_[i] *= 1.0 + 0.22 * noise.noise(Vector(V_[i] * 1.9 + Vector((k * 3.1, 0, 0))))
    OLV.append((V_, F_))


def olive_tree(x, y, z, r):
    V_, F_ = OLV[int(rng.integers(0, len(OLV)))]
    cv = V_ * np.array([r, r, 0.78 * r]) + np.array([x, y, z + 0.16 + 0.7 * r])
    add_mesh('F_olive_trees', cv, F_)
    # 줄기(4각)
    t = np.array([[x + 0.05 * math.cos(a), y + 0.05 * math.sin(a)] for a in np.linspace(0, 2 * math.pi, 4, endpoint=False)])
    tv = np.r_[np.c_[t, np.full(4, z - 0.05)], np.c_[t, np.full(4, z + 0.2 + 0.5 * r)]]
    add_mesh('F_olive_trees', tv, [(i, (i + 1) % 4, 4 + (i + 1) % 4, 4 + i) for i in range(4)])


def vine_row(p0, p1, z_fn, seed):
    """p0→p1(세계 xy) 덩굴 줄: 둥근 삼각 단면, 높이·굵기 흔들림"""
    L = float(np.linalg.norm(p1 - p0))
    if L < 0.6:
        return
    t = (p1 - p0) / L; n = np.array([-t[1], t[0]])
    ss = np.linspace(0, L, max(3, int(L / 0.22)))
    prof = [(-1.0, 0.0), (-0.55, 0.62), (0.0, 1.0), (0.55, 0.62), (1.0, 0.0)]
    V_ = []
    for s_ in ss:
        c = p0 + t * s_
        z = z_fn(c)
        hh = 0.20 + 0.07 * noise.noise(Vector((s_ * 1.7, seed, 0.3)))
        ww = 0.10 + 0.03 * noise.noise(Vector((s_ * 2.3, seed, 1.7)))
        tap = min(1.0, s_ / 0.25, (L - s_) / 0.25) ** 0.5
        for a, b in prof:
            V_.append((c[0] + n[0] * a * ww, c[1] + n[1] * a * ww, z + 0.02 + b * hh * tap))
    m = len(prof); F_ = []
    for j in range(len(ss) - 1):
        for k in range(m - 1):
            a0 = j * m + k; b0 = a0 + m
            F_.append((a0, a0 + 1, b0 + 1, b0))
    add_mesh('F_vine_rows', V_, F_)


def z_at(c):
    return float(h_xy(np.array([c]))[0][0])


def strip(cx, cy, ax, ay, w, L, kind, prm):
    bx, by = -ay, ax
    if kind == 'fallow' or w < 0.9 or L < 0.9:
        return False
    c4 = np.array([[cx + sb * ax * L / 2 + sa * bx * w / 2, cy + sb * ay * L / 2 + sa * by * w / 2] for sa in (-1, 1) for sb in (-1, 1)])
    g9 = np.array([[cx + sb * ax * L / 2 + sa * bx * w / 2, cy + sb * ay * L / 2 + sa * by * w / 2] for sa in (-1, 0, 1) for sb in (-1, 0, 1)])
    if not in_frame_world(c4).all() or not rect_ok(uv_of(c4), g9uv=uv_of(g9)):
        return False
    if float(h_xy(g9)[0].min()) < 0.02:          # 물가 비탈(모래사장·강둑) 위엔 밭 없음
        return False
    if overlaps_any(cx, cy, ax, ay, w, L, grow=-0.04):
        return False
    na = max(2, int(w / (0.30 if kind == 'furrow' else 0.7)))
    nb = max(2, int(L / 0.8))
    A = np.linspace(-w / 2, w / 2, na + 1); B = np.linspace(-L / 2, L / 2, nb + 1)
    aa, bb = np.meshgrid(A, B, indexing='ij')
    X = cx + bb * ax + aa * bx; Y = cy + bb * ay + aa * by
    z, _ = h_xy(np.stack([X, Y], -1))
    if kind == 'furrow':
        rid = 0.045 * (np.arange(na + 1) % 2)[:, None] * np.ones_like(bb)
        add_grid('F_centuriatio', X, Y, z + 0.025 + rid)
    elif kind == 'pasture':
        add_grid('F_pasture', X, Y, z + 0.035)
        # 목초지 표시: 드문 덤불(관목) 몇 점 — 빈 종이판처럼 보이지 않게
        for _ in range(int(w * L * 0.07 + rng.random())):
            a_, b_ = rng.uniform(-w / 2 + 0.3, w / 2 - 0.3), rng.uniform(-L / 2 + 0.3, L / 2 - 0.3)
            x0, y0 = cx + b_ * ax + a_ * bx, cy + b_ * ay + a_ * by
            rr = rng.uniform(0.14, 0.24)
            V_, F_ = OLV[int(rng.integers(0, len(OLV)))]
            add_mesh('F_hedge', V_ * np.array([rr * 1.2, rr * 1.2, rr * 0.8]) + np.array([x0, y0, z_at((x0, y0)) + 0.05]), F_)
    else:
        add_grid('F_orchard', X, Y, z + 0.022)
    register(cx, cy, ax, ay, w, L)
    if kind == 'vine':
        sp = prm['vine_sp']
        for a_ in np.arange(-w / 2 + sp * 0.6, w / 2 - sp * 0.3, sp):
            p0 = np.array([cx + (-L / 2 + 0.2) * ax + a_ * bx, cy + (-L / 2 + 0.2) * ay + a_ * by])
            p1 = np.array([cx + (L / 2 - 0.2) * ax + a_ * bx, cy + (L / 2 - 0.2) * ay + a_ * by])
            vine_row(p0, p1, z_at, float(rng.uniform(0, 100)))
    elif kind == 'olive':
        sp = prm['olive_sp']; rr = prm['olive_r']
        rows = np.arange(-w / 2 + sp * 0.55, w / 2 - sp * 0.3, sp * 0.87)
        for ri, a_ in enumerate(rows):
            for b_ in np.arange(-L / 2 + sp * 0.5 + (ri % 2) * sp * 0.5, L / 2 - sp * 0.3, sp):
                if rng.random() < 0.25:
                    continue
                ja = a_ + rng.normal(0, 0.18); jb = b_ + rng.normal(0, 0.22)
                x0, y0 = cx + jb * ax + ja * bx, cy + jb * ay + ja * by
                olive_tree(x0, y0, z_at((x0, y0)), rr * rng.uniform(0.75, 1.2))
    return True


def hedge(p0, p1, seed):
    """구획 경계 생울타리: p0→p1, 표본마다 검사해서 이어진 구간만"""
    L = float(np.linalg.norm(p1 - p0))
    t = (p1 - p0) / max(L, 1e-9); n = np.array([-t[1], t[0]])
    ss = np.arange(0.2, L - 0.2, 0.28)
    if len(ss) < 4:
        return 0
    C_ = p0[None, :] + t[None, :] * ss[:, None]
    zz, q = h_xy(C_)
    ok = ~wet_uv(q[:, 0], q[:, 1]) & ~near_obj(q[:, 0], q[:, 1], 10) & (road_d(q[:, 0], q[:, 1]) > 13) & in_frame_world(C_)
    for i in range(len(ss)):
        if ok[i] and (on_strip(C_[i, 0], C_[i, 1], -0.02) or not on_strip(C_[i, 0], C_[i, 1], 0.9)):
            ok[i] = False
    for i in range(len(ss)):
        if ok[i] and (box_hit(SZ, q[i, 0] - 3, q[i, 1] - 6, q[i, 0] + 3, q[i, 1], 8) or box_hit(TB, q[i, 0] - 3, q[i, 1] - 6, q[i, 0] + 3, q[i, 1], 3)
                      or q[i, 0] < 4 or q[i, 0] > 1187 or q[i, 1] < 436 or q[i, 1] > 1674):
            ok[i] = False
    runs, cur = [], []
    for i in range(len(ss)):
        if ok[i]:
            cur.append(i)
        else:
            if len(cur) >= 5:
                runs.append(cur)
            cur = []
    if len(cur) >= 5:
        runs.append(cur)
    prof = [(-1.0, -0.06), (-0.92, 0.35), (-0.6, 0.8), (0.0, 1.0), (0.6, 0.8), (0.92, 0.35), (1.0, -0.06)]
    nn = 0
    for run in runs:
        V_ = []
        for j, i in enumerate(run):
            s_ = ss[i]; c = C_[i]; z = zz[i]
            bead = 0.62 + 0.38 * abs(math.sin(math.pi * s_ / 0.62 + seed))      # 덤불이 구슬처럼 이어진 줄
            ww = (0.17 + 0.04 * noise.noise(Vector((s_ * 2.6, seed, 0.5)))) * (0.75 + 0.25 * bead)
            hh = (0.30 + 0.08 * noise.noise(Vector((s_ * 2.2, seed, 2.5)))) * bead
            tap = min(1.0, (j + 0.5) / 2.0, (len(run) - j - 0.5) / 2.0)
            for a, b in prof:
                V_.append((c[0] + n[0] * a * ww, c[1] + n[1] * a * ww, z + (b * hh * tap if b > 0 else b)))
        m = len(prof); F_ = []
        for j in range(len(run) - 1):
            for k in range(m - 1):
                a0 = j * m + k; b0 = a0 + m
                F_.append((a0, a0 + 1, b0 + 1, b0))
        F_.append(tuple(range(m - 1, -1, -1)))
        F_.append(tuple((len(run) - 1) * m + k for k in range(m)))
        add_mesh('F_hedge', V_, F_); nn += 1
    return nn


def ok_pts(xy):
    hz, uv = h_xy(xy)
    u, v = uv[..., 0], uv[..., 1]
    rd = road_d(u, v)
    return (u > 4) & (u < 1187) & (v > 430) & (v < 1676) & ~wet_uv(u, v) & ~near_obj(u, v, 12) & (rd > 12) & (hz < 1.9)


# ---------------- 2. 켄투리아티오: 지역별 격자 ----------------
rng = np.random.default_rng(int(globals().get('FIELD_SEED', 31)))   # 밭 전용 난수(길·나무 변경이 밭 배치를 흔들지 않게)
REGIONS = [   # (이름, 화면 판정, 격자 방향°, 구획 한 변, 원점 밀기)
    ('NE', lambda u, v: u >= 760 and v < 960, 0.0, 10.4, (0.0, 0.0)),
    ('NW', lambda u, v: u < 760 and v < 960, 12.0, 9.0, (2.1, 3.3)),
    ('SW', lambda u, v: u < 520 and v >= 960, -15.0, 8.2, (1.2, 4.4)),
    # SC(520~880 × 960~): CORE ③④·DETAIL ③④ 글과 모형이 모인 정보 구역 — 밭을 두지 않음(흩어진 판이 눈을 끌던 것)
    ('SE', lambda u, v: u >= 880 and v >= 960, -9.0, 11.4, (5.2, 2.8)),
]
CW = lo.mean(0)
R_ext = float(np.max(np.linalg.norm(lo - CW, axis=1))) + 12
n_cent = 0; n_hedge = 0; kinds_count = {}; HEDGE_CAND = []
for rname, rtest, ang, CENT, (sx_, sy_) in REGIONS:
    th = math.radians(ang); ex = np.array([math.cos(th), math.sin(th)]); ey = np.array([-math.sin(th), math.cos(th)])
    O = CW + ex * sx_ + ey * sy_
    nr = int(R_ext / CENT) + 1
    prm = {'vine_sp': float(rng.uniform(0.46, 0.6)), 'olive_sp': float(rng.uniform(1.3, 1.65)), 'olive_r': float(rng.uniform(0.27, 0.36))}
    for i in range(-nr, nr):
        for j in range(-nr, nr):
            side = CENT - LIMES
            p00 = O + ex * (i * CENT + LIMES / 2) + ey * (j * CENT + LIMES / 2)
            cen = p00 + ex * side / 2 + ey * side / 2
            if not in_frame_world(cen)[0]:
                continue
            cu = uv_of(cen)[0]
            if not rtest(cu[0], cu[1]):
                continue
            corners = np.array([p00, p00 + ex * side, p00 + ex * side + ey * side, p00 + ey * side, cen])
            okc = ok_pts(corners)
            if okc.sum() < 2:
                continue
            roll = rng.random()
            ctype = 'skip' if roll < 0.08 else 'mixed' if roll < 0.60 else 'grain' if roll < 0.74 else 'pasture' if roll < 0.83 else 'orchard' if roll < 0.92 else 'wood'
            kinds_count[ctype] = kinds_count.get(ctype, 0) + 1
            if ctype == 'skip':
                continue
            if ctype == 'wood':
                WOOD.append((cen, ex, ey, side)); continue
            n_cent += 1
            along_x = rng.random() < 0.5
            if ctype == 'mixed':
                k = int(rng.integers(2, 5)); ws = rng.dirichlet(np.ones(k) * 2.5) * side
                kinds = list(rng.choice(['furrow', 'furrow', 'vine', 'olive', 'pasture', 'fallow'], size=k, p=[0.32, 0.1, 0.2, 0.14, 0.14, 0.1]))
            elif ctype == 'grain':
                k = int(rng.integers(1, 3)); ws = rng.dirichlet(np.ones(k) * 4) * side; kinds = ['furrow'] * k
            elif ctype == 'pasture':
                ws = [side]; kinds = ['pasture']
            else:
                ws = [side]; kinds = ['olive']
            off = 0.0; n_put = 0; n_try = 0
            snap = ({k_: (len(MV[k_]), len(MF[k_]), MN[k_]) for k_ in KEYS}, len(STRIPS))
            ax_, ay_ = (ex if along_x else ey)
            bx_, by_ = (ey if along_x else ex)
            for w, kind in zip(ws, kinds):
                for sb in np.arange(0, side - 1e-6, SUB):
                    L = min(SUB, side - sb)
                    c = p00 + np.array([ax_, ay_]) * (sb + L / 2) + np.array([bx_, by_]) * (off + w / 2)
                    if not ok_pts(np.array([c]))[0]:
                        continue
                    if kind != 'fallow':
                        n_try += 1
                    n_put += bool(strip(c[0], c[1], ax_, ay_, w, L, kind, prm))
                off += w
            # 구획이 조각나면(놓인 띠 < 60%) 통째로 버림 — 흩어진 종잇조각 대신 온전한 네모 구획만
            if n_put < 4 or n_put < 0.7 * max(1, n_try):
                for k_ in KEYS:
                    a_, b_, c_ = snap[0][k_]
                    del MV[k_][a_:]; del MF[k_][b_:]; MN[k_] = c_
                for kk in range(snap[1], len(STRIPS)):
                    for key_, st in list(HASH.items()):
                        st.discard(kk)
                del STRIPS[snap[1]:]
                n_cent -= 1
                continue
            # 생울타리: 네 변 중 일부(로마 농촌의 구획 경계 수풀)
            edges = [(p00 - ey * LIMES / 2, p00 + ex * side - ey * LIMES / 2), (p00 + ex * (side + LIMES / 2), p00 + ex * (side + LIMES / 2) + ey * side),
                     (p00 + ey * (side + LIMES / 2), p00 + ex * side + ey * (side + LIMES / 2)), (p00 - ex * LIMES / 2, p00 - ex * LIMES / 2 + ey * side)]
            for e0, e1 in edges:
                if rng.random() < 0.38:
                    HEDGE_CAND.append((np.asarray(e0), np.asarray(e1), float(rng.uniform(0, 100))))

STR = np.array(STRIPS) if STRIPS else np.zeros((0, 6))


def on_strip(x, y, margin=0.35):
    if len(STR) == 0:
        return False
    dx = x - STR[:, 0]; dy = y - STR[:, 1]
    along = np.abs(dx * STR[:, 2] + dy * STR[:, 3]); across = np.abs(-dx * STR[:, 3] + dy * STR[:, 2])
    return bool(((along < STR[:, 5] / 2 + margin) & (across < STR[:, 4] / 2 + margin)).any())


for e0, e1, sd in HEDGE_CAND:
    n_hedge += hedge(e0, e1, sd)
FIELD_OBS = {}
for key in KEYS:
    U.remove_obj(key)
    if not MV[key]:
        continue
    fv = np.concatenate(MV[key])
    faces = [tuple(dict.fromkeys(f)) for f in MF[key]]
    ob = build(key, fv, faces, '35_FIELDS_ROADS', low=True)
    if key in ('F_olive_trees', 'F_hedge', 'F_vine_rows'):
        for p in ob.data.polygons:
            p.use_smooth = True
    FIELD_OBS[key] = ob
U.remove_obj('F_centuriatio') if 'F_centuriatio' not in FIELD_OBS else None
fields = FIELD_OBS.get('F_centuriatio')
ok = np.array([n_cent])
print('fields: centuriae', n_cent, 'kinds', kinds_count, 'hedges', n_hedge, {k: U.tri_count(o) for k, o in FIELD_OBS.items()})

# ---------------- 3. 나무 ----------------
rng = np.random.default_rng(47)   # 나무 전용 난수
def make_pine(seed, height=5.2, crown=4.6):
    r = np.random.default_rng(seed)
    bm = bmesh.new()
    lean = Vector((r.uniform(-0.25, 0.25), r.uniform(-0.25, 0.25), 0))
    rings = []
    for k in range(7):
        t = k / 6
        c = Vector((0, 0, -0.3 + t * (height * 0.56 + 0.3))) + lean * (t * t) * height * 0.3
        rad = 0.26 * (1 - 0.55 * t)
        rings.append([bm.verts.new(c + Vector((rad * math.cos(a), rad * math.sin(a), 0))) for a in np.linspace(0, 2 * math.pi, 8, endpoint=False)])
    for r0, r1 in zip(rings[:-1], rings[1:]):
        for i in range(8):
            bm.faces.new((r0[i], r0[(i + 1) % 8], r1[(i + 1) % 8], r1[i]))
    top = Vector((0, 0, height * 0.56)) + lean * height * 0.3
    for j in range(7):
        ang = j / 7 * 2 * math.pi + r.uniform(-0.3, 0.3)
        rr = 0 if j == 0 else crown * 0.28 * r.uniform(0.7, 1.0)
        cpos = top + Vector((rr * math.cos(ang), rr * math.sin(ang), r.uniform(0.1, 0.45)))
        sz = crown * (0.42 if j == 0 else 0.30) * r.uniform(0.85, 1.1)
        res = bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)
        for v in res['verts']:
            p = v.co.copy()
            n = noise.noise(p * 1.7 + Vector((seed, j, 0))) * 0.18
            v.co = Vector((p.x * sz * (1 + n), p.y * sz * (1 + n), p.z * sz * 0.32 * (1 + n))) + cpos
    me = bpy.data.meshes.new('TREE_pine_%d' % seed)
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return me


def make_cypress(seed, height=5.6):
    """줄기(땅속 -0.3 ~ 0.9) + 둥근 밑동에서 뾰족한 끝으로 가는 수관(밑동 z 0.55)"""
    r = np.random.default_rng(seed)
    bm = bmesh.new()
    ring = []
    for z_ in (-0.3, 0.95):
        ring.append([bm.verts.new((0.13 * math.cos(a), 0.13 * math.sin(a), z_)) for a in np.linspace(0, 2 * math.pi, 7, endpoint=False)])
    for i in range(7):
        bm.faces.new((ring[0][i], ring[0][(i + 1) % 7], ring[1][(i + 1) % 7], ring[1][i]))
    res = bmesh.ops.create_icosphere(bm, subdivisions=4, radius=1.0)
    R0 = 0.62 * r.uniform(0.92, 1.08)
    for v in res['verts']:
        p = v.co.copy()
        t = (p.z + 1) / 2                                  # 0 밑 ~ 1 끝
        prof = min(1.0, (t / 0.16) ** 0.5) * (1 - t) ** 0.8   # 둥근 밑동 → 뾰족한 끝
        n = noise.noise(p * 3.1 + Vector((seed, 0, 0))) * 0.13
        rad = math.hypot(p.x, p.y) + 1e-9
        v.co = Vector((p.x / rad * R0 * prof * (1 + n) if rad > 1e-6 else 0.0, p.y / rad * R0 * prof * (1 + n) if rad > 1e-6 else 0.0, 0.55 + t * (height - 0.55)))
    me = bpy.data.meshes.new('TREE_cypress_%d' % seed)
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return me


TC = U.coll('60_TREES')
for o in list(TC.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for me in [m for m in bpy.data.meshes if m.name.startswith('TREE_') and m.users == 0]:
    bpy.data.meshes.remove(me)
PINES = [make_pine(s, height=5.2 * k_, crown=4.9) for s, k_ in ((1, 1.0), (2, 0.9), (3, 1.1), (7, 0.95), (8, 1.05))]
CYPR = [make_cypress(s) for s in (4, 5, 6)]
OBJ_BOX = []
for cn in ('20_LANDMARK', '40_REGION', '45_CORE_SCENES', '50_DETAIL_MODEL'):
    col = bpy.data.collections.get(cn)
    for o in (col.objects if col else []):
        if o.type == 'MESH' and not o.hide_render:
            OBJ_BOX.append(U.screen_bbox(o, 4))
PIN_SEGS = [((240, 1533), (198, 1497)), ((590, 1497.8), (590, 1536.9)), ((724, 1545), (724, 1482)), ((897, 1062), (1024, 1062))]
PLANTED = []
# OCC: 큰 물체(콜로세움·수도교·봉우리·베수비오 등)는 화면 상자 대신 투영 꼭짓점 점유 격자(2pt, 6pt 넓힘) — 상자 안 빈 땅에도 나무를 심을 수 있게
OCC = np.zeros((600, 850), bool)
SMALL_BOX = []
for cn in ('20_LANDMARK', '40_REGION', '45_CORE_SCENES', '50_DETAIL_MODEL'):
    col = bpy.data.collections.get(cn)
    for o in (col.objects if col else []):
        if o.type != 'MESH' or (o.hide_render and not o.name.startswith('L01_')):   # 땅에 합친 봉우리(숨김)도 점유로
            continue
        bb = U.screen_bbox(o, 4)
        if (bb[2] - bb[0]) * (bb[3] - bb[1]) < 9000 or len(o.data.vertices) < 3000:
            SMALL_BOX.append(bb); continue
        q = U.project_pts(U.eval_world_coords(o, 1))
        qi = np.clip((q[:, 0] / 2).astype(int), 0, 599); qj = np.clip((q[:, 1] / 2).astype(int), 0, 849)
        OCC[qi, qj] = True
_o = OCC.copy()
for di in range(-3, 4):
    for dj in range(-3, 4):
        OCC |= np.roll(np.roll(_o, di, 0), dj, 1)
OBJ_BOX = SMALL_BOX


def occ_hit(u0, v0, u1, v1):
    i0, i1 = max(0, int(u0 / 2)), min(599, int(u1 / 2) + 1); j0, j1 = max(0, int(v0 / 2)), min(849, int(v1 / 2) + 1)
    return bool(OCC[i0:i1, j0:j1].any())


REJ = {}


def _rej(k):
    REJ[k] = REJ.get(k, 0) + 1
    return None


def plant(kind, xy, scale=1.0, road_min=24.0, allow_strip=False):
    if not in_frame_world(xy)[0]:
        return _rej('outside')
    z, uv = h_xy(np.array([xy]))
    u, v = uv[0]
    if float(z[0]) < 0.02:
        return _rej('beach')
    if wet_uv(u, v) or u < 6 or u > 1185 or v > 1675:
        return _rej('wet/frame')
    if near_obj(u, v, 6):
        return _rej('near_obj')
    _ang = np.linspace(0, 2 * math.pi, 8, endpoint=False)
    if wet_uv(u + 12 * np.cos(_ang), v + 12 * np.sin(_ang)).any():
        return _rej('near_wet')
    if float(road_d(np.array([u]), np.array([v]))[0]) < road_min:
        return _rej('road')
    if not allow_strip and on_strip(xy[0], xy[1], 0.35 + (1.3 if kind == 'pine' else 0.4) * scale):
        return _rej('strip')
    _rk = 1.6 if kind == 'pine' else 0.7
    for (px, py, ps, pk) in PLANTED:                   # 나무끼리 겹침 방지(소나무 수관 1.6, 사이프러스 0.7 반지름 기준)
        need = (_rk * scale + (1.6 if pk == 'pine' else 0.7) * ps) * (0.58 if (kind == 'pine' and pk == 'pine') else 0.95)
        if math.hypot(px - xy[0], py - xy[1]) < need:
            return _rej('tree')
    _r = float(U.rise_per_unit(np.array([[u, v]]))[0])
    if u - 2.6 * scale * _r < 4 or u + 2.6 * scale * _r > 1187 or v - 6.2 * scale * _r < 260:
        return _rej('frame2')
    me = (PINES if kind == 'pine' else CYPR)[rng.integers(0, len(PINES) if kind == 'pine' else len(CYPR))]
    rise = _r
    hgt = 5.6 * scale
    wpt = (2.4 if kind == 'pine' else 0.7) * scale * rise
    for zb in ZONES.values():
        if u + wpt > zb[0] - 3 and u - wpt < zb[2] + 3 and v > zb[1] - 3 and v - hgt * rise < zb[3] + 3:
            return _rej('zone')
    for bb in OBJ_BOX:
        if u + wpt > bb[0] - 6 and u - wpt < bb[2] + 6 and v > bb[1] - 4 and v - hgt * rise < bb[3] + 6:
            return _rej('objbox')
    if occ_hit(u - wpt, v - hgt * rise, u + wpt, v + 2):
        return _rej('occ')
    ob = bpy.data.objects.new(('T_pine' if kind == 'pine' else 'T_cypress'), me)
    TC.objects.link(ob)
    ob.location = (xy[0], xy[1], float(z[0]) - 0.02)
    ob.rotation_euler = (0, 0, rng.uniform(0, 2 * math.pi))
    ob.scale = (scale, scale, scale * rng.uniform(0.92, 1.08))
    PLANTED.append((xy[0], xy[1], scale, kind))
    return ob


n_tree = 0
# (1) 길가 가로수 — 일정 간격(리듬), 화면 뒤쪽 편만(앞쪽 수관은 길을 가림)
AVENUE = {'R_core_road': (4.6, 'cypress', 0.74, 1.5), 'R_via_appia': (3.2, 'alt', 0.66, 1.25), 'R_via_ostiensis': (3.6, 'cypress', 0.66, 1.2)}
for name, pts in ROADS.items():
    if name not in AVENUE:
        continue
    sp, kind0, sc0, off0 = AVENUE[name]
    P = U.pts_to_world(np.asarray(pts, float), 0.0)[:, :2]
    seg = np.r_[0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]
    k_ = 0
    for s in np.arange(3.0, seg[-1] - 2.0, sp):
        c = np.array([np.interp(s, seg, P[:, 0]), np.interp(s, seg, P[:, 1])])
        i = min(np.searchsorted(seg, s), len(P) - 1); t = P[i] - P[max(i - 1, 0)]; t /= np.linalg.norm(t) + 1e-9
        nrm = np.array([-t[1], t[0]])
        for sgn in (-1, 1):
            _uvq = U.project_pts(np.array([[*(c + nrm * sgn * 3.0), 0.0], [c[0], c[1], 0.0]]))
            if _uvq[0, 1] > _uvq[1, 1]:
                continue
            kind = ('cypress' if k_ % 2 == 0 else 'pine') if kind0 == 'alt' else kind0
            wd = ROAD_W[name] / 2 + off0 + (0.9 if kind == 'pine' else 0.0)
            if plant(kind, c + nrm * sgn * wd, sc0 * rng.uniform(0.94, 1.06), road_min=(10.0 if kind == 'cypress' else 20.0)):
                n_tree += 1
        k_ += 1
n_av = n_tree
# (2) 숲 구획: 우산소나무 무리(구획 안 0.6 간격 무작위, 가장자리 비움)
for cen, ex, ey, side in WOOD:
    for _ in range(int(rng.integers(5, 10))):
        a, b = rng.uniform(-side * 0.36, side * 0.36, 2)
        if plant('pine', cen + ex * a + ey * b, rng.uniform(0.46, 0.62)):
            n_tree += 1
n_wood = n_tree - n_av
# (3) 구릉: 높이 0.8~2.6 언덕에 소나무 무리 + 드문 사이프러스
gx, gy = np.meshgrid(np.arange(lo[:, 0].min(), lo[:, 0].max(), 3.0), np.arange(lo[:, 1].min(), lo[:, 1].max(), 3.0), indexing='ij')
gxy = np.stack([gx, gy], -1).reshape(-1, 2)
hc, uvc = h_xy(gxy); v_ = uvc[:, 1]
cand = gxy[(hc > 0.7) & (hc < 2.8) & (v_ > 340) & (v_ < 1440) & (uvc[:, 0] > 12) & (uvc[:, 0] < 1179)]   # 산맥 아래 비탈(v 340~)에도 소나무 숲
rng.shuffle(cand)
# 정해 둔 숲 자리(화면 pt): 알바노 구릉·남서 해안 평야·북서 구릉·포룸 둘레·북동 끝·남쪽 해안 — 빈 땅에 덩어리 숲(리듬)
GROVES = [(880, 1125), (955, 1180), (865, 1250), (1015, 1110), (1095, 1165), (1150, 1235), (1070, 1300), (930, 1300),
          (45, 1175), (115, 1235), (55, 1300), (160, 1300), (210, 1225),
          (35, 520), (95, 600), (175, 640), (30, 680),
          (275, 490), (265, 600), (395, 485),
          (1150, 690), (1165, 780), (1105, 840), (1160, 880),
          (455, 1440), (560, 1360), (640, 1400), (420, 1380)]
for gu, gv in GROVES:
    c = U.pts_to_world(np.array([[gu, gv]], float), 0.0)[0, :2]
    for _ in range(int(rng.integers(5, 9))):
        if plant('pine', c + rng.normal(0, 1.15, 2), rng.uniform(0.48, 0.62)):
            n_tree += 1
    for _ in range(int(rng.integers(0, 3))):
        a = rng.uniform(0, 2 * math.pi)
        if plant('cypress', c + 2.8 * np.array([math.cos(a), math.sin(a)]), rng.uniform(0.7, 0.88)):
            n_tree += 1
n_grove = n_tree - n_av - n_wood
CENTERS = []
for c in cand:
    if len(CENTERS) >= 48:
        break
    if all(np.hypot(*(c - q)) > 7.5 for q in CENTERS):
        CENTERS.append(c)
for c in CENTERS:
    for _ in range(int(rng.integers(4, 9))):
        if plant('pine', c + rng.normal(0, 1.05, 2), rng.uniform(0.48, 0.62)):
            n_tree += 1
    for _ in range(int(rng.integers(0, 3))):
        a = rng.uniform(0, 2 * math.pi)
        if plant('cypress', c + 2.6 * np.array([math.cos(a), math.sin(a)]), rng.uniform(0.7, 0.88)):
            n_tree += 1
# (4) 도심·유적 둘레 사이프러스
for uvp in [(520, 600), (560, 590), (720, 640), (780, 700), (300, 940), (330, 980), (470, 1000), (690, 1020), (606, 560), (845, 820), (884, 760)]:
    w = U.pts_to_world(np.array([uvp], float), 0.0)[0, :2]
    if plant('cypress', w, 0.8):
        n_tree += 1

ROAD_SCREEN = []
for _p in ROAD_ARR:
    _P = np.asarray(_p, float); _sg = np.r_[0, np.cumsum(np.hypot(*np.diff(_P, axis=0).T))]; _ss = np.arange(0, _sg[-1], 1.0)
    ROAD_SCREEN.append(np.c_[np.interp(_ss, _sg, _P[:, 0]), np.interp(_ss, _sg, _P[:, 1])])
removed_t = 0
for t in [o for o in TC.objects]:
    bb = U.screen_bbox(t, 1)
    bad = any(bb[2] > z[0] - 2 and bb[0] < z[2] + 2 and bb[3] > z[1] - 2 and bb[1] < z[3] + 2 for z in ZONES.values())
    bad = bad or any(bb[2] > b[0] - 2 and bb[0] < b[2] + 2 and bb[3] > b[1] - 2 and bb[1] < b[3] + 2 for b in OBJ_BOX) or occ_hit(*bb)
    bad = bad or bb[0] < 4 or bb[2] > 1187 or bb[1] < 258
    bad = bad or any(bb[2] > min(a_[0], b_[0]) - 4 and bb[0] < max(a_[0], b_[0]) + 4 and bb[3] > min(a_[1], b_[1]) - 4 and bb[1] < max(a_[1], b_[1]) + 4 for a_, b_ in PIN_SEGS)
    # 길 앞(화면 아래쪽)에 서서 길을 가리는 나무: 길 가운데선 점이 나무 상자 가로 범위 안이고 나무 밑동보다 위(뒤)에 있지 않으면
    if not bad:
        for _rp in ROAD_SCREEN:
            m_ = (_rp[:, 0] > bb[0] + 1) & (_rp[:, 0] < bb[2] - 1) & (_rp[:, 1] > bb[1]) & (_rp[:, 1] < bb[3] + 3)
            if m_.any():
                bad = True; break
    if bad:
        bpy.data.objects.remove(t, do_unlink=True); removed_t += 1; n_tree -= 1
print('trees: avenue', n_av, 'wood', n_wood, 'grove', n_grove, 'total', n_tree, 'removed by postcheck', removed_t, 'reject', REJ)
tri_tree = sum(len(m.polygons) for m in PINES + CYPR)
