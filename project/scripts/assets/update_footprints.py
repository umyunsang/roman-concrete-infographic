"""오브젝트 바닥 발자국(화면 pt 상자) 다시 계산 → assets/object_footprints.json
대상 컬렉션: 20_LANDMARK, 40_REGION, 45_CORE_SCENES, 50_DETAIL_MODEL (수도교는 제외 — 길게 뻗어 땅을 다 눌러 버림)
Blender에서: exec(open(<이 파일>).read())
"""
import json
import bpy
import numpy as np

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/'
U = bpy.data.texts['asset_utils.py'].as_module()
foot = {}
for cn in ('20_LANDMARK', '40_REGION', '45_CORE_SCENES', '50_DETAIL_MODEL'):
    c = bpy.data.collections.get(cn)
    if not c or c.hide_render:
        continue
    for ob in c.objects:
        if ob.hide_render or ob.type != 'MESH' or ob.name.startswith('L05_aqua'):
            continue
        P = U.eval_world_coords(ob, 4).copy(); P[:, 2] = 0
        q = U.project_pts(P)
        foot[ob.name] = [round(float(np.percentile(q[:, 0], 1)), 1), round(float(np.percentile(q[:, 1], 1)), 1),
                         round(float(np.percentile(q[:, 0], 99)), 1), round(float(np.percentile(q[:, 1], 99)), 1)]
json.dump(foot, open(ROOT + 'assets/object_footprints.json', 'w'), indent=0)
print('footprints', len(foot))
