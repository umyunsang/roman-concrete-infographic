import bpy, numpy as np, math
U = bpy.data.texts['asset_utils.py'].as_module()
o = bpy.data.objects['L07_vesuvius']
P = U.eval_world_coords(o, 1); q = U.project_pts(P)
top = P[P[:, 2] > np.percentile(P[:, 2], 97)]
cx, cy = top[:, 0].mean(), top[:, 1].mean()
r = np.hypot(P[:, 0] - cx, P[:, 1] - cy); ang = np.arctan2(P[:, 1] - cy, P[:, 0] - cx)
# debris region on screen: 925-990 x 1265-1360
m = (q[:, 0] > 925) & (q[:, 0] < 990) & (q[:, 1] > 1265) & (q[:, 1] < 1360)
print('PROBE n in debris box', m.sum(), 'z', P[m, 2].min().round(2), P[m, 2].max().round(2), 'r', r[m].min().round(2), r[m].max().round(2), 'ang', np.degrees(ang[m]).min().round(0), np.degrees(ang[m]).max().round(0))
for zb in np.arange(-3, 15, 1.5):
    mm = (P[:, 2] >= zb) & (P[:, 2] < zb + 1.5)
    if mm.any():
        print('PROBE z %.1f n %6d r p50 %.2f p95 %.2f p99.5 %.2f max %.2f' % (zb, mm.sum(), np.percentile(r[mm], 50), np.percentile(r[mm], 95), np.percentile(r[mm], 99.5), r[mm].max()))
