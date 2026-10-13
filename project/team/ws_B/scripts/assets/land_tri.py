"""땅 메시 v2 (R6): 격자를 해안·강 다각형에 '끌어다 붙이던' 방식은 둑 벽이 주름지고 해안이 톱니가 됨 →
화면 pt 평면에서 땅 다각형(프레임 − 바다 − 강)을 직접 삼각분할:
- 경계: 다각형 고리를 1.6pt 간격으로 촘촘히
- 안쪽: 3.5pt 격자 점(경계에서 2pt 넘게 떨어진 것만)
- scipy Delaunay → 무게중심이 땅 안인 삼각형만
→ assets/land_tri.npz (uv, faces, rings: 경계 고리별 꼭짓점 번호 목록)
시스템 python3: python3 land_tri.py
"""
import json

import numpy as np
from scipy.spatial import Delaunay
import shapely
from shapely.geometry import Polygon, Point

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_B/'
P = json.load(open(ROOT + 'assets/terrain_polys.json'))
polys = [Polygon(r[0], r[1:]) for r in P['land']]
STEP_B, STEP_I = 1.6, 3.5
pts, rings = [], []


def densify(ring):
    ring = np.asarray(ring, float)
    if np.allclose(ring[0], ring[-1]):
        ring = ring[:-1]
    out = []
    n = len(ring)
    for i in range(n):
        a, b = ring[i], ring[(i + 1) % n]
        L = np.linalg.norm(b - a); k = max(1, int(np.ceil(L / STEP_B)))
        for t in range(k):
            out.append(a + (b - a) * t / k)
    return np.array(out)


for poly in polys:
    for ring in [poly.exterior.coords] + [i.coords for i in poly.interiors]:
        d = densify(list(ring))
        idx = list(range(len(pts), len(pts) + len(d)))
        pts.extend(d.tolist()); rings.append(idx)
nb = len(pts)
minx, miny, maxx, maxy = shapely.unary_union(polys).bounds
gx, gy = np.meshgrid(np.arange(minx, maxx, STEP_I), np.arange(miny, maxy, STEP_I), indexing='ij')
G = np.c_[gx.ravel(), gy.ravel()]
land = shapely.unary_union(polys)
inside = shapely.contains_xy(land, G[:, 0], G[:, 1])
G = G[inside]
bnd = shapely.boundary(land)
dist = shapely.distance(bnd, shapely.points(G))
G = G[dist > 2.0]
# BEACH_ROWS (워커 B · 비평 5): 해안·강둑 비탈을 고르게 그리도록 물가와 나란한 점 줄을 촘촘히(격자 점은 그 띠에서 뺌)
_P0 = json.load(open(ROOT + 'assets/terrain_polys.json'))
_seaP = Polygon(_P0['sea'][0][0]).buffer(0); _rivP = Polygon(_P0['river'][0][0]).buffer(0)
_dsG = shapely.distance(_seaP.boundary, shapely.points(G)); _drG = shapely.distance(_rivP.boundary, shapely.points(G))
G = G[(_dsG > 25.0) & (_drG > 11.5)]
_rows = []


def _aligned_rows(poly, ds, sp, other):
    """물가 고리를 호 길이 sp로 나누고, 부드럽게 한 법선 방향으로 ds만큼 밀어낸 점 줄(줄끼리 같은 위치에 정렬 → 비탈 음영이 고름)."""
    ring = np.asarray(poly.exterior.coords)[:-1]
    seg = np.r_[0, np.cumsum(np.hypot(*np.diff(np.r_[ring, ring[:1]], axis=0).T))]
    L = seg[-1]; n = int(L / sp); t = np.arange(n) * L / n
    P = np.c_[np.interp(t, seg, np.r_[ring[:, 0], ring[0, 0]]), np.interp(t, seg, np.r_[ring[:, 1], ring[0, 1]])]
    Tg = np.roll(P, -4, 0) - np.roll(P, 4, 0)
    for _ in range(6):
        Tg = 0.25 * np.roll(Tg, 1, 0) + 0.5 * Tg + 0.25 * np.roll(Tg, -1, 0)
    Tg /= np.linalg.norm(Tg, axis=1, keepdims=True) + 1e-12
    Nn = np.c_[Tg[:, 1], -Tg[:, 0]]
    # 바깥(물 밖) 쪽 법선으로 맞춤
    probe = P + Nn * 0.8
    out = ~shapely.contains_xy(poly, probe[:, 0], probe[:, 1])
    Nn = np.where(out[:, None], Nn, -Nn)
    on_land = shapely.contains_xy(land, (P + Nn * 0.5)[:, 0], (P + Nn * 0.5)[:, 1])
    res = []
    for d in ds:
        Q = P + Nn * d
        dd = shapely.distance(poly.boundary, shapely.points(Q))
        ok = on_land & (np.abs(dd - d) < 0.35) & shapely.contains_xy(land, Q[:, 0], Q[:, 1])
        ok &= shapely.distance(bnd, shapely.points(Q)) > 0.6
        if other is not None:
            ok &= shapely.distance(other.boundary, shapely.points(Q)) > 0.8
        res.append(Q[ok])
    return np.concatenate(res)


_rows.append(_aligned_rows(_seaP, (1.0, 2.2, 3.6, 5.2, 7.0, 9.0, 11.3, 13.8, 16.6, 19.6, 22.8), 1.7, _rivP))
_rows.append(_aligned_rows(_rivP, (0.9, 2.0, 3.3, 4.8, 6.6, 8.8, 11.0), 1.6, _seaP))
# RANGE_DENSE (워커 B · 비평 6): 산괴 띠(range_relief E>0.01)는 1.6pt 격자로 촘촘히 — 실제 고도의 능선·골짜기가 보이게
from scipy.interpolate import RegularGridInterpolator as _RGI
_RR = np.load(ROOT + 'assets/range_relief.npz')
_ru = float(_RR['u0']) + np.arange(_RR['E'].shape[0]) * float(_RR['step']); _rv = float(_RR['v0']) + np.arange(_RR['E'].shape[1]) * float(_RR['step'])
_Ef = _RGI((_ru, _rv), _RR['E'].astype(np.float64), bounds_error=False, fill_value=0.0)
_Rf = _RGI((_ru, _rv), _RR['R'].astype(np.float64), bounds_error=False, fill_value=0.0)
G = G[(_Ef(G) < 0.01) & (_Rf(G) < 0.004)]
_dx, _dy = np.meshgrid(np.arange(_ru[0], _ru[-1], 1.9), np.arange(_rv[0], _rv[-1], 1.9), indexing='ij')   # 봉우리를 합친 뒤에도 T_land 50만 삼각형 이하
_D = np.c_[_dx.ravel(), _dy.ravel()]
_D = _D[(_Ef(_D) >= 0.01) | (_Rf(_D) >= 0.004)]   # 봉우리 기슭(skirt)만 있는 곳(왼쪽 끝 테르미닐로)도 촘촘히 — 3.5pt 격자에서 생기던 세로 줄무늬
_D = _D[shapely.contains_xy(land, _D[:, 0], _D[:, 1])]
_D = _D[shapely.distance(bnd, shapely.points(_D)) > 2.0]
_rows.append(_D)
_rows = np.concatenate(_rows) if _rows else np.zeros((0, 2))
pts = np.array(pts + _rows.tolist() + G.tolist())
tri = Delaunay(pts)
F = tri.simplices
cen = pts[F].mean(1)
keep = shapely.contains_xy(land, cen[:, 0], cen[:, 1])
F = F[keep]
_P2 = json.load(open(ROOT + 'assets/terrain_polys.json'))
_sea = Polygon(_P2['sea'][0][0]).buffer(0); _riv = Polygon(_P2['river'][0][0]).buffer(0)
dist_sea = shapely.distance(_sea.boundary, shapely.points(pts))      # R13 바다 해안까지(프레임 가장자리 제외)
dist_riv = shapely.distance(_riv.boundary, shapely.points(pts))      # 강둑까지
dist_all = np.minimum(dist_sea, dist_riv)
ring_flat = np.concatenate([np.array(r, dtype=np.int64) for r in rings])
ring_off = np.cumsum([0] + [len(r) for r in rings]).astype(np.int64)   # 고리 k = ring_flat[off[k]:off[k+1]] (pickle 없이 저장)
np.savez_compressed(ROOT + 'assets/land_tri.npz', uv=pts, faces=F, nb=nb, ring_flat=ring_flat, ring_off=ring_off, dist=dist_all, dist_sea=dist_sea, dist_riv=dist_riv)
print('verts', len(pts), 'boundary', nb, 'faces', len(F), 'rings', len(rings))
