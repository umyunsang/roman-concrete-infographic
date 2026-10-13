import bpy, numpy as np
U = bpy.data.texts['asset_utils.py'].as_module()
o = bpy.data.objects['L03_forum_vesta']
P = U.eval_world_coords(o, 1)
cx, cy = np.median(P[:, 0]), np.median(P[:, 1])
print('PROBE users', o.data.users, 'n', len(P), 'z', P[:, 2].min().round(2), P[:, 2].max().round(2), 'c', round(cx, 2), round(cy, 2))
for z0 in np.arange(0, P[:, 2].max(), 0.25):
    m = (P[:, 2] >= z0) & (P[:, 2] < z0 + 0.25)
    if m.any():
        r = np.hypot(P[m, 0] - cx, P[m, 1] - cy)
        print('PROBE z %.2f n %4d r max %.2f p50 %.2f' % (z0, m.sum(), r.max(), np.median(r)))
