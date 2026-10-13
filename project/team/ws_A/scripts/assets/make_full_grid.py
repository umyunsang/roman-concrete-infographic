"""(백그라운드 Blender) 땅 높이장 격자 + 원근 상승량 + 오브젝트 바닥 발자국 → assets/full_grid.npz, object_footprints.json
blender -b --factory-startup <파일> --python make_full_grid.py -- <격자 간격 pt>
"""
import json
import sys
import bpy
import numpy as np

STEP = float(sys.argv[sys.argv.index('--') + 1]) if '--' in sys.argv else 3.5
ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_A/'
U = bpy.data.texts['asset_utils.py'].as_module()
uu, vv = np.meshgrid(np.arange(-10.0, 1202.5 + 1e-6, STEP), np.arange(-10.0, 1702.5 + 1e-6, STEP), indexing='ij')
UV = np.stack([uu, vv], -1)
W = U.pts_to_world(UV, 0.0)
rise = U.rise_per_unit(UV)
np.savez_compressed(ROOT + 'assets/full_grid.npz', u=uu, v=vv, wx=W[..., 0], wy=W[..., 1], rise=rise)
foot = {}
for c in ('20_LANDMARK', '40_REGION'):
    col = bpy.data.collections.get(c)
    for ob in (col.objects if col else []):
        if ob.hide_render or ob.type != 'MESH' or ob.name.startswith('L05_aqua'):
            continue
        P = U.eval_world_coords(ob, 6).copy(); P[:, 2] = 0
        q = U.project_pts(P)
        foot[ob.name] = [round(float(np.percentile(q[:, 0], 1)), 1), round(float(np.percentile(q[:, 1], 1)), 1),
                         round(float(np.percentile(q[:, 0], 99)), 1), round(float(np.percentile(q[:, 1], 99)), 1)]
json.dump(foot, open(ROOT + 'assets/object_footprints.json', 'w'), indent=0)
print('GRID', uu.shape, 'STEP', STEP, 'FOOT', len(foot))
