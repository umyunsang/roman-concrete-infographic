"""assets/apennines_hf.npz(높이장, 화면 pt 격자) → Blender 메시 L01_apennines (30_TERRAIN).
Blender에서: exec(open(<이 파일>).read()).
위 띠(v < 662.5)의 땅 전체를 이 메시가 맡는다(T_ground는 그 아래만) → 산 기슭에 경계선이 생기지 않음.
강 칸은 비우고, 모든 열린 가장자리(강둑·재단 끝)에 아래로 1.6 내려가는 벽을 붙인다.
"""
import bpy
import bmesh
import numpy as np

U = bpy.data.texts['asset_utils.py'].as_module()
D = np.load('/Users/um-yunsang/Documents/로마콘크리트_3D/assets/apennines_hf.npz')
uu, vv, H, rin = D['u'], D['v'], D['h'], D['river']
nu, nv = H.shape
W = U.pts_to_world(np.stack([uu, vv], -1).astype(np.float64), 0.0)
W[..., 2] = H
verts = W.reshape(-1, 3)
idx = np.arange(nu * nv).reshape(nu, nv)
cell_ok = ~(rin[:-1, :-1] | rin[1:, :-1] | rin[:-1, 1:] | rin[1:, 1:])
ci, cj = np.nonzero(cell_ok)
a = idx[ci, cj]; b = idx[ci + 1, cj]; c = idx[ci + 1, cj + 1]; d = idx[ci, cj + 1]
faces = np.concatenate([np.stack([a, b, c], 1), np.stack([a, c, d], 1)])
used = np.unique(faces)
remap = -np.ones(len(verts), dtype=np.int64)
remap[used] = np.arange(len(used))
ob = U.mesh_from_arrays('L01_apennines', verts[used], remap[faces], U.coll('30_TERRAIN'))
ob['low_terrain'] = True
bm = bmesh.new()
bm.from_mesh(ob.data)
edges = [e for e in bm.edges if e.is_boundary]
# 강둑 꼭짓점을 강 다각형 위로 옮겨 계단(격자) 모양을 없앰
import json
RING = np.asarray(json.load(open('/Users/um-yunsang/Documents/로마콘크리트_3D/assets/terrain_polys.json'))['river'][0][0])
A_, B_ = RING[:-1], RING[1:]
bverts = list({v for e in edges for v in e.verts})
UVb = U.project_pts(np.array([(v.co.x, v.co.y, 0.0) for v in bverts]))
for v, (u_, w_) in zip(bverts, UVb):
    if u_ < -9 or u_ > 1201 or w_ < -9 or w_ > 662:
        continue          # 재단 끝·이음매 가장자리는 그대로
    d = B_ - A_
    t = np.clip(((u_ - A_[:, 0]) * d[:, 0] + (w_ - A_[:, 1]) * d[:, 1]) / ((d ** 2).sum(1) + 1e-12), 0, 1)
    q = A_ + t[:, None] * d
    k = np.argmin(np.hypot(q[:, 0] - u_, q[:, 1] - w_))
    if np.hypot(q[k, 0] - u_, q[k, 1] - w_) > 4.5:
        continue
    xy = U.pts_to_world(q[k][None, :], 0.0)[0]
    v.co.x, v.co.y, v.co.z = xy[0], xy[1], 0.0
res = bmesh.ops.extrude_edge_only(bm, edges=edges)
newv = [g for g in res['geom'] if isinstance(g, bmesh.types.BMVert)]
for v in newv:
    v.co.z = -1.6
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(ob.data)
bm.free()
for p in ob.data.polygons:
    p.use_smooth = False
print('L01_apennines tris', len(faces))
