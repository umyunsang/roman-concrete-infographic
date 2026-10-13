import bpy, numpy as np
U = bpy.data.texts['asset_utils.py'].as_module()
o = bpy.data.objects['D2_lime_kiln']
P = U.eval_world_coords(o, 1); q = U.project_pts(P)
print('PROBE kiln z', P[:, 2].min().round(2), P[:, 2].max().round(2), 'users', o.data.users, 'verts', len(P))
for z0 in np.arange(0, P[:, 2].max(), 0.5):
    m = (P[:, 2] >= z0) & (P[:, 2] < z0 + 0.5)
    if m.any():
        print('PROBE z %.1f n %5d x %.1f..%.1f y %.1f..%.1f  screen u %.0f..%.0f v %.0f..%.0f' % (z0, m.sum(), P[m, 0].min(), P[m, 0].max(), P[m, 1].min(), P[m, 1].max(), q[m, 0].min(), q[m, 0].max(), q[m, 1].min(), q[m, 1].max()))
