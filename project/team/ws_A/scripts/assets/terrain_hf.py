"""맵 전체 땅 높이장 (v2, 2026-10-07 14:25 사용자: "산맥을 좀 줄이고, 높낮이가 느껴지도록(등고선, 울퉁불퉁)")
→ assets/terrain_hf.npz  (Blender: terrain_mesh.py가 메시 T_land로 만든다)

입력
- assets/full_grid.npz : 화면 pt 격자(u, v; 2.5pt), 땅 위 세계 좌표(wx, wy), 높이 1단위의 화면 상승 rise (Blender에서 원근 카메라로 계산)
- assets/terrain_polys.json : 바다·강 다각형(화면 pt)
- assets/object_footprints.json : 오브젝트 바닥 발자국(화면 pt 상자) → 그 자리는 z=0 평탄지
- sketch_v2/text_zones.json : 글 자리 → 기복을 약하게(논밭 평야)
- 실제 고도(AWS Terrain Tiles z10) : 위 띠 산지(사비나~심브루이니), apennines_dem.py와 같은 지도 변환

높이 = 산지(실제 고도, 줄임) + 평야 기복(세계 좌표 잡음: 완만한 구릉 + 잔요철) + 실제 구릉(알바노 화산 구릉·분화구 호수, 레피니 산줄기)
      → 강 골짜기·해안·오브젝트 자리·글 자리 처리 → 약한 계단(등고선 단) → 프레임 위 안 넘기
시스템 python3: python3 terrain_hf.py <dem 타일 폴더>
"""
import glob
import json
import math
import os
import sys

import numpy as np
from PIL import Image

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_A/'
DEM_DIR = sys.argv[1]
G = np.load(ROOT + 'assets/full_grid.npz')
uu, vv, WX, WY, RISE = G['u'], G['v'], G['wx'], G['wy'], G['rise']
GS = float(uu[1, 0] - uu[0, 0])           # 격자 간격(pt)

# ---------- 공용 ----------
def smooth01(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def gblur(a, sig):
    r = int(3 * sig); x = np.arange(-r, r + 1); k = np.exp(-x * x / (2 * sig * sig)); k /= k.sum()
    a = np.apply_along_axis(lambda m: np.convolve(np.pad(m, r, mode='edge'), k, mode='valid'), 0, a)
    return np.apply_along_axis(lambda m: np.convolve(np.pad(m, r, mode='edge'), k, mode='valid'), 1, a)


def ring_dist(ring, x, y):
    ring = np.asarray(ring)
    best = np.full(x.shape, 1e9)
    for (ax, ay), (bx, by) in zip(ring[:-1], ring[1:]):
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy + 1e-12
        t = np.clip(((x - ax) * dx + (y - ay) * dy) / L2, 0, 1)
        best = np.minimum(best, np.hypot(x - (ax + t * dx), y - (ay + t * dy)))
    return best


def ring_inside(ring, x, y):
    ring = np.asarray(ring)
    res = np.zeros(x.shape, dtype=bool)
    xi, yi = ring[:, 0], ring[:, 1]; xj, yj = np.roll(xi, 1), np.roll(yi, 1)
    for a, b, c, d in zip(xi, yi, xj, yj):
        cond = (b > y) != (d > y)
        with np.errstate(divide='ignore', invalid='ignore'):
            xint = (c - a) * (y - b) / (d - b + 1e-12) + a
        res ^= cond & (x < xint)
    return res


def box_dist(b, x, y):
    dx = np.maximum(np.maximum(b[0] - x, x - b[2]), 0); dy = np.maximum(np.maximum(b[1] - y, y - b[3]), 0)
    return np.hypot(dx, dy)


# ---------- 1. 산지(실제 고도) ----------
Z = 10
tiles = {}
for p in glob.glob(os.path.join(DEM_DIR, 't_*.png')):
    _, x, y = os.path.basename(p)[:-4].split('_'); tiles[(int(x), int(y))] = p
xs = sorted({k[0] for k in tiles}); ys = sorted({k[1] for k in tiles}); TX0, TY0 = xs[0], ys[0]
mos = np.zeros((len(ys) * 256, len(xs) * 256), dtype=np.float32)
for (x, y), p in tiles.items():
    a = np.asarray(Image.open(p).convert('RGB'), dtype=np.float32)
    mos[(y - TY0) * 256:(y - TY0 + 1) * 256, (x - TX0) * 256:(x - TX0 + 1) * 256] = a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768


def dem(lon, lat):
    n = 2 ** Z
    px = ((lon + 180) / 360 * n - TX0) * 256
    py = ((1 - np.log(np.tan(np.radians(lat)) + 1 / np.cos(np.radians(lat))) / math.pi) / 2 * n - TY0) * 256
    x0 = np.clip(np.floor(px).astype(int), 0, mos.shape[1] - 2); y0 = np.clip(np.floor(py).astype(int), 0, mos.shape[0] - 2)
    fx = np.clip(px - x0, 0, 1); fy = np.clip(py - y0, 0, 1)
    return (mos[y0, x0] * (1 - fx) + mos[y0, x0 + 1] * fx) * (1 - fy) + (mos[y0 + 1, x0] * (1 - fx) + mos[y0 + 1, x0 + 1] * fx) * fy


LAT0, LON0 = 42.0, 12.8
KX = 111.32 * math.cos(math.radians(LAT0)); KY = 111.0
gA = complex((12.565 - LON0) * KX, (42.075 - LAT0) * KY); gB = complex((13.02 - LON0) * KX, (41.95 - LAT0) * KY)
sA = complex(240.0, -530.0); sB = complex(1060.0, -392.0)
T = (sB - sA) / (gB - gA)
g = (uu - 1j * vv - sA) / T + gA
lon, lat = LON0 + g.real / KX, LAT0 + g.imag / KY
K_MTN = 7.0                                  # 단위/km (v1 11 → 줄임)
Hm = np.clip(dem(lon, lat) - 120.0, 0, None) / 1000.0 * K_MTN
Hm = gblur(Hm, 4.0 / GS)
HM = float(Hm.max()); Hm = HM * (Hm / HM) ** 1.2
Hm *= 1 - smooth01((vv - 210) / 170.0)       # 산은 위 띠에만 (v 210까지 그대로, 380에서 0) — v1보다 얕게
Hm *= smooth01(np.minimum(uu, 1191 - uu) / 120.0)
Hm *= 0.0                                    # 15:23 산맥은 따로 만든 L01_apennines(mountains_hf.py)로 — 밑땅은 낮은 구릉만

# ---------- 2. 평야 기복 (세계 좌표 잡음) ----------
rng = np.random.default_rng(7)


def fbm(x, y, lam_min, lam_max, n, amp_pow=1.0):
    out = np.zeros_like(x)
    lams = np.exp(rng.uniform(np.log(lam_min), np.log(lam_max), n))
    for lam in lams:
        th = rng.uniform(0, math.pi); ph = rng.uniform(0, 2 * math.pi)
        kx, ky = math.cos(th) * 2 * math.pi / lam, math.sin(th) * 2 * math.pi / lam
        out += (lam ** amp_pow) * np.sin(kx * x + ky * y + ph)
    return out / np.sqrt(np.sum(np.exp(rng.uniform(np.log(lam_min), np.log(lam_max), n)) ** (2 * amp_pow)))


roll = fbm(WX, WY, 10.0, 70.0, 28, 1.0)                 # 완만한 구릉
roll = (roll - roll.min()) / (np.ptp(roll) + 1e-9)       # 0..1
roll = 1.35 * roll ** 1.3                                # 낮은 땅 넓게, 언덕은 드문드문
bump = fbm(WX, WY, 1.6, 5.0, 24, 0.6)                   # 잔요철(울퉁불퉁)
bump = 0.0 * bump                                        # 잔요철도 끔(표면 처리 제외)
Hp = roll + bump


# 실제 구릉: 화면 앵커 → 세계 좌표 가우스 언덕
def wpt(u, v):
    i = int(np.clip(round((u - uu[0, 0]) / GS), 0, uu.shape[0] - 1)); j = int(np.clip(round((v - vv[0, 0]) / GS), 0, uu.shape[1] - 1))
    return WX[i, j], WY[i, j]


def hill(u, v, r_world, h):
    cx, cy = wpt(u, v)
    d2 = (WX - cx) ** 2 + (WY - cy) ** 2
    return h * np.exp(-d2 / (2 * r_world ** 2))


# 알바노 화산 구릉(Colli Albani): 로마 남동쪽 — 바깥 고리 + 가운데 분화구(알바노·네미 호수 자리)
cx, cy = wpt(905, 1230)
d = np.hypot(WX - cx, WY - cy)
albani = 1.3 * np.exp(-((d - 9.0) ** 2) / (2 * 5.0 ** 2)) + 0.6 * np.exp(-d ** 2 / (2 * 14.0 ** 2))   # 15:12 베수비오가 더 커 보이게 낮춤(3.2/1.2 → 1.3/0.6)
crater = -0.5 * np.exp(-d ** 2 / (2 * 3.2 ** 2))
# 레피니 산줄기(Monti Lepini): 프리베르눔 뒤(화면 오른쪽), 길쭉한 능선
lep = hill(1120, 960, 9.0, 1.5) + hill(1170, 1010, 8.0, 1.2) + hill(1060, 935, 7.0, 0.9)
# 수도교 수원 쪽 언덕(아니에네 골짜기 입구): 수로가 언덕 속에서 나와 아치로 이어지게
aq_hill = hill(1180, 392, 6.5, 3.4)
Hp = Hp + albani + crater + lep + aq_hill

# ---------- 3. 강·해안·오브젝트·글 자리 ----------
P = json.load(open(ROOT + 'assets/terrain_polys.json'))
river = P['river'][0][0]; sea = P['sea'][0][0]
d_river = ring_dist(river, uu, vv); in_river = ring_inside(river, uu, vv)
d_sea = ring_dist(sea, uu, vv); in_sea = ring_inside(sea, uu, vv)
H = Hm + Hp * (1 - smooth01((210 - vv) / 120.0) * 0.0)   # 산지와 평야 기복을 그냥 더함
H *= smooth01(d_river / 42.0)                             # 강 쪽으로 내려가는 골짜기
H *= smooth01(d_sea / 34.0)                               # 해안 쪽으로 낮아짐
H += 0.12 * smooth01(d_sea / 30.0) * smooth01(d_river / 12.0)   # 땅 전체 0.12 돋움(물체 밑동 잔해를 덮던 기존 값) — 워커 A: 물가 쪽은 DIP 비탈이 맡으므로 30/12pt로 넓혀 둔덕 없앰
FOOT = json.load(open(ROOT + 'assets/object_footprints.json'))
# 사각형 그대로 깎으면 네모난 단이 생김 → 상자를 격자에 찍고 가우스로 흐려 자연스러운 모양의 마스크로
def soft_mask(boxes, pad, sig_pt, ellipse=True):
    m = np.zeros_like(H)
    for b in boxes:
        if ellipse:   # 상자에 외접하는 타원 → 둥근 평탄지
            cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
            rx, ry = (b[2] - b[0]) / 2 * 1.2 + pad, (b[3] - b[1]) / 2 * 1.2 + pad
            m[((uu - cx) / rx) ** 2 + ((vv - cy) / ry) ** 2 <= 1.0] = 1.0
        else:
            m[(uu >= b[0] - pad) & (uu <= b[2] + pad) & (vv >= b[1] - pad) & (vv <= b[3] + pad)] = 1.0
    return np.clip(gblur(m, sig_pt / GS) * 1.7, 0, 1)


M_obj = soft_mask([b for k, b in FOOT.items() if b[3] < 1700 and not k.startswith('L01_')], 4.0, 14.0)
# FOOTHILL: 아펜니노 봉우리(L01_*) 밑은 평탄지 대신 이어진 낮은 구릉 — 봉우리들이 한 산줄기로 이어져 보이게
M_mtn = soft_mask([b for k, b in FOOT.items() if k.startswith('L01_')], 18.0, 26.0)
# 워커 A(비평 6): 봉우리를 하나의 산맥으로 — 봉우리 밑동을 잇는 등줄기(세계 좌표 가우스 띠, 뒤쪽은 넓게·앞쪽은 좁게) + 가지 능선
SPINE = [(-20, 300), (60, 312), (150, 334), (250, 398), (330, 388), (420, 360), (515, 333), (600, 322), (700, 342), (780, 350), (860, 368), (905, 376),
         (965, 386), (1025, 390), (1085, 383), (1130, 376), (1215, 366)]
SW_ = np.array([wpt(u, v) for u, v in SPINE])
def _seg_dist(P, x, y):
    best = np.full(x.shape, 1e9); tpar = np.zeros(x.shape)
    acc = 0.0
    for (ax, ay), (bx, by) in zip(P[:-1], P[1:]):
        dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy + 1e-12
        t = np.clip(((x - ax) * dx + (y - ay) * dy) / L2, 0, 1)
        d = np.hypot(x - (ax + t * dx), y - (ay + t * dy))
        m = d < best; best = np.where(m, d, best); tpar = np.where(m, acc + t * np.sqrt(L2), tpar)
        acc += np.sqrt(L2)
    return best, tpar
dsp, ssp = _seg_dist(SW_, WX, WY)
sp_v = np.interp(uu, [p[0] for p in SPINE], [p[1] for p in SPINE])
back = vv < sp_v
sig = np.where(back, 5.2, 3.6)
amp = 2.3 + 0.55 * np.sin(ssp / 9.0 + 0.7) + 0.3 * np.sin(ssp / 3.7)
spur = 0.5 + 0.5 * np.cos(2 * math.pi * ssp / 5.5 + 1.3 * np.sin(ssp / 7.0))      # 등줄기 방향으로 번갈아 가지 능선·골짜기
fl = np.clip(dsp / sig, 0, 2.5)
Hr = amp * np.exp(-(dsp / sig) ** 2) * (1 - 0.42 * np.clip(fl, 0, 1.2) * (1 - spur))
Hr *= smooth01((uu - 40) / 120.0) * 0.55 + 0.45      # 왼쪽 끝(테르미닐로 쪽) 낮게
# 비우는 곳: 글 상자(헤더 제외)·글 자리 14pt 둘레, 수도교 길 18pt
_FT = json.load(open(ROOT + 'loop/figma_texts.json'))
_TB = [t['b'] for t in _FT if t['kind'] not in ('header', 'title')] + [b for k, b in json.load(open(ROOT + 'sketch_v2/text_zones.json'))['zones'].items() if k not in ('TITLE_BAND', 'TIMELINE')]
M_tx = np.zeros_like(H)
for b in _TB:
    M_tx = np.maximum(M_tx, 1 - smooth01((box_dist(b, uu, vv) - 6.0) / 16.0))
_AQ = np.array([(1186, 398), (1080, 466), (990, 528), (910, 590), (858, 640), (830, 676)], float)
M_aq = 1 - smooth01((ring_dist(_AQ, uu, vv) - 10.0) / 16.0)
Hr *= (1 - M_tx) * (1 - M_aq) * smooth01((vv - 250) / 40.0)
H = H + (0.8 * M_mtn + Hr) * smooth01((d_river - 6) / 34.0)   # R13 강 발원지 둘레엔 구릉 없음
H *= 1 - M_obj                                            # 오브젝트 자리는 z=0 평탄지(가장자리는 부드럽게)
Zs = json.load(open(ROOT + 'sketch_v2/text_zones.json'))['zones']
M_txt = soft_mask([b for k, b in Zs.items() if k not in ('TITLE_BAND', 'TIMELINE')], 0.0, 22.0)
H *= 1 - 0.6 * M_txt                                      # 글 자리는 기복 약하게(평야·논밭)

# ---------- 4. 등고선 단(약한 계단) ----------
TERRACE = False     # 14:32 사용자: "등고선만 제외" → 계단 끔
if TERRACE:
    STEP = 0.24
    f = H / STEP; n = np.floor(f); t = f - n
    s = smooth01((t - 0.5) / 0.30 + 0.5)
    H = np.where(H > 0.03, 0.55 * STEP * (n + s) + 0.45 * H, H)

# ---------- 4b. 표면 질감 — 14:44 사용자: "표면 처리 제외"(무거움) → TEXTURE=False ----------
TEXTURE = False
# 평야: 풀·흙의 잔잔한 울퉁불퉁(두 크기) / 산지: 바위 능선 줄무늬(능선형 잡음, 경사·높이에 비례) / 해안 가까이: 모래 물결
land_w = smooth01(d_sea / 8.0) * smooth01(d_river / 6.0)
grain1 = fbm(WX, WY, 0.7, 1.6, 20, 0.5); grain1 /= np.abs(grain1).max() + 1e-9
grain2 = fbm(WX, WY, 1.8, 4.0, 16, 0.8); grain2 /= np.abs(grain2).max() + 1e-9
ridged = np.zeros_like(WX)
for lam, amp in ((2.2, 1.0), (4.5, 0.8), (1.1, 0.45)):
    th = rng.uniform(0, math.pi); ph = rng.uniform(0, 2 * math.pi)
    k = 2 * math.pi / lam
    ridged += amp * (1 - np.abs(np.sin(k * (math.cos(th) * WX + math.sin(th) * WY) + ph + 0.6 * np.sin(0.37 * k * WY))))
ridged /= ridged.max()
gy, gx = np.gradient(H, GS)
slope = np.clip(np.hypot(gx, gy) * 8.0, 0, 1)            # 화면 pt당 기울기 → 0..1
mtn_w = smooth01(Hm / 2.0)
dune = 0.05 * np.sin(2 * math.pi * (WX * 0.8 + WY * 0.6) / 1.3) * (1 - smooth01((d_sea - 6) / 30.0)) * smooth01(d_sea / 3.0)
texture = (0.11 * grain1 + 0.16 * grain2) * (1 - 0.6 * M_txt) + 0.6 * ridged * mtn_w * (0.4 + 0.6 * slope) + dune
if TEXTURE:
    H = np.where(H > -1, H + texture * land_w * (1 - M_obj), H)
H = np.maximum(H, 0.0)

# ---------- 5. 프레임 안에 다 보이게 ----------
H = H * smooth01((vv - 14.0) / 140.0)          # R7 프레임 위 가장자리: 꺾인 주름 없이 부드럽게 0으로
H = np.where(in_river | in_sea, 0.0, H)
H_rel = H.copy()
# 워커 A(비평 5): 해안 = 케이크 단면 벽 대신 모래사장 비탈(해안선에서 -0.95 → 26pt 안쪽에서 0), 강둑 = 9pt 완만한 비탈(-0.55 → 0)
SEA_DIP, SEA_BW, RIV_DIP, RIV_BW = -0.95, 26.0, -0.85, 9.0
_FPc = [b for k, b in FOOT.items() if k in ('L12_harbor_pilae', 'L08_pompeii', 'L08_pompeii_site', 'L07_vesuvius', 'L09_portus_mole', 'L09_portus_lighthouse')]
M_co = np.zeros_like(H)
for b in _FPc:
    cx_, cy_ = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2; rx_, ry_ = (b[2] - b[0]) / 2 + 4, (b[3] - b[1]) / 2 + 4
    e_ = np.sqrt(((uu - cx_) / rx_) ** 2 + ((vv - cy_) / ry_) ** 2)
    M_co = np.maximum(M_co, 1 - smooth01((e_ - 1.0) / 0.25))
DIP = SEA_DIP * (1 - smooth01((d_sea + SEA_BW * M_co) / SEA_BW)) + RIV_DIP * (1 - smooth01(d_river / RIV_BW))   # 보호 구역은 비탈을 바다 쪽으로 밀기(진폭을 줄이면 수면 높이에 평평한 띠가 생겨 z-충돌)
DIP = np.where(in_river | in_sea, 0.0, DIP)
H = H + DIP

np.savez_compressed(ROOT + 'assets/terrain_hf.npz', step=GS, u=uu.astype(np.float32), v=vv.astype(np.float32),
                    h=H.astype(np.float32), h_rel=H_rel.astype(np.float32), river=in_river, sea=in_sea)
land = ~(in_river | in_sea)
print('grid', H.shape, 'max', float(H.max()), 'mountain max', float(Hm.max()),
      'plain mean', float(H[land & (vv > 500)].mean()), 'plain p95', float(np.percentile(H[land & (vv > 500)], 95)))
