"""아펜니노(로마 북동쪽 실제 산지) 높이장 → assets/apennines_hf.npz
실제 고도: AWS Terrain Tiles(terrarium, z10, 공개 데이터) — 사비나·루크레틸리·티부르티니·프레네스티니·심브루이니(클라우디아 수도교 수원).
지도 방향: 실제 지점 두 곳을 화면 자리에 고정한 닮음 변환(회전+축척) — 화면 위 ≈ 북북동.
  A 티베르강(몬테로톤도 부근 42.075N 12.565E) → 화면 (240, 530)  : 다시 그린 강 위 구간과 같은 자리
  B 클라우디아 수도교 수원(아고스타 부근 41.95N 13.02E) → 화면 (1060, 392) : 수도교 오른쪽 위 끝 너머
높이: (고도 - 100 m) * K, 0 미만 0. 화면에서 높이 h 단위 = 8.165h pt 위로 솟음.
제한(화면 기준):
  - 프레임 위로 안 나감: 솟은 꼭대기 v - 8.165h >= TOP_SAFE
  - 좌우 가장자리 40pt 안에선 낮춤(봉우리가 잘리지 않게)
  - 글 자리(text_zones)·수도교 앞을 가리지 않음: 그 자리보다 앞(아래)에서 솟아 그 자리 안으로 들어오지 못하게
  - 강: 강 다각형 안은 비움(면 삭제는 Blender 쪽), 둑에서 완만히 솟음
  - v 560~660에서 0으로 (로마 평야)
시스템 python3로 실행: python3 apennines_dem.py <dem 타일 폴더>
"""
import glob
import json
import math
import os
import sys

import numpy as np
from PIL import Image

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/'
DEM_DIR = sys.argv[1]
Z = 10
STEP = 2.5                     # 격자 간격(pt)
U0, U1, V0, V1 = -10.0, 1202.5, -10.0, 662.5   # 위 띠 전체(재단 여백 포함) — 이 띠의 땅은 이 메시가 맡고 T_ground는 v>=662.5만
K = 11.0                       # 단위/km (수직 과장)
BASE_M = 100.0
TOP_SAFE = 14.0
RISE = 8.165                   # 높이 1단위 → 화면 pt (정사영 값; 원근이면 아래에서 격자별 값으로 바꿈)

# --- 타일 모자이크 ---
tiles = {}
for p in glob.glob(os.path.join(DEM_DIR, 't_*.png')):
    _, x, y = os.path.basename(p)[:-4].split('_')
    tiles[(int(x), int(y))] = p
xs = sorted({k[0] for k in tiles}); ys = sorted({k[1] for k in tiles})
TX0, TY0 = xs[0], ys[0]
mos = np.zeros((len(ys) * 256, len(xs) * 256), dtype=np.float32)
for (x, y), p in tiles.items():
    a = np.asarray(Image.open(p).convert('RGB'), dtype=np.float32)
    e = a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768
    mos[(y - TY0) * 256:(y - TY0 + 1) * 256, (x - TX0) * 256:(x - TX0 + 1) * 256] = e


def lonlat_to_pix(lon, lat):
    n = 2 ** Z
    x = (lon + 180) / 360 * n
    y = (1 - np.log(np.tan(np.radians(lat)) + 1 / np.cos(np.radians(lat))) / math.pi) / 2 * n
    return (x - TX0) * 256, (y - TY0) * 256


def sample(lon, lat):
    px, py = lonlat_to_pix(lon, lat)
    x0 = np.clip(np.floor(px).astype(int), 0, mos.shape[1] - 2); y0 = np.clip(np.floor(py).astype(int), 0, mos.shape[0] - 2)
    fx = np.clip(px - x0, 0, 1); fy = np.clip(py - y0, 0, 1)
    a = mos[y0, x0]; b = mos[y0, x0 + 1]; c = mos[y0 + 1, x0]; d = mos[y0 + 1, x0 + 1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


# --- 닮음 변환 (km 평면 ↔ 화면 pt) ---
LAT0, LON0 = 42.0, 12.8
KX = 111.32 * math.cos(math.radians(LAT0)); KY = 111.0
geoA = np.array([(12.565 - LON0) * KX, (42.075 - LAT0) * KY])
geoB = np.array([(13.02 - LON0) * KX, (41.95 - LAT0) * KY])
scrA = np.array([240.0, 530.0]); scrB = np.array([1060.0, 392.0])
# 화면 좌표를 (x, -y)로 두면 지도와 같은 손잡이 방향
gA = complex(*geoA); gB = complex(*geoB); sA = complex(scrA[0], -scrA[1]); sB = complex(scrB[0], -scrB[1])
T = (sB - sA) / (gB - gA)       # 회전·축척
print('scale pt/km', abs(T), 'screen-up bearing(deg)', math.degrees(math.atan2((1j / T).real, (1j / T).imag)))


def screen_to_lonlat(u, v):
    s = u - 1j * v
    g = (s - sA) / T + gA
    return LON0 + g.real / KX, LAT0 + g.imag / KY


# --- 격자 ---
uu, vv = np.meshgrid(np.arange(U0, U1 + 1e-6, STEP), np.arange(V0, V1 + 1e-6, STEP), indexing='ij')
_rg = ROOT + 'assets/rise_grid.npz'
if os.path.exists(_rg):
    _R = np.load(_rg)
    assert _R['rise'].shape == uu.shape, (_R['rise'].shape, uu.shape)
    RISE = _R['rise'].astype(np.float64)        # 원근 카메라: 땅 자리마다 높이 1단위의 화면 상승(pt)
    print('rise grid', float(RISE.min()), float(RISE.max()))
lon, lat = screen_to_lonlat(uu, vv)
elev = sample(lon, lat)
H = np.clip(elev - BASE_M, 0, None) / 1000.0 * K

# 잔 소음 줄이기(가우스, 약 0.35 km) — 큰 능선만 남김
def gblur(a, sig):
    r = int(3 * sig); x = np.arange(-r, r + 1); k = np.exp(-x * x / (2 * sig * sig)); k /= k.sum()
    a = np.apply_along_axis(lambda m: np.convolve(np.pad(m, r, mode='edge'), k, mode='valid'), 0, a)
    return np.apply_along_axis(lambda m: np.convolve(np.pad(m, r, mode='edge'), k, mode='valid'), 1, a)
H = gblur(H, 1.8)
# 봉우리는 살리고 기슭은 눌러 능선을 또렷하게
HM = float(H.max()); H = HM * (H / HM) ** 1.25


def smooth01(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


# 산은 뒤쪽 띠에만: v 300까지 그대로, 480에서 0 (그 앞은 로마 평야 Campagna Romana)
H *= 1 - smooth01((vv - 300) / 180.0)
# 좌우 가장자리
edge = np.minimum(uu - 0, 1191 - uu)
H *= smooth01(edge / 120.0)

# 글 자리: 부드럽게 평야로 (자리 안 0, 바깥 36pt에 걸쳐 원래 높이로)
Zs = json.load(open(ROOT + 'sketch_v2/text_zones.json'))['zones']
keep = {k: z for k, z in Zs.items() if k not in ('TITLE_BAND', 'TIMELINE') and z[1] < V1}
MARGIN = 36.0
for k, (x0, y0, x1, y1) in keep.items():
    dx = np.maximum(np.maximum(x0 - uu, uu - x1), 0); dy = np.maximum(np.maximum(y0 - vv, vv - y1), 0)
    d = np.hypot(dx, dy)
    H *= smooth01(d / MARGIN)
# 프레임 위 안 넘기
H = np.minimum(H, np.clip((vv - TOP_SAFE) / RISE, 0, None))
# 글 자리 앞에서 솟아 자리 안으로 들어오는 것 막기(부드럽게 위 처리 뒤 남은 것만)
for k, (x0, y0, x1, y1) in keep.items():
    inx = (uu >= x0 - 6) & (uu <= x1 + 6)
    front = inx & (vv > y1)
    H = np.where(front, np.minimum(H, (vv - y1) / RISE), H)
_aq = ROOT + 'assets/aqueduct_base.json'
AQ = np.array(json.load(open(_aq)) if os.path.exists(_aq) else
              [(803.2, 534.2), (827.2, 521.0), (846.4, 513.2), (868.5, 502.2), (884.2, 491.3), (904.4, 477.4),
               (920.7, 468.4), (944.5, 456.5), (963.6, 445.4), (982.6, 432.9), (1005.9, 420.3)])
aq_base = np.interp(uu, AQ[:, 0], AQ[:, 1], left=np.nan, right=np.nan)
inaq = ~np.isnan(aq_base)
# 수도교 발치 띠(±10pt)는 거의 평지, 그 앞은 수도교 바닥선 위로 못 솟음
near = inaq & (np.abs(vv - np.nan_to_num(aq_base)) < 10)
H = np.where(near, np.minimum(H, 0.15), H)
front = inaq & (vv > np.nan_to_num(aq_base) + 10)
H = np.where(front, np.minimum(H, (vv - np.nan_to_num(aq_base)) / RISE * 0.9), H)

# 강 둑
R = json.load(open(ROOT + 'assets/terrain_polys.json'))['river'][0][0]
R = np.asarray(R)


def dist_to_ring(ring, x, y):
    best = np.full(x.shape, 1e9)
    for (ax, ay), (bx, by) in zip(ring[:-1], ring[1:]):
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy + 1e-12
        t = np.clip(((x - ax) * dx + (y - ay) * dy) / L2, 0, 1)
        best = np.minimum(best, np.hypot(x - (ax + t * dx), y - (ay + t * dy)))
    return best


def inside_ring(ring, x, y):
    res = np.zeros(x.shape, dtype=bool)
    xi, yi = ring[:, 0], ring[:, 1]; xj, yj = np.roll(xi, 1), np.roll(yi, 1)
    for a, b, c, d in zip(xi, yi, xj, yj):
        cond = (b > y) != (d > y)
        with np.errstate(divide='ignore', invalid='ignore'):
            xint = (c - a) * (y - b) / (d - b + 1e-12) + a
        res ^= cond & (x < xint)
    return res


rin = inside_ring(R, uu, vv)
rd = dist_to_ring(R, uu, vv)
H = np.where(rin, 0.0, np.minimum(H, rd / RISE * 1.1))
# 강 바로 앞(아래)에서 솟아 강을 가리지 않게: 같은 열에서 위쪽 강까지 거리
# (강은 위에서 아래로 흐르는 띠 → 열마다 가장 가까운 위쪽 강 칸까지의 v 차)
col_has = rin.any(axis=1)
for i in np.nonzero(col_has)[0]:
    rows = np.nonzero(rin[i])[0]
    for j in range(rin.shape[1]):
        above = rows[rows < j]
        if len(above):
            dv = vv[i, j] - vv[i, above.max()]
            H[i, j] = min(H[i, j], max(0.0, dv / (RISE[i, j] if np.ndim(RISE) else RISE) * 0.95))

np.savez_compressed(ROOT + 'assets/apennines_hf.npz', u=uu.astype(np.float32), v=vv.astype(np.float32),
                    h=H.astype(np.float32), river=rin)
peak = np.unravel_index(H.argmax(), H.shape)
print('grid', H.shape, 'max h', float(H.max()), 'at pt', float(uu[peak]), float(vv[peak]),
      'top screen v', float((vv - H * RISE)[H > 0.05].min()) if (H > 0.05).any() else None)
for name, (la, lo) in {'Monte Gennaro': (42.06, 12.83), 'Monte Autore': (41.92, 13.19), 'Tivoli': (41.96, 12.80),
                       'Monte Guadagnolo': (41.92, 12.92)}.items():
    g = complex((lo - LON0) * KX, (la - LAT0) * KY)
    s = (g - gA) * T + sA
    print(name, round(s.real), round(-s.imag))
