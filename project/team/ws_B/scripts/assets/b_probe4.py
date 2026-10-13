import bpy, numpy as np
U = bpy.data.texts['asset_utils.py'].as_module()
o = bpy.data.objects['F_villa_walls']
q = U.project_pts(U.eval_world_coords(o, 1))
# 동마다 꼭짓점 8개 × 4동 = 32개 / 채
n = len(q) // 32
for k in range(n):
    b = q[k * 32:(k + 1) * 32]
    print('VILLA', k, [round(x, 1) for x in (b[:, 0].min(), b[:, 1].min(), b[:, 0].max(), b[:, 1].max())])
