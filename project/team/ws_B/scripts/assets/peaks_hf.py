"""아펜니노 봉우리 하나하나를 화산(베수비오 스캔)처럼: 실제 고도(z12 ≈ 29 m)에서 정상 둘레를 원형으로 잘라내고 가장자리를 땅으로 낮춤.
→ assets/peaks/<이름>.npz  (x, y: -1..1 정규 좌표, h: 0..1 정규 높이, 실제 반지름 km·높이 km)
시스템 python3: python3 peaks_hf.py <z12 타일 폴더>
"""
import glob
import math
import os
import sys

import numpy as np
from PIL import Image

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_B/'
DEM = sys.argv[1]
OUT = ROOT + 'assets/peaks/'
os.makedirs(OUT, exist_ok=True)
Z = 12
PEAKS = {   # 이름: (위도, 경도, 잘라낼 반지름 km)
    'terminillo': (42.4706, 12.9897, 5.5),
    'gennaro': (42.0657, 12.8327, 4.5),
    'corno_grande': (42.4695, 13.5658, 6.5),
    'velino': (42.1543, 13.3858, 6.0),
    'autore': (41.9197, 13.1950, 5.0),
    'viglio': (41.8851, 13.3795, 5.0),
}
tiles = {}
for p in glob.glob(os.path.join(DEM, 't_*.png')):
    _, x, y = os.path.basename(p)[:-4].split('_'); tiles[(int(x), int(y))] = p
cache = {}


def tile(x, y):
    if (x, y) not in cache:
        a = np.asarray(Image.open(tiles[(x, y)]).convert('RGB'), dtype=np.float32)
        cache[(x, y)] = a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768
    return cache[(x, y)]


def dem(lon, lat):
    n = 2 ** Z
    px = (lon + 180) / 360 * n * 256
    py = (1 - np.log(np.tan(np.radians(lat)) + 1 / np.cos(np.radians(lat))) / math.pi) / 2 * n * 256
    out = np.zeros(np.shape(lon), np.float32)
    ix = np.floor(px).astype(int); iy = np.floor(py).astype(int)
    for k in np.ndindex(out.shape):
        X, Y = ix[k], iy[k]
        t = tile(X // 256, Y // 256)
        out[k] = t[Y % 256, X % 256]
    return out


def smooth01(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


N = 121
for name, (la, lo, rk) in PEAKS.items():
    g = np.linspace(-1, 1, N)
    X, Y = np.meshgrid(g, g, indexing='ij')          # X: 동(+), Y: 북(+)
    lat = la + Y * rk / 111.0
    lon = lo + X * rk / (111.32 * math.cos(math.radians(la)))
    e = dem(lon, lat).astype(np.float64)
    r = np.hypot(X, Y)
    rim = e[(r > 0.92) & (r < 1.0)]
    base = float(np.percentile(rim, 30))
    h = np.clip(e - base, 0, None)
    h *= 1 - smooth01((r - 0.72) / 0.28)               # 가장자리 테이퍼(화산과 같은 방식)
    h[r > 1.0] = 0
    hk = float(h.max()) / 1000.0
    h = h / max(1e-9, h.max())
    np.savez_compressed(OUT + name + '.npz', x=X, y=Y, h=h, radius_km=rk, height_km=hk, summit_m=float(e.max()))
    print(name, 'summit', int(e.max()), 'm  base', int(base), 'm  relief', round(hk, 2), 'km  r', rk, 'km')
