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

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_A/'
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
roads = {n: road_mesh(n, p, ROAD_W[n]) for n, p in ROADS.items() if n != 'R_core_road'}
U.remove_obj('R_core_road')
exec(open(ROOT + 'scripts/assets/a_core_road.py').read())   # 워커 A: CORE 길 = 노반·현무암 포장·흰 연석·셰브런·시작 광장·도착 개선문
roads['R_core_road'] = _core_obj

# ---------------- 2·3. 밭·나무: 워커 A 재작성(a_fields_trees.py) ----------------
exec(open(ROOT + 'scripts/assets/a_fields_trees.py').read())
print('roads', {k: U.tri_count(o) for k, o in roads.items()}, 'trees', n_tree)
