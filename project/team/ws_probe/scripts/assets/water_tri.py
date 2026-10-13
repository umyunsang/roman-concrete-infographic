"""물 수면 v2 (R6): 격자로 자른 수면은 가장자리가 계단 → 바다·강 다각형을 3pt 넓혀 직접 삼각분할(가장자리는 땅 벽 밑으로 들어감)
→ assets/water_tri.npz (sea_uv, sea_f, river_uv, river_f)
시스템 python3: python3 water_tri.py
"""
import json

import numpy as np
import shapely
from scipy.spatial import Delaunay
from shapely.geometry import Polygon

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_probe/'
P = json.load(open(ROOT + 'assets/terrain_polys.json'))


def tri(poly, step_b=1.6, step_i=4.0):
    poly = poly.buffer(3.0).simplify(0.15)
    if poly.geom_type == 'MultiPolygon':
        poly = max(poly.geoms, key=lambda g: g.area)
    pts = []
    for ring in [poly.exterior.coords] + [i.coords for i in poly.interiors]:
        r = np.asarray(ring)[:-1]
        for a, b in zip(r, np.roll(r, -1, axis=0)):
            k = max(1, int(np.ceil(np.linalg.norm(b - a) / step_b)))
            for t in range(k):
                pts.append(a + (b - a) * t / k)
    minx, miny, maxx, maxy = poly.bounds
    gx, gy = np.meshgrid(np.arange(minx, maxx, step_i), np.arange(miny, maxy, step_i), indexing='ij')
    G = np.c_[gx.ravel(), gy.ravel()]
    G = G[shapely.contains_xy(poly, G[:, 0], G[:, 1])]
    G = G[shapely.distance(poly.boundary, shapely.points(G)) > 2.0]
    pts = np.array(pts + G.tolist())
    F = Delaunay(pts).simplices
    c = pts[F].mean(1)
    F = F[shapely.contains_xy(poly, c[:, 0], c[:, 1])]
    return pts, F


s_uv, s_f = tri(Polygon(P['sea'][0][0]))
_sea = Polygon(P['sea'][0][0]).buffer(0)
_riv = Polygon(P['river'][0][0]).buffer(0).difference(_sea.buffer(1.5))   # R10 하구에서 바다 위로 튀어나온 판 없앰
r_uv, r_f = tri(_riv if _riv.geom_type == 'Polygon' else max(_riv.geoms, key=lambda g: g.area))
r_dsea = shapely.distance(_sea, shapely.points(r_uv))
np.savez_compressed(ROOT + 'assets/water_tri.npz', sea_uv=s_uv, sea_f=s_f, river_uv=r_uv, river_f=r_f, river_dsea=r_dsea)
print('sea', len(s_uv), len(s_f), 'river', len(r_uv), len(r_f))
