"""땅 메시 v2: assets/land_tri.npz(땅 다각형 삼각분할) + terrain_hf.npz(높이) → T_land.
해안·강둑은 다각형 그대로의 매끈한 선, 거기서 아래로 1.6 내려가는 벽(주름 없음).
Blender에서: exec(open(<이 파일>).read())
"""
import bpy
import bmesh
import numpy as np

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_B/'
U = bpy.data.texts['asset_utils.py'].as_module()
L = np.load(ROOT + 'assets/land_tri.npz')
uv, F = L['uv'], L['faces']
rings = [L['ring_flat'][L['ring_off'][k]:L['ring_off'][k + 1]] for k in range(len(L['ring_off']) - 1)]
D = np.load(ROOT + 'assets/terrain_hf.npz')
HG = D['h_base'].astype(np.float64) if 'h_base' in D.files else D['h'].astype(np.float64); G0u = float(D['u'][0, 0]); G0v = float(D['v'][0, 0]); GS = float(D['u'][1, 0] - D['u'][0, 0])
fi = (uv[:, 0] - G0u) / GS; fj = (uv[:, 1] - G0v) / GS
i0 = np.clip(np.floor(fi).astype(int), 0, HG.shape[0] - 2); j0 = np.clip(np.floor(fj).astype(int), 0, HG.shape[1] - 2)
a = np.clip(fi - i0, 0, 1); b = np.clip(fj - j0, 0, 1)
H = (HG[i0, j0] * (1 - a) + HG[i0 + 1, j0] * a) * (1 - b) + (HG[i0, j0 + 1] * (1 - a) + HG[i0 + 1, j0 + 1] * a) * b
H = np.maximum(H, 0.0)
# RANGE (워커 B · 비평 6): 산괴는 1pt 원격자(range_relief)에서 꼭짓점마다 다시 표본 × 같은 배수(rfac)
if 'rfac' in D.files:
    _RR = np.load(ROOT + 'assets/range_relief.npz'); _R = _RR['R'].astype(np.float64); _st = float(_RR['step'])
    _fi = (uv[:, 0] - float(_RR['u0'])) / _st; _fj = (uv[:, 1] - float(_RR['v0'])) / _st
    _inb = (_fi >= 0) & (_fi <= _R.shape[0] - 1) & (_fj >= 0) & (_fj <= _R.shape[1] - 1)
    _a0 = np.clip(np.floor(_fi).astype(int), 0, _R.shape[0] - 2); _b0 = np.clip(np.floor(_fj).astype(int), 0, _R.shape[1] - 2)
    _ta = np.clip(_fi - _a0, 0, 1); _tb_ = np.clip(_fj - _b0, 0, 1)
    _rv_ = (_R[_a0, _b0] * (1 - _ta) + _R[_a0 + 1, _b0] * _ta) * (1 - _tb_) + (_R[_a0, _b0 + 1] * (1 - _ta) + _R[_a0 + 1, _b0 + 1] * _ta) * _tb_
    _RF = D['rfac'].astype(np.float64)
    _fac = (_RF[i0, j0] * (1 - a) + _RF[i0 + 1, j0] * a) * (1 - b) + (_RF[i0, j0 + 1] * (1 - a) + _RF[i0 + 1, j0 + 1] * a) * b
    RNG_V = np.where(_inb, _rv_, 0.0) * _fac
    H = H + RNG_V
else:
    RNG_V = np.zeros(len(H))
# 둑·해안 8pt 안에서 높이를 0으로 부드럽게(격자 칸이 강·땅에 걸쳐 생기던 톱니 없앰)
_ts = np.clip(L['dist_sea'] / 16.0, 0, 1); _tr = np.clip(L['dist_riv'] / 8.0, 0, 1)   # R13 해안 16pt·강둑 8pt, 프레임 가장자리는 감쇠 없음
H = H * (_ts * _ts * (3 - 2 * _ts)) * (_tr * _tr * (3 - 2 * _tr))
# BEACH (워커 B · 비평 5): terrain_hf와 같은 비탈을 정확한 꼭짓점 거리로 — 해안·강둑 벽 윗단이 물에 잠기게


def _gi(name):
    G = D[name].astype(np.float64)
    return (G[i0, j0] * (1 - a) + G[i0 + 1, j0] * a) * (1 - b) + (G[i0, j0 + 1] * (1 - a) + G[i0 + 1, j0 + 1] * a) * b


if 'beach_w' in D.files:
    _bw = _gi('beach_w'); _kw = _gi('bank_w')
    _tb = np.clip(L['dist_sea'], 0, None) * (22.0 / np.maximum(_bw, 1e-3))
    def _sm(x):
        x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
    _dip_s = -0.2 * (1 - _sm((_tb + 1.0) / 4.0)) - 0.58 * (1 - _sm((_tb - 2.5) / 19.5))
    _ds = np.clip(L['dist_sea'] / 30.0, 0, 1); _wz = -0.4 - 0.3 * (1 - _ds * _ds * (3 - 2 * _ds))
    _tk = np.clip(L['dist_riv'], 0, None) * (9.0 / np.maximum(_kw, 1e-3))
    _dip_r = _wz * (0.35 * (1 - _sm((_tk + 0.5) / 2.5)) + 0.85 * (1 - _sm((_tk - 0.5) / 8.5)))
    H = H + np.minimum(_dip_s, _dip_r)
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
