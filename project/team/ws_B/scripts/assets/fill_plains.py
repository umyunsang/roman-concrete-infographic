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

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_B/'
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
    'R_via_appia':    [(836, 977), (848, 986), (885, 992), (925, 994), (1000, 990), (1080, 984), (1150, 982), (1215, 984)],   # R16 프리베르눔 유적 뒤로 11pt 띄움
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


# ---- 워커 B · 비평 1: 길 = 지도에서 가장 또렷한 띠 + 진행 방향 신호 ----
# 돋운 노반(agger, 사다리꼴 단면) + 어두운 현무암 포장석 + 흰 연석(crepido) / CORE 길엔 흰 셰브런 포장(진행 방향 ①→⑤),
# 시작 ①: 둥근 광장 + 황금 이정표 기둥(Milliarium Aureum), 끝 ⑤: 화살촉 모양 포장 끝, 길가 이정표 기둥(miliarium) 일정 간격.
ROAD_STYLE = {   # 노반 높이, 포장석 회색, 연석 회색, 노반 회색
    'R_core_road': (0.17, 0.34, 1.0, 0.84),
    'R_via_appia': (0.07, 0.64, 1.0, 0.8),
    'R_via_ostiensis': (0.07, 0.64, 1.0, 0.8),
}
_FTB = [t['b'] for t in json.load(open(ROOT + 'loop/figma_texts.json'))]


def _hits_text(P3, pad=3.0):
    """세계 점들(N,3)이 화면에서 글 상자(+pad)에 하나라도 들어가면 True"""
    q = U.project_pts(np.asarray(P3, float))
    for b_ in _FTB:
        if ((q[:, 0] > b_[0] - pad) & (q[:, 0] < b_[2] + pad) & (q[:, 1] > b_[1] - pad) & (q[:, 1] < b_[3] + pad)).any():
            return True
    return False


class _MB:
    """간단한 메시 모음(꼭짓점·면 목록)"""
    def __init__(self):
        self.v, self.f = [], []

    def box(self, cx, cy, tx, ty, nx, ny, L, Wd, z0, hgt):
        b0 = len(self.v)
        for sz in (0.0, hgt):
            for a_, b_ in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                self.v.append((cx + tx * a_ * L / 2 + nx * b_ * Wd / 2, cy + ty * a_ * L / 2 + ny * b_ * Wd / 2, z0 + sz))
        self.f.extend([(b0 + 4, b0 + 5, b0 + 6, b0 + 7), (b0, b0 + 1, b0 + 5, b0 + 4), (b0 + 1, b0 + 2, b0 + 6, b0 + 5),
                       (b0 + 2, b0 + 3, b0 + 7, b0 + 6), (b0 + 3, b0, b0 + 4, b0 + 7)])

    def ribbon(self, sections):
        """sections: [ [(x,y,z), ...k개], ... ] 단면 k점을 이어 띠(열린 면들)"""
        if len(sections) < 2:
            return
        k = len(sections[0]); b0 = len(self.v)
        for sec in sections:
            self.v.extend(sec)
        for j in range(len(sections) - 1):
            for m in range(k - 1):
                a0 = b0 + j * k + m
                self.f.append((a0, a0 + k, a0 + k + 1, a0 + 1))

    def prism(self, poly_xy, z0, z1):
        """바닥 다각형(볼록) → 옆면+윗면"""
        n = len(poly_xy); b0 = len(self.v)
        for (x, y) in poly_xy:
            self.v.append((x, y, z0))
        for (x, y) in poly_xy:
            self.v.append((x, y, z1))
        self.f.append(tuple(b0 + n + i for i in range(n)))
        for i in range(n):
            j = (i + 1) % n
            self.f.append((b0 + i, b0 + j, b0 + n + j, b0 + n + i))

    def cyl(self, x, y, z0, r, h, seg=10):
        pts = [(x + r * math.cos(t), y + r * math.sin(t)) for t in np.linspace(0, 2 * math.pi, seg, endpoint=False)]
        self.prism(pts, z0, z0 + h)


def road_mesh(name, pts_uv, width):
    AG, G_PAVE, G_CURB, G_BED = ROAD_STYLE[name]
    core = name == 'R_core_road'
    P = U.pts_to_world(np.asarray(pts_uv, float), 0.0)[:, :2]
    seg = np.r_[0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]
    s = np.arange(0, seg[-1], 0.45)
    C = np.c_[np.interp(s, seg, P[:, 0]), np.interp(s, seg, P[:, 1])]
    Tg = np.gradient(C, axis=0); Tg /= np.linalg.norm(Tg, axis=1, keepdims=True) + 1e-9
    N = np.c_[-Tg[:, 1], Tg[:, 0]]
    stones, curbs, bed, chev = _MB(), _MB(), _MB(), _MB()
    zc, uvc = h_xy(C)
    _ang = np.linspace(0, 2 * math.pi, 16, endpoint=False)
    _core = np.asarray(ROADS['R_core_road'], float)
    kept = []
    for i in range(len(C)):
        if wet_uv(uvc[i, 0], uvc[i, 1]):
            continue
        if core:
            if any(float(poly_dist(np.array([a_, b_]), np.array([uvc[i, 0]]), np.array([uvc[i, 1]]))[0]) < 4 for a_, b_ in BRIDGE_SPANS):
                continue
        elif any(wet_uv(uvc[i, 0] + rr * np.cos(_ang), uvc[i, 1] + rr * np.sin(_ang)).any() for rr in (5, 9, 13)):
            continue
        if not core and float(poly_dist(_core, np.array([uvc[i, 0]]), np.array([uvc[i, 1]]))[0]) < 4:   # 워커 B: 곁길 끝은 CORE 길 노반 밑으로(T자 갈림)
            continue
        kept.append(i)
    if core and kept:
        # 끝 화살촉이 ⑤ 글 상자(+3.5pt)에 닿지 않을 때까지 길 끝을 뒤로 물림(화살촉 크기는 그대로)
        for back in range(0, 20):
            ie_ = kept[-1 - back]; tx_, ty_ = Tg[ie_]; nx_, ny_ = N[ie_]
            wd_ = road_width(name, uvc[ie_, 0], uvc[ie_, 1]); ze_ = zc[ie_] + 0.02
            base_ = C[ie_] + np.array([tx_, ty_]) * 0.1
            tip_ = base_ + np.array([tx_, ty_]) * 1.25 * wd_ * 0.8
            lft_ = base_ + np.array([nx_, ny_]) * (wd_ / 2 + 0.75); rgt_ = base_ - np.array([nx_, ny_]) * (wd_ / 2 + 0.75)
            pts_ = [tip_ + np.array([tx_, ty_]) * 0.35, lft_ + np.array([nx_, ny_]) * 0.5, rgt_ - np.array([nx_, ny_]) * 0.5]
            P3_ = np.array([[*p_, zz_] for p_ in pts_ for zz_ in (ze_ - 0.15, ze_ + AG + 0.25)])
            if not _hits_text(P3_, 3.5):
                break
        kept = kept[:len(kept) - back]
        print('arrow back', back)
    kset = set(kept)
    for i in (kept if core else []):   # 워커 B: 곁길(아피아·오스티아)은 포장석 없이 밝은 자갈길 띠 — CORE 길만 돌길(흐름 경쟁 없앰)
        cx, cy = C[i]; tx, ty = Tg[i]; nx, ny = N[i]
        z0 = zc[i] + 0.02 + AG
        wd = road_width(name, uvc[i, 0], uvc[i, 1])
        nac = max(4, int(round(wd / 0.55)))
        off = (i % 2) * 0.5
        for k in range(nac):
            a_ = (-wd / 2) + (k + 0.5 + off * 0.5) * wd / nac
            if abs(a_) > wd / 2 - 0.1:
                continue
            L = 0.40 + rng.uniform(-0.04, 0.03); Wd = wd / nac - 0.07
            stones.box(cx + nx * a_, cy + ny * a_, tx, ty, nx, ny, L, Wd, z0 - 0.02, 0.07 + rng.uniform(0, 0.025))
    # 연속 구간(run)마다 노반·연석 띠
    runs, cur = [], []
    for i in kept:
        if cur and i != cur[-1] + 1:
            runs.append(cur); cur = []
        cur.append(i)
    if cur:
        runs.append(cur)
    # 노반 어깨 폭: 기본 0.42, 바깥 점이 화면에서 글 상자(+3pt)에 닿는 곳은 0.08(글 바탕을 비움)
    SHW = {}
    if kept:
        ka = np.array(kept)
        wds = np.array([road_width(name, uvc[i, 0], uvc[i, 1]) for i in kept])
        bad = np.zeros(len(ka), bool)
        for sgn in (-1, 1):
            for ww_, zz_ in ((0.42, 0.0), (0.0, AG + 0.2)):
                o3 = np.c_[C[ka] + N[ka] * sgn * (wds / 2 + 0.26 + ww_)[:, None], zc[ka] + zz_]
                q = U.project_pts(o3)
                for b_ in _FTB:
                    bad |= (q[:, 0] > b_[0] - 4) & (q[:, 0] < b_[2] + 4) & (q[:, 1] > b_[1] - 4) & (q[:, 1] < b_[3] + 4)
        bad = np.convolve(bad.astype(float), np.ones(5), mode='same') > 0
        SHW = {i: (0.08 if bb else 0.42) for i, bb in zip(kept, bad)}
    for run in runs:
        if len(run) < 2:
            continue
        secs_bed, secs_cl, secs_cr = [], [], []
        for i in run:
            cx, cy = C[i]; nx, ny = N[i]; z = zc[i] + 0.02
            wd = road_width(name, uvc[i, 0], uvc[i, 1])
            hw = wd / 2 + 0.26
            sw = SHW.get(i, 0.42)
            secs_bed.append([(cx + nx * a_, cy + ny * a_, z + dz) for a_, dz in
                             ((-(hw + sw), -0.12 if sw > 0.2 else 0.0), (-hw, AG), (hw, AG), (hw + sw, -0.12 if sw > 0.2 else 0.0))])
            curb_ok = core
            for sgn, secs in ((-1, secs_cl), (1, secs_cr)):
                a_in = sgn * (wd / 2 + 0.02); a_out = sgn * (wd / 2 + 0.26)
                secs.append([(cx + nx * a_, cy + ny * a_, z + AG + dz) for a_, dz in
                             ((a_in, -0.02), (a_in, 0.14 if curb_ok else 0.0), (a_out, 0.14 if curb_ok else 0.0), (a_out, -0.02))])
        bed.ribbon(secs_bed); curbs.ribbon(secs_cl); curbs.ribbon(secs_cr)
    n_chev = n_mil = 0
    if core and kept:
        # 셰브런: 5.4단위마다, 다리 둘레·구간 끝 3칸은 건너뜀. 꼭짓점이 진행 방향(①→⑤)을 가리킴
        step_i = int(round(5.4 / 0.45))
        for i in kept[6::step_i]:
            if not all((i + d) in kset for d in (-4, -3, 3, 4)):
                continue
            cx, cy = C[i]; tx, ty = Tg[i]; nx, ny = N[i]
            wd = road_width(name, uvc[i, 0], uvc[i, 1]); z = zc[i] + 0.02 + AG
            apex = np.array([cx, cy]) + np.array([tx, ty]) * 0.42 * wd
            for sgn in (-1, 1):
                end = np.array([cx, cy]) - np.array([tx, ty]) * 0.40 * wd + np.array([nx, ny]) * sgn * 0.40 * wd
                mid = (apex + end) / 2; d_ = end - apex; Lb = float(np.linalg.norm(d_)); d_ /= Lb
                chev.box(mid[0], mid[1], d_[0], d_[1], -d_[1], d_[0], Lb + 0.2, 0.30, z + 0.03, 0.09)
            n_chev += 1
        # 시작 광장 + 황금 이정표
        i0 = kept[0]; tx, ty = Tg[i0]
        pc = C[i0] + np.array([tx, ty]) * 1.0
        zp = float(h_xy(np.array([pc]))[0][0]) + 0.02
        Rp = 2.25
        ring = [(pc[0] + Rp * math.cos(t), pc[1] + Rp * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 40, endpoint=False)]
        bed.prism([(pc[0] + (Rp + 0.45) * math.cos(t), pc[1] + (Rp + 0.45) * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 40, endpoint=False)], zp - 0.12, zp + AG - 0.03)
        stones.prism(ring, zp + AG - 0.04, zp + AG + 0.05)
        for k in range(40):     # 연석 고리(조각)
            t0 = 2 * math.pi * k / 40; t1 = 2 * math.pi * (k + 1) / 40
            q = [(pc[0] + Rp * math.cos(t0), pc[1] + Rp * math.sin(t0)), (pc[0] + (Rp + 0.26) * math.cos(t0), pc[1] + (Rp + 0.26) * math.sin(t0)),
                 (pc[0] + (Rp + 0.26) * math.cos(t1), pc[1] + (Rp + 0.26) * math.sin(t1)), (pc[0] + Rp * math.cos(t1), pc[1] + Rp * math.sin(t1))]
            # 길이 나가는 쪽(진행 방향 ±35°)은 연석 없음
            mid_ang = (t0 + t1) / 2
            if math.cos(mid_ang - math.atan2(ty, tx)) > math.cos(math.radians(38)):
                continue
            curbs.prism(q, zp + AG - 0.03, zp + AG + 0.15)
        # 광장 안 흰 원(포장 무늬) — 시작점 표지
        for k in range(28):
            t0 = 2 * math.pi * k / 28; t1 = 2 * math.pi * (k + 1) / 28
            r0, r1 = 1.05, 1.32
            chev.prism([(pc[0] + r0 * math.cos(t0), pc[1] + r0 * math.sin(t0)), (pc[0] + r1 * math.cos(t0), pc[1] + r1 * math.sin(t0)),
                        (pc[0] + r1 * math.cos(t1), pc[1] + r1 * math.sin(t1)), (pc[0] + r0 * math.cos(t1), pc[1] + r0 * math.sin(t1))], zp + AG + 0.02, zp + AG + 0.1)
        # 황금 이정표 기둥: 받침 + 기둥 + 머리
        col = _MB()
        col.prism([(pc[0] + 0.42 * a_, pc[1] + 0.42 * b_) for a_, b_ in ((-1, -1), (1, -1), (1, 1), (-1, 1))], zp + AG, zp + AG + 0.22)
        col.cyl(pc[0], pc[1], zp + AG + 0.22, 0.2, 1.05, 14)
        col.prism([(pc[0] + 0.3 * a_, pc[1] + 0.3 * b_) for a_, b_ in ((-1, -1), (1, -1), (1, 1), (-1, 1))], zp + AG + 1.27, zp + AG + 1.39)
        if not _hits_text(col.v, 3.0):
            b0 = len(curbs.v); curbs.v.extend(col.v); curbs.f.extend([tuple(x + b0 for x in f_) for f_ in col.f])
        else:
            print('milestone column skipped (text)')
        # 끝 ⑤: 화살촉 포장
        ie = kept[-1]; tx, ty = Tg[ie]; nx, ny = N[ie]
        wd = road_width(name, uvc[ie, 0], uvc[ie, 1]); ze = zc[ie] + 0.02
        for sc_ in (0.8,):
            base = C[ie] + np.array([tx, ty]) * 0.1
            tip = base + np.array([tx, ty]) * 1.25 * wd * sc_
            lft = base + np.array([nx, ny]) * (wd / 2 + 0.75); rgt = base - np.array([nx, ny]) * (wd / 2 + 0.75)
            tri3 = np.array([[*(tip + np.array([tx, ty]) * 0.35), zz_] for zz_ in (ze - 0.15, ze + AG + 0.2)] +
                            [[*(lft + np.array([nx, ny]) * 0.5), zz_] for zz_ in (ze - 0.15, ze + AG + 0.2)] +
                            [[*(rgt - np.array([nx, ny]) * 0.5), zz_] for zz_ in (ze - 0.15, ze + AG + 0.2)])
            if not _hits_text(tri3, 3.5):
                break
        stones.prism([tuple(tip), tuple(lft), tuple(rgt)], ze + AG - 0.04, ze + AG + 0.06)
        print('arrowhead scale', sc_)
        bed.prism([tuple(tip + np.array([tx, ty]) * 0.35), tuple(lft + np.array([nx, ny]) * 0.5 - np.array([tx, ty]) * 0.1),
                   tuple(rgt - np.array([nx, ny]) * 0.5 - np.array([tx, ty]) * 0.1)], ze - 0.12, ze + AG - 0.03)
        for a_, b_ in ((lft, tip), (rgt, tip)):
            d_ = b_ - a_; Lb = float(np.linalg.norm(d_)); d_ /= Lb; m_ = (a_ + b_) / 2
            curbs.box(m_[0], m_[1], d_[0], d_[1], -d_[1], d_[0], Lb + 0.15, 0.26, ze + AG - 0.03, 0.17)
        # 화살촉 안 흰 셰브런
        cx, cy = base + np.array([tx, ty]) * 0.35 * wd
        apex = np.array([cx, cy]) + np.array([tx, ty]) * 0.42 * wd * sc_
        for sgn in (-1, 1):
            end = np.array([cx, cy]) - np.array([tx, ty]) * 0.2 * wd + np.array([nx, ny]) * sgn * 0.42 * wd * sc_
            mid = (apex + end) / 2; d_ = end - apex; Lb = float(np.linalg.norm(d_)); d_ /= Lb
            chev.box(mid[0], mid[1], d_[0], d_[1], -d_[1], d_[0], Lb + 0.2, 0.30, ze + AG + 0.03, 0.09)
        # 길가 이정표 기둥(miliarium): 14단위마다, 화면 위(뒤)쪽 길가
        step_m = int(round(14.0 / 0.45))
        for i in kept[step_m // 2::step_m]:
            if not all((i + d) in kset for d in (-3, 3)):
                continue
            cx, cy = C[i]; nx, ny = N[i]
            wd = road_width(name, uvc[i, 0], uvc[i, 1])
            for sgn in (1, -1):
                pm = np.array([cx, cy]) + np.array([nx, ny]) * sgn * (wd / 2 + 0.75)
                q2 = U.project_pts(np.array([[pm[0], pm[1], 0.0], [cx, cy, 0.0]]))
                if q2[0, 1] < q2[1, 1]:
                    break
            zm = float(h_xy(np.array([pm]))[0][0]) + 0.02
            mil = _MB(); mil.cyl(pm[0], pm[1], zm - 0.1, 0.17, 0.95, 12)
            mil.prism([(pm[0] + 0.22 * a_, pm[1] + 0.22 * b_) for a_, b_ in ((-1, -1), (1, -1), (1, 1), (-1, 1))], zm - 0.1, zm + 0.12)
            if _hits_text(mil.v, 4.0) or wet_uv(*U.project_pts(np.array([[pm[0], pm[1], 0.0]]))[0]):
                continue
            b0 = len(curbs.v); curbs.v.extend(mil.v); curbs.f.extend([tuple(x + b0 for x in f_) for f_ in mil.f]); n_mil += 1
    obs = {}
    for suffix, mb, g in (('', stones, G_PAVE), ('_curb', curbs, G_CURB), ('_bed', bed, G_BED), ('_chev', chev, 1.0)):
        if not mb.v:
            U.remove_obj(name + suffix); continue
        ob = build(name + suffix, mb.v, mb.f, '35_FIELDS_ROADS', low=True)
        ob.color = (g, g, g, 1.0)
        obs[suffix] = ob
    if core:
        print('core road chevrons', n_chev, 'milestones', n_mil)
    return obs.get('') or obs.get('_bed')


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
# 워커 B: 수도교 교각 줄 둘레(화면 10pt)엔 밭 띠·생울타리 없음 — 포도 줄·올리브가 교각을 뚫던 것
_AQ = np.array([(1186, 398), (1080, 466), (990, 528), (910, 590), (858, 640), (830, 676)], float)
_aqs = np.r_[0, np.cumsum(np.hypot(*np.diff(_AQ, axis=0).T))]; _aqt = np.arange(0, _aqs[-1], 3.0)
PATH_PTS = np.r_[PATH_PTS, np.c_[np.interp(_aqt, _aqs, _AQ[:, 0]), np.interp(_aqt, _aqs, _AQ[:, 1])]]
SIMPLE_ZONES = [z for k, z in _TZ['zones'].items() if k.startswith(('CORE', 'DETAIL', 'SUPPORT'))] + \
               [_TZ['objects'][k] for k in ('D1_model', 'D2_model', 'D4_model')] + [[250, 1199, 412, 1337]] + \
               [[t['b'][0] - 8, t['b'][1] - 6, t['b'][2] + 8, t['b'][3] + 6] for t in json.load(open(ROOT + 'loop/figma_texts.json')) if t['kind'] not in ('header', 'title', 'timeline')]   # R7 모든 지도 위 글 밑은 평야


def in_simple_zone(cx, cy, ax, ay, w, L, pad=12.0):
    bx, by = -ay, ax
    pts = np.array([[cx + sb * ax * L / 2 + sa * bx * w / 2, cy + sb * ay * L / 2 + sa * by * w / 2] for sa in (-1, 1) for sb in (-1, 1)])
    _, uv = h_xy(pts)
    u0, v0 = uv[:, 0].min(), uv[:, 1].min(); u1, v1 = uv[:, 0].max(), uv[:, 1].max()
    return any(u1 > z[0] - pad and u0 < z[2] + pad and v1 > z[1] - pad and v0 < z[3] + pad for z in SIMPLE_ZONES)


def strip(cx, cy, ax, ay, w, L, kind, dry=False):
    """띠 밭 조각: 중심 (cx,cy), 길이 방향 (ax,ay) 단위벡터, 폭 w, 길이 L."""
    bx, by = -ay, ax
    if kind in ('fallow', 'pasture') or in_simple_zone(cx, cy, ax, ay, w, L):   # 워커 B: 목초지는 판 없이 땅 그대로(무늬 없는 흰 카드 같던 것)
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
    _gz, _ = h_xy(_g)
    if _gz.max() > 1.7 or _gz.min() < -0.02 or np.ptp(_gz) > 0.42:   # 워커 B: 기울어진 판·물가 비탈 위 판 금지
        return
    if any(_q[:, 0].max() > bb[0] - 3 and _q[:, 0].min() < bb[2] + 3 and _q[:, 1].max() > bb[1] - 3 and _q[:, 1].min() < bb[3] + 3 for bb in TALL_BOX):
        return
    _in = (PATH_PTS[:, 0] > _q[:, 0].min() - 10) & (PATH_PTS[:, 0] < _q[:, 0].max() + 10) & (PATH_PTS[:, 1] > _q[:, 1].min() - 10) & (PATH_PTS[:, 1] < _q[:, 1].max() + 10)
    if _in.any() or w < 0.9 or L < 0.9:
        return
    if dry:
        return True
    na = max(2, int(w / (rng.uniform(0.24, 0.42) if kind == 'furrow' else 0.6)))
    nb = max(2, int(L / 1.0))
    A = np.linspace(-w / 2, w / 2, na + 1); B = np.linspace(-L / 2, L / 2, nb + 1)
    aa, bb = np.meshgrid(A, B, indexing='ij')
    X = cx + bb * ax + aa * bx; Y = cy + bb * ay + aa * by
    z, _ = h_xy(np.stack([X, Y], -1))
    # 워커 B · 비평 3: 판을 땅에 붙임(0.03 위, 둘레는 땅속으로 내려가는 치마 — 뜬 판·그림자 틈 없음), 둑·이랑은 낮게
    if kind == 'furrow':
        rid = 0.045 * (np.arange(na + 1) % 2)[:, None] * np.ones_like(bb)
    elif kind == 'pasture':
        rid = 0.012 * rng.random(aa.shape)
    else:
        rid = np.zeros_like(aa)
    edge = np.abs(aa) > w / 2 - 0.12                      # 띠 사이 둑
    Zt = z + 0.03 + np.where(edge, 0.06, rid)
    FIELD_RECTS.append((cx, cy, ax, ay, w, L))
    b0 = nv_total[0]
    add_quads(X, Y, Zt)
    per = [(i_, 0) for i_ in range(na + 1)] + [(na, j_) for j_ in range(1, nb + 1)] + [(i_, nb) for i_ in range(na - 1, -1, -1)] + [(0, j_) for j_ in range(nb - 1, 0, -1)]
    sk0 = nv_total[0]
    FV.append(np.array([(X[i_, j_], Y[i_, j_], z[i_, j_] - 0.1) for i_, j_ in per]))
    nv_total[0] += len(per)
    sf = []
    for k_ in range(len(per)):
        i1, j1 = per[k_]; i2, j2 = per[(k_ + 1) % len(per)]
        sf.append((b0 + i1 * (nb + 1) + j1, sk0 + k_, sk0 + (k_ + 1) % len(per), b0 + i2 * (nb + 1) + j2))
    FF.append(np.array(sf))
    if kind == 'vine':
        # 포도밭: 못판 같은 기둥 격자 대신 길게 이어진 포도 줄(시렁) — 줄마다 끊김·높이 조금씩 다름
        for a_ in np.arange(-w / 2 + 0.3 + rng.uniform(0, 0.12), w / 2 - 0.2, 0.40):
            b_lo = -L / 2 + 0.12
            while b_lo < L / 2 - 0.3:
                seg_l = min(L / 2 - 0.12 - b_lo, rng.uniform(0.9, 2.4))
                if rng.random() > 0.08:
                    bc = b_lo + seg_l / 2
                    x0, y0 = cx + bc * ax + a_ * bx, cy + bc * ay + a_ * by
                    zz, _ = h_xy(np.array([[x0, y0]]))
                    CROPS.box(x0, y0, ax, ay, bx, by, seg_l, 0.1, float(zz[0]) + 0.01, 0.15 + rng.uniform(0, 0.04))
                b_lo += seg_l + rng.uniform(0.1, 0.22)
    elif kind == 'olive':
        # 올리브: 로마식 오점형(quincunx) 배열 + 흔들기·크기 차이·빈자리, 짧은 줄기 위 둥근 수관(공중에 뜬 공 아님)
        sp_ = rng.uniform(0.95, 1.15)
        for r_, a_ in enumerate(np.arange(-w / 2 + 0.5, w / 2 - 0.3, sp_ * 0.87)):
            for b_ in np.arange(-L / 2 + 0.4 + (r_ % 2) * sp_ / 2, L / 2 - 0.25, sp_):
                if rng.random() < 0.2:
                    continue
                aj, bj = a_ + rng.normal(0, 0.16), b_ + rng.normal(0, 0.16)
                x0, y0 = cx + bj * ax + aj * bx, cy + bj * ay + aj * by
                zz, _ = h_xy(np.array([[x0, y0]]))
                add_olive2(x0, y0, float(zz[0]), rng.uniform(0.26, 0.4))


CROPS = _MB()
HEDGE = _MB()
FIELD_RECTS = []
VILLA_W, VILLA_R = _MB(), _MB()


def add_olive2(x0, y0, z0, s_):
    CROPS.cyl(x0, y0, z0 - 0.02, 0.05, 0.3, 5)
    _blob(CROPS, x0, y0, z0 + 0.22 + s_ * 0.55, s_, s_ * 0.7)


def _blob(mb, x0, y0, zc_, rxy, rz, nu=8, nv_=4):
    b0 = len(mb.v)
    jit = 1 + rng.uniform(-0.13, 0.13, (nv_ + 1, nu))
    for i_ in range(nv_ + 1):
        th = math.pi * i_ / nv_
        for j_ in range(nu):
            ph = 2 * math.pi * j_ / nu
            k_ = jit[i_, j_] if 0 < i_ < nv_ else 1.0
            mb.v.append((x0 + rxy * k_ * math.sin(th) * math.cos(ph), y0 + rxy * k_ * math.sin(th) * math.sin(ph), zc_ + rz * math.cos(th) * (k_ if 0 < i_ < nv_ else 1)))
    for i_ in range(nv_):
        for j_ in range(nu):
            a_ = b0 + i_ * nu + j_; c_ = b0 + i_ * nu + (j_ + 1) % nu
            mb.f.append((a_, c_, c_ + nu, a_ + nu))


def pt_in_simple(u, v, pad=6.0):
    return any(u > z_[0] - pad and u < z_[2] + pad and v > z_[1] - pad and v < z_[3] + pad for z_ in SIMPLE_ZONES)


def ok_pts(xy):
    hz, uv = h_xy(xy)
    u, v = uv[..., 0], uv[..., 1]
    rd = np.minimum.reduce([poly_dist(p, u, v) for p in ROADS.values()])
    return (u > 4) & (u < 1187) & (v > 430) & (v < 1676) & ~wet_uv(u, v) & ~near_obj(u, v, 12) & (rd > 12) & (hz < 1.6) & (hz > -0.02)   # 워커 B: 물가 비탈에는 밭 없음(기울기는 strip에서)


CYP_LINES = []


def _pts_ok_generic(xy, road_pt=13.0):
    hz, uv = h_xy(xy)
    u, v = uv[..., 0], uv[..., 1]
    rd = np.minimum.reduce([poly_dist(p_, u, v) for p_ in ROADS.values()])
    ok_ = (u > 6) & (u < 1185) & (v > 440) & (v < 1670) & ~wet_uv(u, v) & (rd > road_pt) & (hz < 1.2) & (hz > -0.02)
    for k_ in range(len(u)):
        if ok_[k_] and (pt_in_simple(u[k_], v[k_], 8.0) or any(bb[0] - 4 < u[k_] < bb[2] + 4 and bb[1] - 4 < v[k_] < bb[3] + 4 for bb in TALL_BOX)):
            ok_[k_] = False
    pin = (PATH_PTS[:, None, 0] - u[None]) ** 2 + (PATH_PTS[:, None, 1] - v[None]) ** 2
    ok_ &= pin.min(0) > 100.0
    return ok_, hz


def _near_rects(xy, rects, m):
    for (cx, cy, ax, ay, w, L) in rects:
        dx, dy = xy[0] - cx, xy[1] - cy
        if abs(dx * ax + dy * ay) < L / 2 + m and abs(-dx * ay + dy * ax) < w / 2 + m:
            return True
    return False


def hedge_line(pa, pb, rects):
    """생울타리: 구획 경계를 따라 크고 작은 덤불이 드문드문 이어진 낮은 띠(밭 곁만, 점마다 글·물·길·물체 검사)"""
    Lh = float(np.linalg.norm(pb - pa)); n_ = int(Lh / 0.36)
    t_ = (np.arange(n_) + 0.5) / n_
    P_ = pa[None] + (pb - pa)[None] * t_[:, None]
    P_ += rng.normal(0, 0.05, P_.shape)
    ok_, hz = _pts_ok_generic(P_)
    gap = 0
    for k_ in range(n_):
        if gap > 0:
            gap -= 1; continue
        if rng.random() < 0.06:
            gap = int(rng.integers(1, 4)); continue
        if ok_[k_] and _near_rects(P_[k_], rects, 0.8):
            r0 = rng.uniform(0.17, 0.3)
            _blob(HEDGE, P_[k_, 0], P_[k_, 1], hz[k_] + 0.08 + r0 * 0.45, r0, r0 * 0.8, 7, 3)


def try_villa(vc):
    """농가: 안마당을 둘러싼 네 동 + 맞배지붕. 모든 꼭짓점이 글 상자 밖·길·물·물체에서 떨어져야"""
    ang = rng.choice([0.0, math.pi / 2]) + rng.uniform(-0.05, 0.05)
    t_ = np.array([math.cos(ang), math.sin(ang)]); n_ = np.array([-t_[1], t_[0]])
    W_, D_, wing = rng.uniform(2.0, 2.6), rng.uniform(1.7, 2.2), 0.55
    corners = np.array([vc + t_ * a_ * (W_ / 2 + 0.3) + n_ * b_ * (D_ / 2 + 0.3) for a_ in (-1, 1) for b_ in (-1, 1)])
    ok_, hz = _pts_ok_generic(np.r_[corners, [vc]], 16.0)
    if not ok_.all():
        return False
    z0 = float(hz.min()) - 0.05; hw = 0.5
    w_mb, r_mb = _MB(), _MB()
    wings = [(vc + n_ * (D_ / 2 - wing / 2), t_, W_), (vc - n_ * (D_ / 2 - wing / 2), t_, W_),
             (vc + t_ * (W_ / 2 - wing / 2), n_, D_ - 2 * wing), (vc - t_ * (W_ / 2 - wing / 2), n_, D_ - 2 * wing)]
    for k_, (c_, d_, len_) in enumerate(wings):
        hh = hw + (0.18 if k_ == 0 else 0.0)        # 본채는 조금 높게
        e_ = np.array([-d_[1], d_[0]])
        w_mb.box(c_[0], c_[1], d_[0], d_[1], e_[0], e_[1], len_, wing, z0, hh + 0.05)
        # 맞배지붕(용마루가 동 길이 방향)
        q = [c_ - d_ * len_ / 2 - e_ * (wing / 2 + 0.06), c_ + d_ * len_ / 2 - e_ * (wing / 2 + 0.06),
             c_ + d_ * len_ / 2 + e_ * (wing / 2 + 0.06), c_ - d_ * len_ / 2 + e_ * (wing / 2 + 0.06)]
        r0 = len(r_mb.v); zt = z0 + hh + 0.05
        hr = max(0.0, len_ / 2 - wing / 2 - 0.06)          # 워커 B: 모임지붕(hip) — 박공 끝 삼각 벽이 모서리에서 틈처럼 보이던 것
        r_mb.v.extend([(*q[0], zt), (*q[1], zt), (*q[2], zt), (*q[3], zt), (*(c_ - d_ * hr), zt + 0.26), (*(c_ + d_ * hr), zt + 0.26)])
        r_mb.f.extend([(r0, r0 + 1, r0 + 5, r0 + 4), (r0 + 2, r0 + 3, r0 + 4, r0 + 5), (r0 + 1, r0 + 2, r0 + 5), (r0 + 3, r0, r0 + 4)])
    if _hits_text(np.array(w_mb.v + r_mb.v), 5.0):
        return False
    for mb_src, mb_dst in ((w_mb, VILLA_W), (r_mb, VILLA_R)):
        b0 = len(mb_dst.v); mb_dst.v.extend(mb_src.v); mb_dst.f.extend([tuple(x + b0 for x in f_) for f_ in mb_src.f])
    return True


nx = int((lo[:, 0].max() - ox) / CENT) + 1; ny = int((lo[:, 1].max() - oy) / CENT) + 1
n_cent = 0
for i in range(nx):
    for j in range(ny):
        x0 = ox + i * CENT + LIMES / 2; y0 = oy + j * CENT + LIMES / 2; side = CENT - LIMES
        corners = np.array([[x0, y0], [x0 + side, y0], [x0 + side, y0 + side], [x0, y0 + side], [x0 + side / 2, y0 + side / 2]])
        okc = ok_pts(corners)
        if okc.sum() < 2 or rng.random() < 0.36:          # 일부 구획은 자연 그대로(목초·숲) — 워커 B: 0.22→0.36, 빈 들판이 숨 쉬게
            continue
        n_cent += 1
        # 워커 B · 비평 3: 몇 구획엔 농가(villa rustica)
        villa_c = None
        if okc.sum() >= 4 and rng.random() < 0.3 and False:   # 워커 B: 농가가 1배에서 '빈 상자'로 읽혀(심사 3회) 뺌
            vc = np.array([x0 + side * rng.uniform(0.3, 0.7), y0 + side * rng.uniform(0.3, 0.7)])
            if try_villa(vc):
                villa_c = vc
        n_rect0 = len(FIELD_RECTS)
        r_ = rng.random()
        sides_ = [((x0, y0), (x0 + side, y0)), ((x0 + side, y0), (x0 + side, y0 + side)), ((x0 + side, y0 + side), (x0, y0 + side)), ((x0, y0 + side), (x0, y0))]
        pick = rng.permutation(4)[:int(rng.integers(1, 3))]
        along_x = rng.random() < 0.5
        _cand_strips = []
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
                if villa_c is not None and abs(cx - villa_c[0]) < w / 2 + 1.7 and abs(cy - villa_c[1]) < L / 2 + 1.7:
                    continue
                if strip(cx, cy, ax, ay, w, L, kind, dry=True):
                    _cand_strips.append((cx, cy, ax, ay, w, L, kind))
            off += w
        # 워커 B: 혼자 떨어진 작은 밭 판(카드 한 장처럼 보임) 없앰 — 구획 안 밭 면적이 12단위² 이상일 때만
        if sum(a_[4] * a_[5] for a_ in _cand_strips) >= 12.0:
            for a_ in _cand_strips:
                strip(*a_)
        # 구획 경계(limes)에 생울타리 또는 사이프러스 줄 — 이 구획에 실제로 놓인 밭 띠 곁에만
        rects_ = FIELD_RECTS[n_rect0:]
        if rects_:
            for k_ in pick:
                (pa, pb) = sides_[k_]
                if r_ < 0.45:
                    hedge_line(np.array(pa), np.array(pb), rects_)
                elif r_ < 0.7:
                    CYP_LINES.append((np.array(pa), np.array(pb), rects_))
fv = np.concatenate(FV)
tri = [tuple(dict.fromkeys(f)) for f in np.concatenate([np.asarray(f) for f in FF]).tolist()]
fields = build('F_centuriatio', fv, tri, '35_FIELDS_ROADS', low=True)
fields.color = (0.86, 0.86, 0.86, 1)
for _nm, _mb, _g in (('F_crops', CROPS, 0.6), ('F_hedges', HEDGE, 0.66), ('F_villa_walls', VILLA_W, 0.95), ('F_villa_roofs', VILLA_R, 0.5)):
    if _mb.v:
        _o = build(_nm, _mb.v, _mb.f, '35_FIELDS_ROADS', low=True); _o.color = (_g, _g, _g, 1)
        print(_nm, 'tris', U.tri_count(_o))
    else:
        U.remove_obj(_nm)
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
    """워커 B · 비평 4: 사이프러스 = 짧은 줄기 + 아래가 둥글게 닫힌 불꽃 모양 잎덩이(끝으로 서서 땅을 뚫지 않음)"""
    r = np.random.default_rng(seed)
    bm = bmesh.new()
    res = bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)
    z_lo = 0.55
    for v in res['verts']:
        p = v.co.copy()
        t = (p.z + 1) / 2                               # 0 아래 ~ 1 위
        w = 0.5 * math.sin(math.pi / 2 * min(1.0, t / 0.16)) * (1 - t) ** 0.62 * (0.75 + 0.25 * math.sin(math.pi * min(1.0, t * 1.6)))
        n = noise.noise(p * 3.1 + Vector((seed, 0, 0))) * 0.12
        v.co = Vector((p.x * w * (1 + n), p.y * w * (1 + n), z_lo + t * (height - z_lo)))
    # 줄기
    ring0 = [bm.verts.new((0.1 * math.cos(a), 0.1 * math.sin(a), -0.25)) for a in np.linspace(0, 2 * math.pi, 7, endpoint=False)]
    ring1 = [bm.verts.new((0.08 * math.cos(a), 0.08 * math.sin(a), z_lo + 0.35)) for a in np.linspace(0, 2 * math.pi, 7, endpoint=False)]
    for i in range(7):
        bm.faces.new((ring0[i], ring0[(i + 1) % 7], ring1[(i + 1) % 7], ring1[i]))
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
# 워커 B: 카메라 앞 도형(80_SHAPES: ③ 단면 도식·지시선·핀 등)은 2번째 패스로 맨 위에 그려짐 → 그 뒤에 나무가 서면 '도식에서 나무가 자라는' 모습
for _cn in ('80_SHAPES', '81_NOSHADOW'):
    _c = bpy.data.collections.get(_cn)
    for _o in (_c.objects if _c else []):
        if _o.type == 'MESH' and not _o.name.startswith(('S_time', 'S_core')):
            _b = U.screen_bbox(_o, 1)
            OBJ_BOX.append((_b[0] - 6, _b[1] - 6, _b[2] + 6, _b[3] + 6))


PIN_SEGS = [((240, 1533), (198, 1497)), ((590, 1497.8), (590, 1536.9)), ((724, 1545), (724, 1482)), ((897, 1062), (1024, 1062))]


PLANTED = []
LINE_MODE = [False]
_ROAD_DENSE = []
for _nm, _pl in ROADS.items():
    _pl = np.asarray(_pl, float); _sg = np.r_[0, np.cumsum(np.hypot(*np.diff(_pl, axis=0).T))]; _t = np.arange(0, _sg[-1], 2.0)
    _hw0 = 13.0 if _nm == 'R_core_road' else 9.0
    for _x, _y in zip(np.interp(_t, _sg, _pl[:, 0]), np.interp(_t, _sg, _pl[:, 1])):
        _ROAD_DENSE.append((_x, _y, _hw0))
_ROAD_DENSE = np.array(_ROAD_DENSE)


# CORE 길 시작 광장·끝 화살촉 둘레는 나무 없이 비움(방향 신호가 또렷하게)
_cr = np.asarray(ROADS['R_core_road'], float)
_CLEAR = [(_cr[0, 0], _cr[0, 1], 30.0), (_cr[-1, 0] + 6, _cr[-1, 1] - 6, 34.0)]


def _occludes_road(u0, v0, u1, v1):
    R_ = _ROAD_DENSE
    if any(u1 > cx_ - r_ and u0 < cx_ + r_ and v1 > cy_ - r_ and v0 < cy_ + r_ for cx_, cy_, r_ in _CLEAR):
        return True
    return bool(((R_[:, 0] > u0 - R_[:, 2]) & (R_[:, 0] < u1 + R_[:, 2]) & (R_[:, 1] > v0 - R_[:, 2] * 0.6) & (R_[:, 1] < v1 + R_[:, 2] * 0.6)).any())


def _in_field(xy, m):
    for (cx, cy, ax, ay, w, L) in FIELD_RECTS:
        dx, dy = xy[0] - cx, xy[1] - cy
        if abs(dx * ax + dy * ay) < L / 2 + m and abs(-dx * ay + dy * ax) < w / 2 + m:
            return True
    return False


REJ = {k: 0 for k in ('obj/wet', 'nearwet', 'road', 'occl', 'field', 'spacing', 'frame', 'zone')}


def plant(kind, xy, scale=1.0):
    z, uv = h_xy(np.array([xy]))
    u, v = uv[0]
    if wet_uv(u, v) or near_obj(u, v, 2) or u < 6 or u > 1185 or v > 1675 or float(z[0]) < -0.02:
        REJ['obj/wet'] += 1; return None
    # NEAR_WET(R10): 둘레 7pt 안에 물이 있으면, 또는 어느 길 가운데선에서 12pt 안이면 심지 않음
    _ang = np.linspace(0, 2 * math.pi, 8, endpoint=False)
    if wet_uv(u + 12 * np.cos(_ang), v + 12 * np.sin(_ang)).any():
        REJ['nearwet'] += 1; return None
    if min(float(poly_dist(p_, np.array([u]), np.array([v]))[0]) for p_ in ROADS.values()) < 11:
        REJ['road'] += 1; return None
    _rr = float(U.rise_per_unit(np.array([[u, v]]))[0])
    _hw = (2.4 if kind == 'pine' else 0.6) * scale * _rr; _ht = (5.6 * scale + 0.3) * _rr
    if _occludes_road(u - _hw, v - _ht, u + _hw, v + 2.0):   # 워커 B: 수관 화면 상자가 길 띠를 가리면 안 심음(뒤쪽 길가는 가까이도 됨)
        REJ['occl'] += 1; return None
    if _in_field(xy, 0.35 if LINE_MODE[0] else 1.1):
        REJ['field'] += 1; return None
    if any(abs(xy[0] - q_[0]) < 0.9 * scale and abs(xy[1] - q_[1]) < 0.9 * scale for q_ in PLANTED):
        REJ['spacing'] += 1; return None
    _r = float(U.rise_per_unit(np.array([[u, v]]))[0])
    if u - 2.6 * scale * _r < 4 or u + 2.6 * scale * _r > 1187 or v - 6.2 * scale * _r < 260:
        REJ['frame'] += 1; return None                                    # 수관이 프레임 밖·헤더로 나가지 않게
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
        REJ['zone'] += 1; return None
    PLANTED.append((xy[0], xy[1]))
    ob = bpy.data.objects.new(('T_pine' if kind == 'pine' else 'T_cypress'), me)
    TC.objects.link(ob)
    ob.location = (xy[0], xy[1], float(z[0]) - 0.05)
    ob.rotation_euler = (0, 0, rng.uniform(0, 2 * math.pi))
    ob.scale = (scale, scale, scale * rng.uniform(0.9, 1.1))
    return ob


n_tree = 0
# 워커 B · 비평 4: 나무를 리듬 있게 — (1) 가도 뒤쪽 길가 가로수(아피아·오스티아: 소나무·사이프러스 번갈아 일정 간격,
# CORE 길: 사이프러스만 듬성), (2) 구획 경계 사이프러스 줄, (3) 구릉·산기슭 소나무 숲(무리), (4) 도심 둘레 사이프러스
for name, pts in ROADS.items():
    P = U.pts_to_world(np.asarray(pts, float), 0.0)[:, :2]
    seg = np.r_[0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]
    stp = {'R_via_appia': 2.4, 'R_via_ostiensis': 2.6, 'R_core_road': 6.5}[name]
    k_alt = 0
    for s_ in np.arange(1.5, seg[-1], stp):
        c = np.array([np.interp(s_, seg, P[:, 0]), np.interp(s_, seg, P[:, 1])])
        i = min(np.searchsorted(seg, s_), len(P) - 1); t = P[i] - P[max(i - 1, 0)]; t /= np.linalg.norm(t) + 1e-9
        nrm = np.array([-t[1], t[0]])
        for sgn in (-1, 1):
            _uvq = U.project_pts(np.array([[*(c + nrm * sgn * 3.0), 0.0], [c[0], c[1], 0.0]]))
            if _uvq[0, 1] > _uvq[1, 1]:      # 화면 아래(앞)쪽 길가는 수관이 길을 가림 → 뒤쪽 편만
                continue
            kind = 'cypress' if (name == 'R_core_road' or k_alt % 2 == 0) else 'pine'
            sc_ = 0.62 if kind == 'cypress' else 0.55
            if plant(kind, c + nrm * sgn * (ROAD_W[name] / 2 + 1.25), sc_ * rng.uniform(0.94, 1.06)):
                n_tree += 1
        k_alt += 1
# 구획 경계 사이프러스 줄
LINE_MODE[0] = True
for pa, pb, rects_ in CYP_LINES:
    Lc = float(np.linalg.norm(pb - pa)); nn_ = int(Lc / 1.35)
    for k_ in range(nn_):
        q_ = pa + (pb - pa) * (k_ + 0.5) / nn_
        if not _near_rects(q_, rects_, 1.0):
            continue
        if plant('cypress', q_, 0.46 * rng.uniform(0.92, 1.08)):
            n_tree += 1
LINE_MODE[0] = False
# 구릉·산기슭 숲: 높이 0.7~2.4인 곳(밭 밖)에 소나무 무리
gx, gy = np.meshgrid(np.arange(lo[:, 0].min(), lo[:, 0].max(), 2.6), np.arange(lo[:, 1].min(), lo[:, 1].max(), 2.6), indexing='ij')
gxy = np.stack([gx, gy], -1).reshape(-1, 2)
hc, uvc = h_xy(gxy); v_ = uvc[:, 1]
cand = gxy[(hc > 0.7) & (hc < 2.4) & (v_ > 330) & (v_ < 1440)]
rng.shuffle(cand)
for c in cand[:140]:
    for _ in range(rng.integers(3, 7)):
        if plant('pine' if rng.random() < 0.8 else 'cypress', c + rng.normal(0, 1.3, 2), rng.uniform(0.45, 0.62)):
            n_tree += 1
# 평야의 작은 숲(silva): 밭이 없는 빈 땅에 소나무 무리 — 빈 캔버스 느낌·나무 수 부족 보완
cand2 = gxy[(hc > 0.05) & (hc < 1.9) & (v_ > 470) & (v_ < 1430)]
rng.shuffle(cand2)
n_grove = 0
for c in cand2:
    if n_grove >= 26:
        break
    if _in_field(c, 1.5):
        continue
    got = 0
    for _ in range(rng.integers(3, 8)):
        if plant('pine' if rng.random() < 0.75 else 'cypress', c + rng.normal(0, 1.1, 2), rng.uniform(0.42, 0.58)):
            n_tree += 1; got += 1
    n_grove += 1 if got >= 2 else 0
# 로마 도심 둘레·강둑의 사이프러스 몇 그루
for uvp in [(520, 600), (560, 590), (720, 640), (780, 700), (300, 940), (330, 980), (470, 1000), (690, 1020)]:
    w = U.pts_to_world(np.array([uvp], float), 0.0)[0, :2]
    if plant('cypress', w, 0.62):
        n_tree += 1

# POSTCHECK: 심은 뒤 실제 화면 상자로 다시 검사 — 글 자리·오브젝트와 겹치는 나무는 지움
removed_t = 0
for t in [o for o in TC.objects]:
    bb = U.screen_bbox(t, 1)
    bad = any(bb[2] > z[0] - 2 and bb[0] < z[2] + 2 and bb[3] > z[1] - 2 and bb[1] < z[3] + 2 for z in ZONES.values())
    bad = bad or any(bb[2] > b[0] - 2 and bb[0] < b[2] + 2 and bb[3] > b[1] - 2 and bb[1] < b[3] + 2 for b in OBJ_BOX)
    bad = bad or bb[0] < 4 or bb[2] > 1187 or bb[1] < 258
    bad = bad or _occludes_road(bb[0], bb[1], bb[2], bb[3] - 2.0)
    # R16 나무 화면 상자가 SUPPORT 핀 선(±4pt)과 겹치면 지움
    bad = bad or any(bb[2] > min(a_[0], b_[0]) - 4 and bb[0] < max(a_[0], b_[0]) + 4 and bb[3] > min(a_[1], b_[1]) - 4 and bb[1] < max(a_[1], b_[1]) + 4 for a_, b_ in PIN_SEGS)
    if bad:
        bpy.data.objects.remove(t, do_unlink=True); removed_t += 1; n_tree -= 1
print('trees removed by postcheck', removed_t, 'reject', REJ)
tri_tree = sum(len(m.polygons) for m in PINES + CYPR)
print('roads', {k: U.tri_count(o) for k, o in roads.items()}, 'fields tris', U.tri_count(fields), 'centuriae', int(ok.sum()),
      'trees', n_tree, 'tree template faces', tri_tree)
