"""assets/terrain_hf.npz(맵 전체 높이장, 화면 pt 격자) → Blender 메시 T_land (30_TERRAIN).
바다·강 칸은 비우고, 열린 가장자리(해안·강둑)는 다각형 위로 맞춘 뒤 아래로 1.6 내려가는 벽을 붙인다.
Blender에서: exec(open(<이 파일>).read())
"""
import json
import bpy
import bmesh
import numpy as np

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_B/'
U = bpy.data.texts['asset_utils.py'].as_module()
D = np.load(ROOT + 'assets/terrain_hf.npz')
uu, vv, H, rin, sin_ = D['u'], D['v'], D['h'], D['river'], D['sea']
nu, nv = H.shape
W = U.pts_to_world(np.stack([uu, vv], -1).astype(np.float64), 0.0)
W[..., 2] = H
verts = W.reshape(-1, 3)
idx = np.arange(nu * nv).reshape(nu, nv)
wet = rin | sin_
cell_ok = ~(wet[:-1, :-1] | wet[1:, :-1] | wet[:-1, 1:] | wet[1:, 1:])
ci, cj = np.nonzero(cell_ok)
a = idx[ci, cj]; b = idx[ci + 1, cj]; c = idx[ci + 1, cj + 1]; d = idx[ci, cj + 1]
faces = np.concatenate([np.stack([a, b, c], 1), np.stack([a, c, d], 1)])
used = np.unique(faces)
remap = -np.ones(len(verts), dtype=np.int64)
remap[used] = np.arange(len(used))
U.remove_obj('T_land')
ob = U.mesh_from_arrays('T_land', verts[used], remap[faces], U.coll('30_TERRAIN'))
ob['low_terrain'] = True
P = json.load(open(ROOT + 'assets/terrain_polys.json'))
rings = [np.asarray(P['river'][0][0]), np.asarray(P['sea'][0][0])]
segA = np.concatenate([r[:-1] for r in rings]); segB = np.concatenate([r[1:] for r in rings])
bm = bmesh.new()
bm.from_mesh(ob.data)
edges = [e for e in bm.edges if e.is_boundary]
bverts = list({v for e in edges for v in e.verts})
co = np.array([(v.co.x, v.co.y, 0.0) for v in bverts])
UVb = U.project_pts(co)
dseg = segB - segA
L2 = (dseg ** 2).sum(1) + 1e-12
targets = []
for (u_, w_) in UVb:
    if u_ < -9 or u_ > 1201 or w_ < -9 or w_ > 1701:
        targets.append(None); continue
    t = np.clip(((u_ - segA[:, 0]) * dseg[:, 0] + (w_ - segA[:, 1]) * dseg[:, 1]) / L2, 0, 1)
    q = segA + t[:, None] * dseg
    dd = np.hypot(q[:, 0] - u_, q[:, 1] - w_)
    k = int(np.argmin(dd))
    targets.append(q[k] if dd[k] < 6.5 else None)   # R5 해안 톱니 없애기(격자 대각선 4.95보다 크게)
sel = [i for i, q in enumerate(targets) if q is not None]
if sel:
    Q = np.array([targets[i] for i in sel])
    XY = U.pts_to_world(Q, 0.0)
    for i, xy in zip(sel, XY):
        v = bverts[i]
        v.co.x, v.co.y, v.co.z = xy[0], xy[1], max(0.0, min(v.co.z, 0.15))
res = bmesh.ops.extrude_edge_only(bm, edges=edges)
for g in res['geom']:
    if isinstance(g, bmesh.types.BMVert):
        g.co.z = -1.6
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(ob.data)
bm.free()
for p in ob.data.polygons:
    p.use_smooth = False
print('T_land tris', U.tri_count(ob), 'snapped', len(sel))
