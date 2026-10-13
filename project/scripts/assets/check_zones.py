"""글 자리 겹침 검사 + 물체 삼각형 수 검사.
Blender에서 exec(open(<이 파일>).read()) → 결과 표를 print 하고 assets/zone_check.json에 저장.
- sketch_v2/text_zones.json 의 zones(글 자리) 를 매번 다시 읽는다.
- 검사 대상: 렌더에 보이는 메시 오브젝트(20_LANDMARK, 40_REGION, 50_DETAIL_MODEL, 30_TERRAIN).
- low_terrain=True (땅판·바다·강·논밭·길 포장)는 '낮은 지형'으로 겹침 허용(높이 확인만).
- 물체의 화면 경계 상자 = 평가된 모든 꼭짓점을 카메라로 투영한 최소/최대 (pt).
"""
import bpy
import json
import numpy as np

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/'
U = bpy.data.texts['asset_utils.py'].as_module()
Z = json.load(open(ROOT + 'sketch_v2/text_zones.json'))
zones = Z['zones']
COLLS = ['20_LANDMARK', '30_TERRAIN', '40_REGION', '50_DETAIL_MODEL']
MIN_TRIS = 50000
LOW_MAX_Z = 0.5


def visible(ob):
    if ob.hide_render or ob.type != 'MESH':
        return False
    for c in ob.users_collection:
        if c.hide_render:
            return False
    return True


def overlap(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


rows = []
for cn in COLLS:
    c = bpy.data.collections.get(cn)
    if not c or c.hide_render:
        continue
    for ob in c.objects:
        if not visible(ob):
            continue
        n = len(ob.data.vertices)
        step = max(1, n // 400000)
        P = U.eval_world_coords(ob, step)
        uv = U.project_pts(P)
        bb = [float(uv[:, 0].min()), float(uv[:, 1].min()), float(uv[:, 0].max()), float(uv[:, 1].max())]
        low = bool(ob.get('low_terrain', False))
        hits = []
        if low:
            zmax = float(P[:, 2].max())
            if zmax > LOW_MAX_Z:
                # 낮은 지형인데 높은 곳이 있으면 글 자리 안 꼭짓점만 따로 확인
                for k, z in zones.items():
                    m = (uv[:, 0] > z[0]) & (uv[:, 0] < z[2]) & (uv[:, 1] > z[1]) & (uv[:, 1] < z[3])
                    if m.any() and P[m, 2].max() > LOW_MAX_Z:
                        hits.append(k + '(높음)')
        else:
            hits = [k for k, z in zones.items() if overlap(bb, z)]
        tris = U.tri_count(ob)
        rows.append({'object': ob.name, 'collection': cn, 'low_terrain': low,
                     'bbox': [round(x, 1) for x in bb], 'overlaps': hits, 'tris': tris,
                     'under_min': (not low) and tris < MIN_TRIS})

n_over = sum(1 for r in rows if r['overlaps'])
n_small = sum(1 for r in rows if r['under_min'])
total = sum(r['tris'] for r in rows)
res = {'zones_source': Z.get('source'), 'overlap_objects': n_over, 'under_50k_objects': n_small,
       'total_tris': total, 'rows': rows}
json.dump(res, open(ROOT + 'assets/zone_check.json', 'w'), ensure_ascii=False, indent=1)
for r in rows:
    flag = ('겹침:' + ','.join(r['overlaps'])) if r['overlaps'] else 'ok'
    print(f"{r['object']:<22} {r['tris']:>9,} {'낮은지형' if r['low_terrain'] else '물체':<5} {r['bbox']} {flag}{' <5만' if r['under_min'] else ''}")
print('겹침 물체', n_over, '| 5만 미만 물체', n_small, '| 전체 tris', f'{total:,}')
