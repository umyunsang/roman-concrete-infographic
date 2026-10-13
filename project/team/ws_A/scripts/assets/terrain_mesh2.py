"""땅 메시 v2: assets/land_tri.npz(땅 다각형 삼각분할) + terrain_hf.npz(높이) → T_land.
해안·강둑은 다각형 그대로의 매끈한 선, 거기서 아래로 1.6 내려가는 벽(주름 없음).
Blender에서: exec(open(<이 파일>).read())
"""
import bpy
import bmesh
import numpy as np

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_A/'
U = bpy.data.texts['asset_utils.py'].as_module()
L = np.load(ROOT + 'assets/land_tri.npz')
uv, F = L['uv'], L['faces']
rings = [L['ring_flat'][L['ring_off'][k]:L['ring_off'][k + 1]] for k in range(len(L['ring_off']) - 1)]
D = np.load(ROOT + 'assets/terrain_hf.npz')
HG = (D['h_rel'] if 'h_rel' in D.files else D['h']).astype(np.float64); G0u = float(D['u'][0, 0]); G0v = float(D['v'][0, 0]); GS = float(D['u'][1, 0] - D['u'][0, 0])
fi = (uv[:, 0] - G0u) / GS; fj = (uv[:, 1] - G0v) / GS
i0 = np.clip(np.floor(fi).astype(int), 0, HG.shape[0] - 2); j0 = np.clip(np.floor(fj).astype(int), 0, HG.shape[1] - 2)
a = np.clip(fi - i0, 0, 1); b = np.clip(fj - j0, 0, 1)
H = (HG[i0, j0] * (1 - a) + HG[i0 + 1, j0] * a) * (1 - b) + (HG[i0, j0 + 1] * (1 - a) + HG[i0 + 1, j0 + 1] * a) * b
H = np.maximum(H, 0.0)
# 둑·해안 8pt 안에서 높이를 0으로 부드럽게(격자 칸이 강·땅에 걸쳐 생기던 톱니 없앰)
_ts = np.clip(L['dist_sea'] / 16.0, 0, 1); _tr = np.clip(L['dist_riv'] / 8.0, 0, 1)   # R13 해안 16pt·강둑 8pt, 프레임 가장자리는 감쇠 없음
H = H * (_ts * _ts * (3 - 2 * _ts)) * (_tr * _tr * (3 - 2 * _tr))
# 워커 A(비평 5): 모래사장·강둑 비탈 — 경계 고리는 수면 아래(-0.95/-0.55)라 땅 옆벽이 물속에 숨음, 물가선은 비탈과 수면이 만나는 곳
import json as _jj
def _sm(x):
    x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
_FPc = [b for k, b in _jj.load(open(ROOT + 'assets/object_footprints.json')).items() if k in ('L12_harbor_pilae', 'L08_pompeii', 'L08_pompeii_site', 'L07_vesuvius', 'L09_portus_mole', 'L09_portus_lighthouse')]
_Mco = np.zeros(len(uv))
for b in _FPc:
    cx_, cy_ = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2; rx_, ry_ = (b[2] - b[0]) / 2 + 4, (b[3] - b[1]) / 2 + 4
    e_ = np.sqrt(((uv[:, 0] - cx_) / rx_) ** 2 + ((uv[:, 1] - cy_) / ry_) ** 2)
    _Mco = np.maximum(_Mco, 1 - _sm((e_ - 1.0) / 0.25))
_ds = L['dist_sea']; _dr = L['dist_riv']
_frame_edge = (uv[:, 0] < -6) | (uv[:, 0] > 1197) | (uv[:, 1] > 1690)
DIP = -0.95 * (1 - _sm((_ds + 26.0 * _Mco) / 26.0)) - 0.85 * (1 - _sm(_dr / 9.0))
H = H + np.where(_frame_edge & (_ds > 3), 0.0, DIP)
# 워커 A: 물가 비탈 다듬기 — 높이장 이중선형 보간의 격자선 주름(세로 줄무늬)을 이웃 평균으로 펴 줌(물가 40pt·강 16pt 띠만, 경계 고리 고정)
_E = np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]).astype(np.int64)
_E = np.concatenate([_E, _E[:, ::-1]])
_w = np.clip(np.maximum(1 - _ds / 40.0, 1 - _dr / 16.0), 0, 1)
_w[np.concatenate(rings).astype(np.int64)] = 0.0
for _ in range(8):
    _sum = np.zeros(len(H)); _cnt = np.zeros(len(H))
    np.add.at(_sum, _E[:, 0], H[_E[:, 1]]); np.add.at(_cnt, _E[:, 0], 1.0)
    H = H + 0.6 * _w * (_sum / np.maximum(_cnt, 1) - H)
# ARENA_SINK(R9): 콜로세움 벽 안쪽 땅을 낮춤 — 땅(z 0)이 경기장 바닥(z -0.2)을 뚫고 나와 생기던 선 없앰
import json as _j
_F = _j.load(open(ROOT + 'assets/object_footprints.json')).get('COL_ruined')
if _F:
    _cx, _cy = (_F[0] + _F[2]) / 2, (_F[1] + _F[3]) / 2; _ax, _ay = (_F[2] - _F[0]) / 2 * 0.86, (_F[3] - _F[1]) / 2 * 0.86
    _e = ((uv[:, 0] - _cx) / _ax) ** 2 + ((uv[:, 1] - _cy) / _ay) ** 2
    H = np.where(_e < 1.0, np.minimum(H, -1.0), H)
W = U.pts_to_world(uv.astype(np.float64), 0.0)
W[:, 2] = H
U.remove_obj('T_land')
ob = U.mesh_from_arrays('T_land', W, F.astype(np.int64), U.coll('30_TERRAIN'))
bm = bmesh.new(); bm.from_mesh(ob.data)
bm.verts.ensure_lookup_table()
tops_all = [[bm.verts[int(k)] for k in ring] for ring in rings]   # 새 꼭짓점을 만들기 전에 미리 잡아 둠
# 경계 고리 → 아래로 벽
for tops in tops_all:
    low = [bm.verts.new((v.co.x, v.co.y, -1.6)) for v in tops]
    n = len(tops)
    for i in range(n):
        a1, b1 = tops[i], tops[(i + 1) % n]
        try:
            bm.faces.new((a1, b1, low[(i + 1) % n], low[i]))
        except ValueError:
            pass
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(ob.data); bm.free()
for p in ob.data.polygons:
    p.use_smooth = True     # R6 땅은 부드러운 음영(삼각형 면이 톱니처럼 보이던 것 없앰)
ob['low_terrain'] = True
print('T_land v2 tris', U.tri_count(ob))
