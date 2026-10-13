import bpy, numpy as np
U = bpy.data.texts['asset_utils.py'].as_module()
P = U.eval_world_coords(bpy.data.objects['S_lab_island'], 1)
cx, cy = (P[:, 0].max() + P[:, 0].min()) / 2, (P[:, 1].max() + P[:, 1].min()) / 2
print('PROBE center', round(cx, 2), round(cy, 2), 'ext', np.ptp(P[:, 0]).round(2), np.ptp(P[:, 1]).round(2))
for z0 in np.arange(0, 3.0, 0.25):
    m = (P[:, 2] >= z0) & (P[:, 2] < z0 + 0.25)
    if m.any():
        a = (P[m, 0] - cx + P[m, 1] - cy) / 1.414; b = (P[m, 0] - cx - (P[m, 1] - cy)) / 1.414
        print('PROBE z %.2f n %4d along(1,1) %.2f..%.2f across %.2f..%.2f' % (z0, m.sum(), a.min(), a.max(), b.min(), b.max()))
