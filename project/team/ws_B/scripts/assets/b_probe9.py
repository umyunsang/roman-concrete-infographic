import bpy, numpy as np
U = bpy.data.texts['asset_utils.py'].as_module()
o = bpy.data.objects['C1_pozzolana_quarry']
print('PROBE C1 bbox', [round(x, 1) for x in U.screen_bbox(o, 1)], 'dims', [round(x, 2) for x in o.dimensions], 'loc', [round(x, 2) for x in o.location], 'rot', [round(x, 2) for x in o.rotation_euler])
P = U.eval_world_coords(o, 1); print('PROBE C1 world x', P[:, 0].min().round(2), P[:, 0].max().round(2), 'y', P[:, 1].min().round(2), P[:, 1].max().round(2), 'z', P[:, 2].min().round(2), P[:, 2].max().round(2))
for uv in [(760, 415), (830, 470), (690, 470)]:
    print('PROBE world at', uv, U.pts_to_world(np.array([uv], float), 0.0)[0].round(2), 'rise', round(float(U.rise_per_unit(np.array([uv], float))[0]), 2))
