import bpy, numpy as np, json
U = bpy.data.texts['asset_utils.py'].as_module()
def sil(n, step=1):
    o = bpy.data.objects[n]; P = U.eval_world_coords(o, step); q = U.project_pts(P)
    P0 = P.copy(); P0[:, 2] = 0; g = U.project_pts(P0)
    return q, g
qc, gc = sil('COL_ruined', 2)
for x in range(340, 600, 10):
    m = (qc[:, 0] >= x) & (qc[:, 0] < x + 10)
    mg = (gc[:, 0] >= x) & (gc[:, 0] < x + 10)
    print('PROBE COL x', x, 'sil top v', round(float(qc[m, 1].min()), 1) if m.any() else None, 'ground top v', round(float(gc[mg, 1].min()), 1) if mg.any() else None)
for n in ('L03_forum_vesta', 'L03_forum_temple'):
    q, g = sil(n, 1)
    print('PROBE', n, 'sil', [round(float(v), 1) for v in (q[:, 0].min(), q[:, 1].min(), q[:, 0].max(), q[:, 1].max())], 'ground', [round(float(v), 1) for v in (g[:, 0].min(), g[:, 1].min(), g[:, 0].max(), g[:, 1].max())])
