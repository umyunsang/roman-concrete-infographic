"""아펜니노 산맥 v2 (15:23 사용자: "헤더 때문에 산맥이 안 보임 → 더 넓은 공간에, 화산 모델링과 비슷한 느낌으로")
- 자리: 헤더(제목·BASIC, v ≤ 252) 아래 띠. 산 꼭대기의 화면 높이가 v 258 아래로 내려오도록 '전체 높이 배율'을 자동으로 정함(잘라서 평평한 봉우리 만들지 않음).
- 앞 경계(산 기슭 선) F(u): 왼쪽 DETAIL ① 글·모형 위(≤ 350), 가운데 강~CORE ① 왼쪽(≤ 440), CORE ① 위(≤ 366), 수도교 뒤(≤ 350).
- 모양: 실제 고도(AWS Terrain Tiles z11, 로마 북동쪽 사비나~티부르티니~심브루이니~에르니치)를 세계 좌표에 닮음 변환으로 놓고,
  화산 스캔처럼 가파르고(높이 지수 1.35, 기슭 기준 고도 이하 잘라냄) 능선이 날카롭게(언샤프) — 매끈한 담요 모양 X.
- 티베르강: 산 사이 골짜기에서 나옴(강에서 거리로 골 파기).
입력: assets/mtn_grid.npz(Blender: 2pt 화면 격자 → 세계 좌표·상승량), terrain_hf.npz(밑땅 높이), terrain_polys.json(강)
출력: assets/mtn_hf.npz (h = 밑땅 위 산 높이)
시스템 python3: python3 mountains_hf.py <z11 타일 폴더>
"""
import glob
import json
import math
import os
import sys

import numpy as np
from PIL import Image

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_probe/'
DEM = sys.argv[1]
G = np.load(ROOT + 'assets/mtn_grid.npz')
uu, vv, WX, WY, RISE = G['u'], G['v'], G['wx'], G['wy'], G['rise']
GS = float(uu[1, 0] - uu[0, 0])


def smooth01(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def gblur(a, sig):
    r = max(1, int(3 * sig)); x = np.arange(-r, r + 1); k = np.exp(-x * x / (2 * sig * sig)); k /= k.sum()
    a = np.apply_along_axis(lambda m: np.convolve(np.pad(m, r, mode='edge'), k, mode='valid'), 0, a)
    return np.apply_along_axis(lambda m: np.convolve(np.pad(m, r, mode='edge'), k, mode='valid'), 1, a)


# ---- DEM ----
Z = 11
tiles = {}
for p in glob.glob(os.path.join(DEM, 't_*.png')):
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


# ---- 세계 → 지리 (화면 위 = 방위 30°, 화면 오른쪽 = 120°) ----
BETA = math.radians(29.8)
up = np.array([-1.0, 1.0]) / math.sqrt(2); right = np.array([1.0, 1.0]) / math.sqrt(2)
W0 = np.array([-74.0, 74.0])          # 띠 가운데(화면 ≈ (600, 340))의 세계 좌표
KM_PER_UNIT = 0.36                     # 띠 너비(≈ 205 단위) ↔ 약 74 km
LAT0, LON0 = 42.02, 12.98              # 띠 가운데 = 사비나·심브루이니 사이
d = np.stack([WX, WY], -1) - W0
wu = d @ up; wr = d @ right
E = KM_PER_UNIT * (wu * math.sin(BETA) + wr * math.cos(BETA))
N = KM_PER_UNIT * (wu * math.cos(BETA) - wr * math.sin(BETA))
lat = LAT0 + N / 111.0; lon = LON0 + E / (111.32 * math.cos(math.radians(LAT0)))
elev = dem(lon, lat)

# ---- 산 모양: 기준 고도 이하 잘라 기슭을 또렷이, 지수로 가파르게, 언샤프로 능선 날카롭게 ----
E0 = 420.0
Hn = np.clip(elev - E0, 0, None) / 1000.0
Hn = gblur(Hn, 0.6)
Hn = Hn + 0.8 * (Hn - gblur(Hn, 3.0))          # 능선·골 강조
Hn = np.clip(Hn, 0, None) ** 1.35

# ---- 앞 경계(산 기슭 선) ----
FRONT = np.array([(-10, 350), (190, 352), (215, 425), (300, 440), (470, 440), (505, 366), (690, 366),
                  (740, 352), (1202, 348)], float)
F = np.interp(uu[:, 0], FRONT[:, 0], FRONT[:, 1])[:, None]
Hn *= smooth01((F - vv) / 46.0)                  # 기슭 선에서 0, 46pt 안쪽부터 제 높이
Hn *= smooth01((vv - 262) / 55.0)                # 헤더(≤252) 뒤 땅엔 산을 두지 않음 — 산 전체가 헤더 아래에 보이게
# 강 골짜기
R = np.asarray(json.load(open(ROOT + 'assets/terrain_polys.json'))['river'][0][0])
best = np.full(uu.shape, 1e9)
for (ax, ay), (bx, by) in zip(R[:-1], R[1:]):
    dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy + 1e-12
    t = np.clip(((uu - ax) * dx + (vv - ay) * dy) / L2, 0, 1)
    best = np.minimum(best, np.hypot(uu - (ax + t * dx), vv - (ay + t * dy)))
Hn *= smooth01((best - 6) / 40.0)
# 좌우 끝
Hn *= smooth01((uu + 10) / 30.0) * smooth01((1202 - uu) / 30.0)

# ---- 높이: 자리마다 '헤더 아래(v ≥ TOP)까지 솟을 수 있는 높이'에 비례 → 잘림·평평한 봉우리 없이 전부 보임 ----
TOP = 262.0
A = Hn / max(1e-9, float(Hn.max()))
H = 0.94 * A * np.clip(vv - TOP, 0, None) / RISE
K = float(H.max())
# 밑땅 높이(terrain_hf, 3.5pt 격자)
T = np.load(ROOT + 'assets/terrain_hf.npz')
tu0 = float(T['u'][0, 0]); tst = float(T['u'][1, 0] - T['u'][0, 0]); TH = T['h'].astype(np.float64)
fi = (uu - tu0) / tst; fj = (vv - tu0) / tst
i0 = np.clip(np.floor(fi).astype(int), 0, TH.shape[0] - 2); j0 = np.clip(np.floor(fj).astype(int), 0, TH.shape[1] - 2)
a = np.clip(fi - i0, 0, 1); b = np.clip(fj - j0, 0, 1)
base = (TH[i0, j0] * (1 - a) + TH[i0 + 1, j0] * a) * (1 - b) + (TH[i0, j0 + 1] * (1 - a) + TH[i0 + 1, j0 + 1] * a) * b
np.savez_compressed(ROOT + 'assets/mtn_hf.npz', u=uu.astype(np.float32), v=vv.astype(np.float32), h=H.astype(np.float32),
                    base=base.astype(np.float32), front=FRONT)
top_v = (vv - H * RISE)[H > 0.05]
print('max H(units)', round(K, 2), 'max H', round(float(H.max()), 2), 'cells>0.05', int((H > 0.05).sum()),
      'highest screen v', round(float(top_v.min()), 1), 'elev range', int(elev.min()), int(elev.max()))
