"""지형 2D 다각형(화면 pt = 땅 z=0 기준) 계산 → assets/terrain_polys.json
- sea: water.json 'Vector' 해안선을 좌우·아래로 넓힘
- river: 아래 구간 = water.json 'Vector_12'(v>=770), 위 구간 = 북쪽 골짜기로 다시 그린 물길(실제 지리)
- land: 프레임(+여유) − sea − river, 구속 들로네 삼각형
시스템 python3(shapely 2.1)로 실행.
"""
import json
import shapely
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_B/'
W = json.load(open(ROOT + 'ref/svg/water.json'))
get = lambda i: [e for e in W if e['id'] == i][0]['pts']
M = 9   # 프레임 밖 여유(pt) = A2 재단 여백 3mm (카메라에서 땅이 정확히 포스터 직사각형으로 보이게)

coast = get('Vector')
# 해안선 = 첫 점들 중 v가 바다 위쪽 경계인 부분 (0,1335)…(1191,1600)
line = [p for p in coast if not (p[1] >= 1683)]
line = [p for p in line if p != [1191.0, 1684.0] and p != [0.0, 1684.0]]
line = [tuple(p) for p in line][:11]
# CHAIKIN(R9): 해안선 꺾인 모서리를 부드럽게(4번)
for _ in range(4):
    nl = [line[0]]
    for (ax, ay), (bx, by) in zip(line[:-1], line[1:]):
        nl += [(0.75 * ax + 0.25 * bx, 0.75 * ay + 0.25 * by), (0.25 * ax + 0.75 * bx, 0.25 * ay + 0.75 * by)]
    nl.append(line[-1]); line = nl
sea = Polygon([(-M, line[0][1] - 0.36 * M)] + line + [(1191 + M, line[-1][1] + 0.15 * M),
                                                     (1191 + M, 1684 + 2 * M), (-M, 1684 + 2 * M)]).buffer(0)

river_full = Polygon(get('Vector_12')).buffer(0)
# 실제 지리(북동쪽이 화면 위): 티베르강은 북쪽(화면 왼쪽 위) 산골짜기에서 내려와 로마 서쪽을 지나 남서쪽(화면 아래) 오스티아로.
# → 스케치 강의 아래 구간(v >= 770)은 그대로, 위 구간(수도교 발치에서 나오던 물길)은 북쪽 골짜기로 다시 그림.
from shapely.geometry import LineString
lower = river_full.intersection(box(-M, 770, 1191 + M, 1684 + 2 * M))
if lower.geom_type != 'Polygon':
    lower = max(lower.geoms, key=lambda g: g.area)
UPPER = [(291, 810), (290, 772), (284, 730), (272, 680), (258, 620), (244, 560), (230, 500), (213, 440), (192, 380), (170, 345), (146, 324)]   # R8 아래 강 가운데(290.5)·폭(23)에서 그대로 이어짐
# 16:35 강은 산골짜기(테르미닐로·젠나로 사이)에서 시작 — 헤더 글 아래로 지나가지 않게
# 16:40 위로 갈수록 가늘어지는 물줄기(발원지는 산골짜기에서 가늘게 시작)
_L = LineString(UPPER); _n = 60
upper = unary_union([Point(_L.interpolate(i / _n, normalized=True)).buffer(23 - 17 * (i / _n) ** 1.3, 24) for i in range(_n + 1)])
river = unary_union([lower, upper]).buffer(30, 48).buffer(-30, 48).buffer(-5, 48).buffer(5, 48)   # R8 이음매 굽이 없애기(닫기 30 + 열기 5)
if river.geom_type == 'MultiPolygon':
    river = max(river.geoms, key=lambda g: g.area)

frame = box(-M, -M, 1191 + M, 1684 + 2 * M)
land = frame.difference(sea).difference(river)   # R6: 위 띠도 땅 메시가 맡음(옛 산 높이장 메시는 없앰)
land = land.simplify(0.15)
tris = shapely.constrained_delaunay_triangles(land)
T = [list(t.exterior.coords)[:3] for t in tris.geoms]

def rings(g):
    gs = g.geoms if g.geom_type == 'MultiPolygon' else [g]
    return [[list(p.exterior.coords)] + [list(i.coords) for i in p.interiors] for p in gs]

out = {'sea': rings(sea), 'river': rings(river), 'land': rings(land), 'land_tris': T,
       'note': '좌표 = 화면 pt (땅 z=0 평면 위 점이 보이는 자리)'}
json.dump(out, open(ROOT + 'assets/terrain_polys.json', 'w'))
print('sea', sea.area, 'river', river.area, 'land', land.area, 'tris', len(T), 'land parts', len(rings(land)))
print('river bounds', river.bounds)
