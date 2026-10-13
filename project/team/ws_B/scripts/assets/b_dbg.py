import bpy, json, os, numpy as np
U = bpy.data.texts['asset_utils.py'].as_module()
T = {t['id']: t for t in json.load(open('/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_B/loop/figma_texts.json'))}
for spec in os.environ.get('DBG', 'R_core_road_bed:CORE5').split(';'):
    on, tid = spec.split(':')
    o = bpy.data.objects[on]; P = U.eval_world_coords(o, 1); q = U.project_pts(P)
    b = T[tid]['b']
    m = (q[:, 0] > b[0] - 2) & (q[:, 0] < b[2] + 2) & (q[:, 1] > b[1] - 2) & (q[:, 1] < b[3] + 2)
    print('DBG', on, tid, b, 'n', int(m.sum()), np.round(q[m], 1).tolist()[:10], np.round(P[m], 2).tolist()[:4])
