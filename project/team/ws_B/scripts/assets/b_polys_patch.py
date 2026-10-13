"""워커 B (시스템 python3): 실험실 섬이 바다 위 '떠 있는 섬'으로 보이던 것 → 해안에서 섬 밑까지 이어지는 작은 곶(headland).
원본 backup_r16/terrain_polys.orig.json 에서 sea − 곶, land ∪ 곶 → assets/terrain_polys.json"""
import json
import shapely
from shapely.geometry import Polygon, Point
from shapely import affinity
ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_B/'
P = json.load(open(ROOT + 'backup_r16/terrain_polys.orig.json'))
sea = Polygon(P['sea'][0][0]).buffer(0)
land = shapely.unary_union([Polygon(r[0], r[1:]) for r in P['land']])
blob = affinity.scale(Point(591, 1568).buffer(1.0, quad_segs=32), 50, 33)
neck = Polygon([(566, 1505), (618, 1505), (624, 1560), (560, 1560)])
cape = shapely.unary_union([blob, neck]).intersection(sea)
# 폼페이 공사현장·폼페이 받침이 해안 비탈 끝에 걸쳐 떠 보이던 것 → 그 앞 해안선을 12pt쯤 바다 쪽으로(글 상자 위까지만)
shelf = Polygon([(622, 1500), (622, 1525), (650, 1535), (700, 1540), (760, 1540.5), (820, 1537), (870, 1535.5), (915, 1536), (945, 1540), (955, 1500)])
cape = shapely.unary_union([cape, shelf.intersection(sea)])
# 강 발원 끝(폭 6pt 미만의 가는 꼬리)은 땅으로 메움 — 물 꼬리가 구릉 비탈에 반쯤 묻혀 유령 구조물처럼 보이던 것(심사 3회)
riv = Polygon(P['river'][0][0]).buffer(0)
from shapely.geometry import box as _box
tail = riv.intersection(_box(-20, -20, 400, 346))
riv2 = riv.difference(_box(-20, -20, 400, 346)).buffer(2.5, quad_segs=8).buffer(-2.5, quad_segs=8)
if riv2.geom_type == 'MultiPolygon':
    riv2 = max(riv2.geoms, key=lambda g: g.area)
P['river'] = [[[list(map(float, c)) for c in riv2.exterior.coords]]]
land = shapely.unary_union([land, tail.buffer(0.5)])
new_land = shapely.unary_union([land, cape]).buffer(7, quad_segs=16).buffer(-7, quad_segs=16)
new_land = new_land.difference(riv2)
new_land = new_land.intersection(land.envelope)
new_sea = sea.difference(new_land.buffer(0.01)).buffer(0)
if new_sea.geom_type == 'MultiPolygon':
    new_sea = max(new_sea.geoms, key=lambda g: g.area)
if new_land.geom_type == 'MultiPolygon':
    new_land = max(new_land.geoms, key=lambda g: g.area)
P['sea'] = [[[list(map(float, c)) for c in new_sea.exterior.coords]]]
P['land'] = [[[list(map(float, c)) for c in new_land.exterior.coords]] + [[list(map(float, c)) for c in i.coords] for i in new_land.interiors]]
json.dump(P, open(ROOT + 'assets/terrain_polys.json', 'w'))
print('cape area', round(cape.area), 'sea', round(sea.area), '->', round(new_sea.area), 'land holes', len(new_land.interiors))
