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

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_A/'
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
# 워커 A(비평 5): 모래사장·강둑 비탈(해안 26pt·강 9pt) 구간은 3.5pt 격자로는 물가선이 톱니 → 해안·강 다각형에서 일정 거리 띠 곡선을 1.6pt 간격으로 촘촘히
from scipy.spatial import cKDTree
_sea0 = Polygon(P['sea'][0][0]).buffer(0); _riv0 = Polygon(P['river'][0][0]).buffer(0)
# 띠 안은 촘촘한 정삼각 격자(1.3pt, 엇갈림) — 평행 곡선 점은 가는 삼각형을 만들어 cavity가 세로 줄무늬를 그림
_band = shapely.union_all([_sea0.buffer(27.0, 32), _riv0.buffer(11.0, 32)]).intersection(land)
_hx = 1.45; _hy = 1.45 * 0.866
_bx0, _by0, _bx1, _by1 = _band.bounds
_yy = np.arange(_by0, _by1, _hy)
OFF = []
for _k, _y in enumerate(_yy):
    _xs = np.arange(_bx0 + (_k % 2) * _hx / 2, _bx1, _hx)
    OFF.append(np.c_[_xs, np.full(len(_xs), _y)])
OFF = np.concatenate(OFF)
OFF = OFF[shapely.contains_xy(_band, OFF[:, 0], OFF[:, 1])]
OFF = np.array(OFF)
OFF = OFF[shapely.distance(bnd, shapely.points(OFF)) > 0.9]
if len(OFF):
    G = G[cKDTree(OFF).query(G)[0] > 1.5]
    pts = np.array(pts + OFF.tolist() + G.tolist())
else:
    pts = np.array(pts + G.tolist())
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
