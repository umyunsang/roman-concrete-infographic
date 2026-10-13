"""assets/mtn_hf.npz → L01_apennines (30_TERRAIN). 밑땅(T_land) 위에 산 높이를 얹은 2pt 격자, 산이 있는 칸만.
가장자리는 밑땅보다 살짝 아래로(이음매 안 보이게). Blender에서: exec(open(<이 파일>).read())
"""
import bpy
import numpy as np

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_B/'
U = bpy.data.texts['asset_utils.py'].as_module()
D = np.load(ROOT + 'assets/mtn_hf.npz')
uu, vv, H, B = D['u'], D['v'], D['h'].astype(np.float64), D['base'].astype(np.float64)
nu, nv = H.shape
W = U.pts_to_world(np.stack([uu, vv], -1).astype(np.float64), 0.0)
W[..., 2] = B + H - 0.04
idx = np.arange(nu * nv).reshape(nu, nv)
hmax = np.maximum.reduce([H[:-1, :-1], H[1:, :-1], H[:-1, 1:], H[1:, 1:]])
ci, cj = np.nonzero(hmax > 0.03)
a = idx[ci, cj]; b = idx[ci + 1, cj]; c = idx[ci + 1, cj + 1]; d = idx[ci, cj + 1]
faces = np.concatenate([np.stack([a, b, c], 1), np.stack([a, c, d], 1)])
used = np.unique(faces)
remap = -np.ones(nu * nv, dtype=np.int64); remap[used] = np.arange(len(used))
U.remove_obj('L01_apennines')
ob = U.mesh_from_arrays('L01_apennines', W.reshape(-1, 3)[used], remap[faces], U.coll('30_TERRAIN'))
for p in ob.data.polygons:
    p.use_smooth = False
ob['low_terrain'] = True
print('L01_apennines tris', len(faces), 'screen', [round(x, 1) for x in U.screen_bbox(ob, 3)])
