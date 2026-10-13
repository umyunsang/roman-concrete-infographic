"""땅 표면 질감용 덤불(마키아)·돌 뿌리기 (14:32 사용자: "표면 질감 작업")
- 밭·길·물·오브젝트 자리를 피해서, 언덕·경사·강둑일수록 촘촘히. 글 자리는 아주 드물게.
- 산지(위 띠)에는 바위 덩어리.
- 작은 형태(높이 ≤ 0.5)라 낮은 지형으로 취급(low_terrain).
Blender에서: exec(open(<이 파일>).read())  — fill_plains.py 다음에.
"""
import json
import math
import bpy
import numpy as np
from mathutils import noise, Vector

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_probe/'
U = bpy.data.texts['asset_utils.py'].as_module()
rng = np.random.default_rng(33)
D = np.load(ROOT + 'assets/terrain_hf.npz')
HG = D['h'].astype(np.float64); WET = D['river'] | D['sea']; G0 = float(D['u'][0, 0]); GS = float(D['u'][1, 0] - D['u'][0, 0])
ZONES = [z for k, z in json.load(open(ROOT + 'sketch_v2/text_zones.json'))['zones'].items() if k not in ('TITLE_BAND', 'TIMELINE')]
FOOT = list(json.load(open(ROOT + 'assets/object_footprints.json')).values())


def samp(A, u, v):
    fi = (u - G0) / GS; fj = (v - G0) / GS
    i0 = np.clip(np.floor(fi).astype(int), 0, A.shape[0] - 2); j0 = np.clip(np.floor(fj).astype(int), 0, A.shape[1] - 2)
    a = np.clip(fi - i0, 0, 1); b = np.clip(fj - j0, 0, 1)
    return (A[i0, j0] * (1 - a) + A[i0 + 1, j0] * a) * (1 - b) + (A[i0, j0 + 1] * (1 - a) + A[i0 + 1, j0 + 1] * a) * b


# 밭·길이 덮은 화면 칸 표시 (꼭짓점을 바닥에 투영해 격자에 찍고 한 칸 넓힘)
cover = np.zeros(HG.shape, bool)
for n in ('F_centuriatio', 'R_via_appia', 'R_via_ostiensis'):
    ob = bpy.data.objects.get(n)
    if not ob:
        continue
    P = U.eval_world_coords(ob, 1).copy(); P[:, 2] = 0
    uv = U.project_pts(P)
    i = np.clip(np.round((uv[:, 0] - G0) / GS).astype(int), 0, HG.shape[0] - 1)
    j = np.clip(np.round((uv[:, 1] - G0) / GS).astype(int), 0, HG.shape[1] - 1)
    cover[i, j] = True
for _ in range(2):
    c2 = cover.copy()
    c2[1:] |= cover[:-1]; c2[:-1] |= cover[1:]; c2[:, 1:] |= cover[:, :-1]; c2[:, :-1] |= cover[:, 1:]
    cover = c2

lo = U.pts_to_world(np.array([[0, 0], [1191, 0], [1191, 1684], [0, 1684]], float), 0.0)[:, :2]
SPC = 0.75
gx, gy = np.meshgrid(np.arange(lo[:, 0].min(), lo[:, 0].max(), SPC), np.arange(lo[:, 1].min(), lo[:, 1].max(), SPC), indexing='ij')
xy = np.stack([gx, gy], -1).reshape(-1, 2) + rng.uniform(-SPC / 2, SPC / 2, (gx.size, 2))
uv = U.project_pts(np.c_[xy, np.zeros(len(xy))])
u, v = uv[:, 0], uv[:, 1]
inside = (u > 3) & (u < 1188) & (v > 12) & (v < 1680)
xy, u, v = xy[inside], u[inside], v[inside]
h = samp(HG, u, v)
gi = np.clip(np.round((u - G0) / GS).astype(int), 0, HG.shape[0] - 1); gj = np.clip(np.round((v - G0) / GS).astype(int), 0, HG.shape[1] - 1)
keep = ~WET[gi, gj] & ~cover[gi, gj]
for b in FOOT:
    cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    rx, ry = (b[2] - b[0]) / 2 * 1.15 + 6, (b[3] - b[1]) / 2 * 1.15 + 6
    keep &= ((u - cx) / rx) ** 2 + ((v - cy) / ry) ** 2 > 1.0
inz = np.zeros(len(u), bool)
for z in ZONES:
    inz |= (u > z[0] - 4) & (u < z[2] + 4) & (v > z[1] - 4) & (v < z[3] + 4)
# 밀도: 언덕·경사·강둑일수록 높게, 평지는 드문드문, 글 자리는 아주 드물게
dh = np.hypot(samp(HG, u + 2.5, v) - h, samp(HG, u, v + 2.5) - h)
river_near = np.zeros(len(u), bool)
for di in (-4, -2, 2, 4):
    river_near |= D['river'][np.clip(gi + di, 0, HG.shape[0] - 1), gj] | D['river'][gi, np.clip(gj + di, 0, HG.shape[1] - 1)]
# 덤불은 무리 지어 자람: 낮은 주파수 잡음으로 군락(있는 곳/없는 곳)
patch = np.array([noise.noise(Vector((x * 0.11, y * 0.11, 3.7))) for x, y in xy])
patch = np.clip((patch + 0.22) * 1.9, 0, 1) ** 1.2
dens = (0.10 + 0.32 * np.clip(h / 2.0, 0, 1) + 0.40 * np.clip(dh * 6, 0, 1) + 0.45 * river_near) * patch
dens = np.where(v < 400, 0.06 * np.clip(dh * 8, 0, 1), dens)       # 산지: 가파른 곳에만 드문 바위
dens = np.where(inz, 0.01, dens)
keep &= rng.random(len(u)) < dens
xy, u, v, h = xy[keep], u[keep], v[keep], h[keep]
is_rock = (v < 400) | (rng.random(len(u)) < 0.12)


def blob(n_sub_lat, n_sub_lon):
    vs = []
    for i in range(n_sub_lat + 1):
        th = math.pi * i / n_sub_lat
        for j in range(n_sub_lon):
            ph = 2 * math.pi * j / n_sub_lon
            vs.append((math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th)))
    fs = []
    for i in range(n_sub_lat):
        for j in range(n_sub_lon):
            a = i * n_sub_lon + j; b = i * n_sub_lon + (j + 1) % n_sub_lon
            fs.append((a, b, b + n_sub_lon, a + n_sub_lon))
    return np.array(vs), np.array(fs)


BV, BF = blob(4, 6)
RV, RF = blob(2, 5)                               # 바위: 각진 면
V, F = [], []
nv = 0
for k in range(len(u)):
    x0, y0 = xy[k]
    if is_rock[k]:
        bv, bf = RV, RF
        s = rng.uniform(0.12, 0.3); sq = (s * rng.uniform(0.9, 1.5), s * rng.uniform(0.7, 1.1), s * rng.uniform(0.4, 0.7))
        z0 = h[k] - sq[2] * 0.3
    else:
        bv, bf = BV, BF
        s = rng.uniform(0.15, 0.32); sq = (s * rng.uniform(1.0, 1.5), s, s * rng.uniform(0.5, 0.7))
        z0 = h[k] + sq[2] * 0.45
    rot = rng.uniform(0, 2 * math.pi); c, sn = math.cos(rot), math.sin(rot)
    jit = 1 + 0.22 * np.array([noise.noise(Vector((p[0] * 2.3 + k, p[1] * 2.3, p[2] * 2.3))) for p in bv])
    P = bv * jit[:, None] * np.array(sq)
    P = np.c_[P[:, 0] * c - P[:, 1] * sn, P[:, 0] * sn + P[:, 1] * c, P[:, 2]] + np.array([x0, y0, z0])
    V.append(P); F.append(bf + nv); nv += len(P)
ob = U.mesh_from_arrays('S_scrub_rocks', np.concatenate(V), np.concatenate(F), U.coll('35_FIELDS_ROADS'))
for p in ob.data.polygons:
    p.use_smooth = False
ob['low_terrain'] = True
print('scrub/rocks', len(u), 'rocks', int(is_rock.sum()), 'tris', U.tri_count(ob))
