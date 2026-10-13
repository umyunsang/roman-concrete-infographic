"""빈 평야 채우기 (2026-10-07 14:25 사용자: "빈 평야에 채우는 작업 진행해 — 지금은 빈 캔버스 같아")
- 로마 가도: 아피아 가도(로마 → 남동, 알바노 구릉 서쪽 기슭 → 프리베르눔 쪽), 오스티아 가도(로마 → 티베르강 동쪽 둑 → 포르투스)
  포장석(현무암 다각 돌) 블록 + 양쪽 연석, 땅 높이를 따라 깔림
- 켄투리아티오(로마 농지 구획): 세계 X/Y 축(화면 ±30°) 격자 밭 — 이랑 밭·포도밭·목초지, 둑
- 나무: 우산소나무(Pinus pinea)·사이프러스 — 가도 양옆 줄, 언덕 숲
모두 T_land 높이(assets/terrain_hf.npz)를 따라 놓는다. 글 자리(text_zones)에는 나무를 두지 않음(밭·길은 허용 = 낮은 지형).
Blender에서: exec(open(<이 파일>).read())
"""
import json
import math
import bpy
import bmesh
import numpy as np
from mathutils import Vector, Matrix, noise

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_probe/'
U = bpy.data.texts['asset_utils.py'].as_module()
rng = np.random.default_rng(11)
D = np.load(ROOT + 'assets/terrain_hf.npz')
HG, WET = D['h'].astype(np.float64), (D['river'] | D['sea'])
G0 = float(D['u'][0, 0]); GS = float(D['u'][1, 0] - D['u'][0, 0])
ZONES = {k: z for k, z in json.load(open(ROOT + 'sketch_v2/text_zones.json'))['zones'].items() if k not in ('TITLE_BAND', 'TIMELINE')}
# FIGMA_TEXT: v7의 실제 글 상자(loop/figma_texts.json)도 피함 — 지명·라벨 포함
for t in json.load(open(ROOT + 'loop/figma_texts.json')):
    ZONES['F_' + t['id']] = [t['b'][0] - 4, t['b'][1] - 4, t['b'][2] + 4, t['b'][3] + 4]
FOOT = json.load(open(ROOT + 'assets/object_footprints.json'))


def h_uv(u, v):
    fi = (np.asarray(u) - G0) / GS; fj = (np.asarray(v) - G0) / GS
    i0 = np.clip(np.floor(fi).astype(int), 0, HG.shape[0] - 2); j0 = np.clip(np.floor(fj).astype(int), 0, HG.shape[1] - 2)
    a = np.clip(fi - i0, 0, 1); b = np.clip(fj - j0, 0, 1)
    return (HG[i0, j0] * (1 - a) + HG[i0 + 1, j0] * a) * (1 - b) + (HG[i0, j0 + 1] * (1 - a) + HG[i0 + 1, j0 + 1] * a) * b


def wet_uv(u, v):
    i = np.clip(np.round((np.asarray(u) - G0) / GS).astype(int), 0, WET.shape[0] - 1)
    j = np.clip(np.round((np.asarray(v) - G0) / GS).astype(int), 0, WET.shape[1] - 1)
    return WET[i, j]


def h_xy(xy):
    """세계 xy 배열 (...,2) → 땅 높이"""
    xy = np.asarray(xy, dtype=np.float64)
    flat = xy.reshape(-1, 2)
    uv = U.project_pts(np.c_[flat, np.zeros(len(flat))])
    return h_uv(uv[:, 0], uv[:, 1]).reshape(xy.shape[:-1]), uv.reshape(xy.shape)


def in_zone(u, v, pad=0.0):
    u = np.asarray(u); v = np.asarray(v); m = np.zeros(u.shape, bool)
    for z in ZONES.values():
        m |= (u > z[0] - pad) & (u < z[2] + pad) & (v > z[1] - pad) & (v < z[3] + pad)
    return m


def near_obj(u, v, pad=10.0):
    u = np.asarray(u); v = np.asarray(v); m = np.zeros(u.shape, bool)
    for b in FOOT.values():
        cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        rx, ry = (b[2] - b[0]) / 2 * 1.15 + pad, (b[3] - b[1]) / 2 * 1.15 + pad
        m |= ((u - cx) / rx) ** 2 + ((v - cy) / ry) ** 2 <= 1.0
    return m


def poly_dist(pl, u, v):
    pl = np.asarray(pl, float); best = np.full(np.shape(u), 1e9)
    for (ax, ay), (bx, by) in zip(pl[:-1], pl[1:]):
        dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy + 1e-12
        t = np.clip(((u - ax) * dx + (v - ay) * dy) / L2, 0, 1)
        best = np.minimum(best, np.hypot(u - (ax + t * dx), v - (ay + t * dy)))
    return best


def build(name, verts, faces, coll, low=False):
    ob = U.mesh_from_arrays(name, np.asarray(verts, float), faces, U.coll(coll))
    for p in ob.data.polygons:
        p.use_smooth = False
    if low:
        ob['low_terrain'] = True
    return ob


# ---------------- 1. 로마 가도 ----------------
ROADS = {
    # 18:04 사용자: 넓은 길이 넓은 공간을 가로질러 CORE 흐름(①→②→③→④→⑤)을 그래픽으로 보여 주게
    'R_core_road': json.load(open(ROOT + 'assets/core_road_uv.json')),        # ① 아래 → 포로 앞 → 다리1(티베르) → ② 옆 → 다리2 → 콜로세움 앞(③④ 위) → ⑤
    'R_via_appia':    [(848, 986), (885, 992), (925, 994), (1000, 990), (1080, 984), (1150, 982), (1215, 984)],   # R16 프리베르눔 유적 뒤로 11pt 띄움
    'R_via_ostiensis': [(398, 1014), (372, 1036), (346, 1068), (322, 1100), (300, 1132), (282, 1160), (262, 1190), (241, 1220), (221, 1250), (201, 1280), (181, 1310), (161, 1340), (150, 1356)],   # R14 CORE 길에서 갈라져 팔라티노 서쪽·강 동쪽 둑 따라(실제 오스티아 가도)
}
ROAD_W = {'R_via_appia': 1.9, 'R_via_ostiensis': 1.5, 'R_core_road': 3.2}


def road_width(name, u, v):
    """R_core_road는 콜로세움 앞(③④ 위, x 400~790)에서만 좁게(2.2), 나머지는 넓게(3.2)"""
    w = ROAD_W[name]
    if name == 'R_core_road':
        k = max(0.0, min(1.0, (min(u - 380, 800 - u) / 40.0))) * max(0.0, min(1.0, (v - 960) / 30.0))
        w = 3.2 - 1.0 * k * k * (3 - 2 * k)
    return w


def _bridge_spans():
    """bridge.py와 같은 방식: CORE 길이 강 다각형을 지나는 구간 + 양쪽 7pt → [(A_uv, B_uv), ...]"""
    riv = np.asarray(json.load(open(ROOT + 'assets/terrain_polys.json'))['river'][0][0])
    road = np.asarray(ROADS['R_core_road'], float)
    sg = np.r_[0, np.cumsum(np.hypot(*np.diff(road, axis=0).T))]
    ss_ = np.arange(0, sg[-1], 0.5)
    pp = np.c_[np.interp(ss_, sg, road[:, 0]), np.interp(ss_, sg, road[:, 1])]
    def _in(x, y):
        c = False
        for (ax, ay), (bx, by) in zip(riv, np.roll(riv, -1, axis=0)):
            if (ay > y) != (by > y) and x < (bx - ax) * (y - ay) / (by - ay + 1e-12) + ax:
                c = not c
        return c
    wet_ = np.array([_in(x, y) for x, y in pp]); out = []; k = 0
    while k < len(wet_):
        if wet_[k]:
            j = k
            while j < len(wet_) and wet_[j]:
                j += 1
            out.append((pp[max(0, k - 14)], pp[min(len(pp) - 1, j + 13)])); k = j
        else:
            k += 1
    return out


BRIDGE_SPANS = _bridge_spans()


def road_mesh(name, pts_uv, width):
    P = U.pts_to_world(np.asarray(pts_uv, float), 0.0)[:, :2]
    # 세계 좌표에서 촘촘히 다시 샘플(0.45 단위 = 포장석 길이)
    seg = np.r_[0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]
    s = np.arange(0, seg[-1], 0.45)
    C = np.c_[np.interp(s, seg, P[:, 0]), np.interp(s, seg, P[:, 1])]
    Tg = np.gradient(C, axis=0); Tg /= np.linalg.norm(Tg, axis=1, keepdims=True) + 1e-9
    N = np.c_[-Tg[:, 1], Tg[:, 0]]
    verts, faces = [], []

    def box(cx, cy, tx, ty, nx, ny, L, Wd, z0, hgt):
        base = len(verts)
        for sz in (0.0, hgt):
            for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                verts.append((cx + tx * a * L / 2 + nx * b * Wd / 2, cy + ty * a * L / 2 + ny * b * Wd / 2, z0 + sz))
        faces.extend([(base + 4, base + 5, base + 6, base + 7), (base, base + 1, base + 5, base + 4), (base + 1, base + 2, base + 6, base + 5),
                      (base + 2, base + 3, base + 7, base + 6), (base + 3, base, base + 4, base + 7)])

    nacross = 4
    curb_pts = []
    zc, uvc = h_xy(C)
    _ang = np.linspace(0, 2 * math.pi, 16, endpoint=False)
    _core = np.asarray(ROADS['R_core_road'], float)
    for i in range(len(C)):
        if wet_uv(uvc[i, 0], uvc[i, 1]):
            continue
        # R11: 물 10pt 안은 다리 경사로 몫 → 포장 안 함 / 다른 길이 CORE 길에 닿는 곳(15pt)은 CORE 길 몫
        if name == 'R_core_road':
            # R11b: CORE 길은 다리 구간(다리 양 끝점 사이)만 비움 — 다리 경사로가 길 끝을 덮음
            if any(float(poly_dist(np.array([a_, b_]), np.array([uvc[i, 0]]), np.array([uvc[i, 1]]))[0]) < 4 for a_, b_ in BRIDGE_SPANS):
                continue
        elif any(wet_uv(uvc[i, 0] + rr * np.cos(_ang), uvc[i, 1] + rr * np.sin(_ang)).any() for rr in (5, 9, 13)):
            continue
        if name != 'R_core_road' and float(poly_dist(_core, np.array([uvc[i, 0]]), np.array([uvc[i, 1]]))[0]) < 12:
            continue
        cx, cy = C[i]; tx, ty = Tg[i]; nx, ny = N[i]
        z0 = zc[i] + 0.02
        width = road_width(name, uvc[i, 0], uvc[i, 1])
        # 노반(살짝 돋운 길 바닥)
        box(cx, cy, tx, ty, nx, ny, 0.47, width + 0.5, z0 - 0.05, 0.07)
        off = (i % 2) * 0.5
        nacross = max(4, int(round(width / 0.55)))
        for k in range(nacross):
            a = (-width / 2) + (k + 0.5 + off * 0.5) * width / nacross
            if abs(a) > width / 2 - 0.1:
                continue
            L = 0.40 + rng.uniform(-0.04, 0.03); Wd = width / nacross - 0.06
            box(cx + nx * a, cy + ny * a, tx, ty, nx, ny, L, Wd, z0 + 0.02, 0.05 + rng.uniform(0, 0.03))
        if name == 'R_core_road' or float(poly_dist(_core, np.array([uvc[i, 0]]), np.array([uvc[i, 1]]))[0]) > 20:
            curb_pts.append((i, cx, cy, nx, ny, z0, width))   # R15 곁길 갈림목엔 끝 연석 없음
    # CURB_RIBBON(R13): 연석을 이어진 띠로(굽은 곳에서 점점이 흩어지던 블록 대신)
    runs, cur = [], []
    for item in curb_pts:
        if cur and item[0] != cur[-1][0] + 1:
            runs.append(cur); cur = []
        cur.append(item)
    if cur:
        runs.append(cur)
    for run in runs:
        if len(run) < 2:
            continue
        for sgn in (-1, 1):
            base = len(verts); k = 0
            for (_, cx, cy, nx, ny, z0, wd) in run:
                a_in = sgn * (wd / 2 + 0.02); a_out = sgn * (wd / 2 + 0.22)
                for a_, zz in ((a_in, z0 + 0.02), (a_in, z0 + 0.13), (a_out, z0 + 0.13), (a_out, z0 + 0.02)):
                    verts.append((cx + nx * a_, cy + ny * a_, zz))
                k += 1
            for j in range(k - 1):
                b0 = base + 4 * j; b1 = b0 + 4
                faces.extend([(b0 + 1, b1 + 1, b1 + 2, b0 + 2), (b0, b1, b1 + 1, b0 + 1), (b0 + 2, b1 + 2, b1 + 3, b0 + 3)])
    return build(name, verts, faces, '35_FIELDS_ROADS', low=True)


for _old in ('R_ring', 'R_via_sacra', 'R_pons'):
    U.remove_obj(_old)
roads = {n: road_mesh(n, p, ROAD_W[n]) for n, p in ROADS.items()}

# ---------------- 2. 켄투리아티오 밭 ----------------
# 로마 농지 구획: 큰 정사각 구획(centuria)을 좁은 농로(limes)로 나누고, 구획 안은 폭이 다른 띠 밭(이랑·포도·올리브·목초·휴경)
CENT = 10.4        # 구획 한 변(세계 단위)
LIMES = 0.5        # 구획 사이 농로 폭
SUB = 2.6          # 띠 밭을 길이 방향으로 자르는 단위(조각마다 물·오브젝트·길 검사)
lo = U.pts_to_world(np.array([[0, 0], [1191, 0], [1191, 1684], [0, 1684]], float), 0.0)[:, :2]
ox, oy = lo[:, 0].min() - 3.1, lo[:, 1].min() - 1.7
FV, FF = [], []
nv_total = [0]


def add_quads(X, Y, Z):
    na, nb = X.shape
    FV.append(np.stack([X, Y, Z], -1).reshape(-1, 3))
    I = np.arange(na * nb).reshape(na, nb) + nv_total[0]
    FF.append(np.stack([I[:-1, :-1], I[1:, :-1], I[1:, 1:], I[:-1, 1:]], -1).reshape(-1, 4))
    nv_total[0] += na * nb


def add_post(x0, y0, z0, r, hgt, cap):
    ring = [(x0 + r * math.cos(t), y0 + r * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 6, endpoint=False)]
    b0 = nv_total[0]
    FV.append(np.array([(p[0], p[1], z0) for p in ring] + [(p[0], p[1], z0 + hgt) for p in ring] + [(x0, y0, z0 + hgt + cap)]))
    f = [(b0 + k, b0 + (k + 1) % 6, b0 + 6 + (k + 1) % 6, b0 + 6 + k) for k in range(6)]
    f += [(b0 + 6 + k, b0 + 6 + (k + 1) % 6, b0 + 12, b0 + 12) for k in range(6)]
    FF.append(np.array(f)); nv_total[0] += 13


def add_olive(x0, y0, z0, s):
    import bmesh as _bm
    b0 = nv_total[0]
    vv_ = []; ff_ = []
    # 작은 둥근 수관(정이십면체 1단 분할 근사: 위도·경도 구)
    nu_, nvv = 6, 3
    for i in range(nvv + 1):
        th = math.pi * i / nvv
        for j in range(nu_):
            ph = 2 * math.pi * j / nu_
            vv_.append((x0 + s * math.sin(th) * math.cos(ph), y0 + s * math.sin(th) * math.sin(ph), z0 + 0.35 + s * 0.75 * (1 + math.cos(th))))
    for i in range(nvv):
        for j in range(nu_):
            a_ = b0 + i * nu_ + j; b_ = b0 + i * nu_ + (j + 1) % nu_
            ff_.append((a_, b_, b_ + nu_, a_ + nu_))
    FV.append(np.array(vv_)); FF.append(np.array(ff_)); nv_total[0] += len(vv_)


_TZ = json.load(open(ROOT + 'sketch_v2/text_zones.json'))
# R7PATH: 밭은 CORE 읽는 순서 길(±10pt)과 모든 오브젝트 화면 상자(수도교·봉우리 제외)를 피함
TALL_BOX = []
for _cn in ('20_LANDMARK', '40_REGION', '45_CORE_SCENES', '50_DETAIL_MODEL'):
    _c = bpy.data.collections.get(_cn)
    for _o in (_c.objects if _c else []):
        if _o.type == 'MESH' and not _o.hide_render and not _o.name.startswith(('L05_aqua', 'L01_')):
            TALL_BOX.append(U.screen_bbox(_o, 4))
PATH_PTS = np.concatenate([np.asarray(p, float) for p in json.load(open(ROOT + 'assets/core_path_uv.json'))])
SIMPLE_ZONES = [z for k, z in _TZ['zones'].items() if k.startswith(('CORE', 'DETAIL', 'SUPPORT'))] + \
               [_TZ['objects'][k] for k in ('D1_model', 'D2_model', 'D4_model')] + [[250, 1199, 412, 1337]] + \
               [[t['b'][0] - 8, t['b'][1] - 6, t['b'][2] + 8, t['b'][3] + 6] for t in json.load(open(ROOT + 'loop/figma_texts.json')) if t['kind'] not in ('header', 'title', 'timeline')]   # R7 모든 지도 위 글 밑은 평야


def in_simple_zone(cx, cy, ax, ay, w, L, pad=12.0):
    bx, by = -ay, ax
    pts = np.array([[cx + sb * ax * L / 2 + sa * bx * w / 2, cy + sb * ay * L / 2 + sa * by * w / 2] for sa in (-1, 1) for sb in (-1, 1)])
    _, uv = h_xy(pts)
    u0, v0 = uv[:, 0].min(), uv[:, 1].min(); u1, v1 = uv[:, 0].max(), uv[:, 1].max()
    return any(u1 > z[0] - pad and u0 < z[2] + pad and v1 > z[1] - pad and v0 < z[3] + pad for z in SIMPLE_ZONES)


def strip(cx, cy, ax, ay, w, L, kind):
    """띠 밭 조각: 중심 (cx,cy), 길이 방향 (ax,ay) 단위벡터, 폭 w, 길이 L."""
    bx, by = -ay, ax
    if kind == 'fallow' or in_simple_zone(cx, cy, ax, ay, w, L):
        return
    # R6CORNERS: 모서리 네 점이 물 밖이고, 키 큰 물체(화산·콜로세움 등) 화면 상자 밖이어야
    _c = np.array([[cx + sb * ax * L / 2 + sa * bx * w / 2, cy + sb * ay * L / 2 + sa * by * w / 2] for sa in (-1, 1) for sb in (-1, 1)])
    _, _q = h_xy(_c)
    if wet_uv(_q[:, 0], _q[:, 1]).any():
        return
    _g = np.array([[cx + sb * ax * L / 2 + sa * bx * w / 2, cy + sb * ay * L / 2 + sa * by * w / 2] for sa in (-1, 0, 1) for sb in (-1, 0, 1)])
    _, _gq = h_xy(_g)
    if min(float(poly_dist(p_, _gq[:, 0], _gq[:, 1]).min()) for p_ in ROADS.values()) < 14:   # R14 3x3 점 모두 길에서 14pt
        return
    if any(_q[:, 0].max() > bb[0] - 3 and _q[:, 0].min() < bb[2] + 3 and _q[:, 1].max() > bb[1] - 3 and _q[:, 1].min() < bb[3] + 3 for bb in TALL_BOX):
        return
    _in = (PATH_PTS[:, 0] > _q[:, 0].min() - 10) & (PATH_PTS[:, 0] < _q[:, 0].max() + 10) & (PATH_PTS[:, 1] > _q[:, 1].min() - 10) & (PATH_PTS[:, 1] < _q[:, 1].max() + 10)
    if _in.any() or w < 0.9 or L < 0.9:
        return
    na = max(2, int(w / (0.30 if kind == 'furrow' else 0.6)))
    nb = max(2, int(L / 1.0))
    A = np.linspace(-w / 2, w / 2, na + 1); B = np.linspace(-L / 2, L / 2, nb + 1)
    aa, bb = np.meshgrid(A, B, indexing='ij')
    X = cx + bb * ax + aa * bx; Y = cy + bb * ay + aa * by
    z, _ = h_xy(np.stack([X, Y], -1))
    if kind == 'furrow':
        rid = 0.07 * (np.arange(na + 1) % 2)[:, None] * np.ones_like(bb)
    elif kind == 'pasture':
        rid = 0.025 * rng.random(aa.shape)
    else:
        rid = np.zeros_like(aa)
    edge = np.abs(aa) > w / 2 - 0.12                      # 띠 사이 둑
    add_quads(X, Y, z + 0.05 + np.where(edge, 0.11, rid))
    if kind == 'vine':
        for a_ in np.arange(-w / 2 + 0.35, w / 2 - 0.2, 0.45):
            for b_ in np.arange(-L / 2 + 0.25, L / 2 - 0.1, 0.5):
                x0, y0 = cx + b_ * ax + a_ * bx, cy + b_ * ay + a_ * by
                zz, _ = h_xy(np.array([[x0, y0]]))
                add_post(x0, y0, float(zz[0]) + 0.05, 0.08, 0.3 + rng.uniform(0, 0.06), 0.1)
    elif kind == 'olive':
        for a_ in np.arange(-w / 2 + 0.6, w / 2 - 0.3, 1.1):
            for b_ in np.arange(-L / 2 + 0.55, L / 2 - 0.3, 1.1):
                x0, y0 = cx + b_ * ax + a_ * bx, cy + b_ * ay + a_ * by
                zz, _ = h_xy(np.array([[x0, y0]]))
                add_olive(x0, y0, float(zz[0]), 0.36 + rng.uniform(-0.05, 0.05))


def ok_pts(xy):
    hz, uv = h_xy(xy)
    u, v = uv[..., 0], uv[..., 1]
    rd = np.minimum.reduce([poly_dist(p, u, v) for p in ROADS.values()])
    return (u > 4) & (u < 1187) & (v > 430) & (v < 1676) & ~wet_uv(u, v) & ~near_obj(u, v, 12) & (rd > 12) & (hz < 1.9)


nx = int((lo[:, 0].max() - ox) / CENT) + 1; ny = int((lo[:, 1].max() - oy) / CENT) + 1
n_cent = 0
for i in range(nx):
    for j in range(ny):
        x0 = ox + i * CENT + LIMES / 2; y0 = oy + j * CENT + LIMES / 2; side = CENT - LIMES
        corners = np.array([[x0, y0], [x0 + side, y0], [x0 + side, y0 + side], [x0, y0 + side], [x0 + side / 2, y0 + side / 2]])
        okc = ok_pts(corners)
        if okc.sum() < 2 or rng.random() < 0.22:          # 일부 구획은 자연 그대로(목초·숲)
            continue
        n_cent += 1
        along_x = rng.random() < 0.5
        k = int(rng.integers(2, 5))
        ws = rng.dirichlet(np.ones(k) * 2.5) * side
        off = 0.0
        for w in ws:
            kind = rng.choice(['furrow', 'furrow', 'vine', 'olive', 'pasture', 'fallow'], p=[0.3, 0.12, 0.2, 0.14, 0.14, 0.1])
            for sb in np.arange(0, side - 1e-6, SUB):
                L = min(SUB, side - sb)
                if along_x:
                    cx, cy = x0 + sb + L / 2, y0 + off + w / 2; ax, ay = 1.0, 0.0
                else:
                    cx, cy = x0 + off + w / 2, y0 + sb + L / 2; ax, ay = 0.0, 1.0
                if not ok_pts(np.array([[cx, cy]]))[0]:
                    continue
                strip(cx, cy, ax, ay, w, L, kind)
            off += w
fv = np.concatenate(FV)
tri = [tuple(dict.fromkeys(f)) for f in np.concatenate([np.asarray(f) for f in FF]).tolist()]
fields = build('F_centuriatio', fv, tri, '35_FIELDS_ROADS', low=True)
ok = np.array([n_cent])

# ---------------- 3. 나무 ----------------
def make_pine(seed, height=5.2, crown=4.6):
    r = np.random.default_rng(seed)
    bm = bmesh.new()
    lean = Vector((r.uniform(-0.25, 0.25), r.uniform(-0.25, 0.25), 0))
    # 줄기: 위로 갈수록 가늘고 살짝 휜 원기둥
    rings = []
    for k in range(7):
        t = k / 6
        c = Vector((0, 0, t * height * 0.78)) + lean * (t * t) * height * 0.3
        rad = 0.22 * (1 - 0.6 * t)
        rings.append([bm.verts.new(c + Vector((rad * math.cos(a), rad * math.sin(a), 0))) for a in np.linspace(0, 2 * math.pi, 8, endpoint=False)])
    for r0, r1 in zip(rings[:-1], rings[1:]):
        for i in range(8):
            bm.faces.new((r0[i], r0[(i + 1) % 8], r1[(i + 1) % 8], r1[i]))
    top = Vector((0, 0, height * 0.78)) + lean * height * 0.3
    # 우산 모양 수관: 납작한 덩어리 여러 개
    for j in range(7):
        ang = j / 7 * 2 * math.pi + r.uniform(-0.3, 0.3)
        rr = 0 if j == 0 else crown * 0.28 * r.uniform(0.7, 1.0)
        cpos = top + Vector((rr * math.cos(ang), rr * math.sin(ang), r.uniform(0.1, 0.45)))
        sz = crown * (0.42 if j == 0 else 0.30) * r.uniform(0.85, 1.1)
        res = bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)
        for v in res['verts']:
            p = v.co.copy()
            n = noise.noise(p * 1.7 + Vector((seed, j, 0))) * 0.18
            v.co = Vector((p.x * sz * (1 + n), p.y * sz * (1 + n), p.z * sz * 0.36 * (1 + n))) + cpos
    me = bpy.data.meshes.new('TREE_pine_%d' % seed)
    bm.to_mesh(me); bm.free()
    return me


def make_cypress(seed, height=5.6):
    r = np.random.default_rng(seed)
    bm = bmesh.new()
    res = bmesh.ops.create_icosphere(bm, subdivisions=4, radius=1.0)
    for v in res['verts']:
        p = v.co.copy()
        t = (p.z + 1) / 2                               # 0 아래 ~ 1 위
        w = 0.55 * (1 - t) ** 0.5 * (0.35 + 0.65 * math.sin(math.pi * min(1, t * 1.15)) ** 0.6) + 0.02
        n = noise.noise(p * 3.1 + Vector((seed, 0, 0))) * 0.12
        v.co = Vector((p.x * w * (1 + n), p.y * w * (1 + n), 0.25 + t * height))
    me = bpy.data.meshes.new('TREE_cypress_%d' % seed)
    bm.to_mesh(me); bm.free()
    return me


TC = U.coll('60_TREES')
for o in list(TC.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for me in [m for m in bpy.data.meshes if m.name.startswith('TREE_') and m.users == 0]:
    bpy.data.meshes.remove(me)
PINES = [make_pine(s) for s in (1, 2, 3)]
# 오브젝트(유적·근거 장소)의 화면 상자: 나무가 이 상자와 겹치면 심지 않음(가림 방지, 14:47 프리베르눔이 소나무에 가려짐)
OBJ_BOX = []
for cn in ('20_LANDMARK', '40_REGION', '45_CORE_SCENES', '50_DETAIL_MODEL'):
    col = bpy.data.collections.get(cn)
    for o in (col.objects if col else []):
        if o.type == 'MESH' and not o.hide_render:
            OBJ_BOX.append(U.screen_bbox(o, 4))
CYPR = [make_cypress(s) for s in (4, 5, 6)]


PIN_SEGS = [((240, 1533), (198, 1497)), ((590, 1497.8), (590, 1536.9)), ((724, 1545), (724, 1482)), ((897, 1062), (1024, 1062))]


def plant(kind, xy, scale=1.0):
    z, uv = h_xy(np.array([xy]))
    u, v = uv[0]
    if wet_uv(u, v) or near_obj(u, v, 6) or u < 6 or u > 1185 or v > 1675:
        return None
    # NEAR_WET(R10): 둘레 7pt 안에 물이 있으면, 또는 어느 길 가운데선에서 12pt 안이면 심지 않음
    _ang = np.linspace(0, 2 * math.pi, 8, endpoint=False)
    if wet_uv(u + 12 * np.cos(_ang), v + 12 * np.sin(_ang)).any():
        return None
    if min(float(poly_dist(p_, np.array([u]), np.array([v]))[0]) for p_ in ROADS.values()) < 24:   # R14 수관까지 길을 가리지 않게
        return None
    _r = float(U.rise_per_unit(np.array([[u, v]]))[0])
    if u - 2.6 * scale * _r < 4 or u + 2.6 * scale * _r > 1187 or v - 6.2 * scale * _r < 260:
        return None                                    # 수관이 프레임 밖·헤더로 나가지 않게
    me = (PINES if kind == 'pine' else CYPR)[rng.integers(0, 3)]
    # 글 자리 침범 검사: 줄기 밑~꼭대기의 화면 상자
    rise = float(U.rise_per_unit(np.array([[u, v]]))[0])
    hgt = (5.6 if kind == 'cypress' else 5.6) * scale
    wpt = (2.4 if kind == 'pine' else 0.7) * scale * rise
    zone = False
    for zb in ZONES.values():
        if u + wpt > zb[0] - 3 and u - wpt < zb[2] + 3 and v > zb[1] - 3 and v - hgt * rise < zb[3] + 3:
            zone = True; break
    for bb in OBJ_BOX:
        if u + wpt > bb[0] - 6 and u - wpt < bb[2] + 6 and v > bb[1] - 4 and v - hgt * rise < bb[3] + 6:
            zone = True; break
    if zone:
        return None
    ob = bpy.data.objects.new(('T_pine' if kind == 'pine' else 'T_cypress'), me)
    TC.objects.link(ob)
    ob.location = (xy[0], xy[1], float(z[0]) - 0.05)
    ob.rotation_euler = (0, 0, rng.uniform(0, 2 * math.pi))
    ob.scale = (scale, scale, scale * rng.uniform(0.9, 1.1))
    return ob


n_tree = 0
# 가도 양옆: 사이프러스와 우산소나무 번갈아
for name, pts in ROADS.items():
    if name not in ('R_via_appia', 'R_via_ostiensis', 'R_core_road'):
        continue
    P = U.pts_to_world(np.asarray(pts, float), 0.0)[:, :2]
    seg = np.r_[0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]
    for s in np.arange(2.0, seg[-1], 3.6 if name == 'R_via_appia' else 6.0):
        c = np.array([np.interp(s, seg, P[:, 0]), np.interp(s, seg, P[:, 1])])
        i = min(np.searchsorted(seg, s), len(P) - 1); t = P[i] - P[max(i - 1, 0)]; t /= np.linalg.norm(t) + 1e-9
        nrm = np.array([-t[1], t[0]])
        for sgn in (-1, 1):
            if rng.random() < 0.25:
                continue
            _cand = c + nrm * sgn * 3.0
            _uvq = U.project_pts(np.array([[_cand[0], _cand[1], 0.0], [c[0], c[1], 0.0]]))
            if _uvq[0, 1] > _uvq[1, 1]:      # R11 화면 아래(앞)쪽 나무는 수관이 길을 가림 → 뒤쪽 편만
                continue
            kind = 'cypress' if rng.random() < 0.55 else 'pine'
            if plant(kind, c + nrm * sgn * (ROAD_W[name] / 2 + 1.3 + rng.uniform(0, 0.5)), rng.uniform(0.75, 0.95)):
                n_tree += 1
# 언덕 숲: 높이 0.9~2.6인 곳에 우산소나무 무리
gx, gy = np.meshgrid(np.arange(lo[:, 0].min(), lo[:, 0].max(), 3.0), np.arange(lo[:, 1].min(), lo[:, 1].max(), 3.0), indexing='ij')
gxy = np.stack([gx, gy], -1).reshape(-1, 2)
hc, uvc = h_xy(gxy); v_ = uvc[:, 1]
cand = gxy[(hc > 0.9) & (hc < 2.6) & (v_ > 430) & (v_ < 1440)]
rng.shuffle(cand)
for c in cand[:70]:
    for _ in range(rng.integers(2, 6)):
        if plant('pine', c + rng.normal(0, 1.6, 2), rng.uniform(0.6, 0.9)):
            n_tree += 1
# 로마 도심 둘레·강둑의 사이프러스 몇 그루
for uvp in [(520, 600), (560, 590), (720, 640), (780, 700), (300, 940), (330, 980), (470, 1000), (690, 1020)]:
    w = U.pts_to_world(np.array([uvp], float), 0.0)[0, :2]
    if plant('cypress', w, 0.8):
        n_tree += 1

# POSTCHECK: 심은 뒤 실제 화면 상자로 다시 검사 — 글 자리·오브젝트와 겹치는 나무는 지움
removed_t = 0
for t in [o for o in TC.objects]:
    bb = U.screen_bbox(t, 1)
    bad = any(bb[2] > z[0] - 2 and bb[0] < z[2] + 2 and bb[3] > z[1] - 2 and bb[1] < z[3] + 2 for z in ZONES.values())
    bad = bad or any(bb[2] > b[0] - 2 and bb[0] < b[2] + 2 and bb[3] > b[1] - 2 and bb[1] < b[3] + 2 for b in OBJ_BOX)
    bad = bad or bb[0] < 4 or bb[2] > 1187 or bb[1] < 258
    # R16 나무 화면 상자가 SUPPORT 핀 선(±4pt)과 겹치면 지움
    bad = bad or any(bb[2] > min(a_[0], b_[0]) - 4 and bb[0] < max(a_[0], b_[0]) + 4 and bb[3] > min(a_[1], b_[1]) - 4 and bb[1] < max(a_[1], b_[1]) + 4 for a_, b_ in PIN_SEGS)
    if bad:
        bpy.data.objects.remove(t, do_unlink=True); removed_t += 1; n_tree -= 1
print('trees removed by postcheck', removed_t)
tri_tree = sum(len(m.polygons) for m in PINES + CYPR)
print('roads', {k: U.tri_count(o) for k, o in roads.items()}, 'fields tris', U.tri_count(fields), 'centuriae', int(ok.sum()),
      'trees', n_tree, 'tree template faces', tri_tree)
