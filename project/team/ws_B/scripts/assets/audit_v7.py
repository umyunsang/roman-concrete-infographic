"""v7 자동 감사: Figma 글 상자(loop/figma_texts.json) ↔ Blender 물체 화면 상자 겹침, 프레임 밖, 글끼리 겹침.
- 물체 단위: 20_LANDMARK·40_REGION·45_CORE_SCENES·60_TREES 오브젝트, 50_DETAIL_MODEL·85_HEADER는 빈 부모 묶음 단위
- 허용(의도된 겹침): 제목 글 ↔ 개선문
- 결과: loop/audit_rN.json + 표 출력
Blender에서: AUDIT_ROUND = N; exec(open(<이 파일>).read())
"""
import json
import bpy
import numpy as np

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_B/'
U = bpy.data.texts['asset_utils.py'].as_module()
T = json.load(open(ROOT + 'loop/figma_texts.json'))
PAD = 2.0
items = []
for cn in ('20_LANDMARK', '40_REGION', '45_CORE_SCENES', '60_TREES'):
    c = bpy.data.collections.get(cn)
    for o in (c.objects if c else []):
        if o.type == 'MESH' and not o.hide_render:
            items.append((o.name, cn, [o]))
for cn in ('50_DETAIL_MODEL', '85_HEADER'):
    c = bpy.data.collections.get(cn)
    for e in (c.objects if c else []):
        if e.type == 'EMPTY':
            ks = [o for o in c.objects if o.parent == e and o.type == 'MESH' and not o.hide_render]
            if ks:
                items.append((e.name, cn, ks))
boxes = {}
for name, cn, obs in items:
    step = 1 if sum(len(o.data.vertices) for o in obs) < 200000 else 4
    boxes[name] = (cn, U.screen_bbox(obs, step))


def ov(a, b, pad=0.0):
    return not (a[2] + pad <= b[0] or b[2] + pad <= a[0] or a[3] + pad <= b[1] or b[3] + pad <= a[1])


ALLOW = {('634:719', 'H_gate'), ('634:720', 'H_gate'), ('634:722', 'H_gate')}
hits = []
for t in T:
    for name, (cn, bb) in boxes.items():
        if (t['id'], name) in ALLOW:
            continue
        if ov(t['b'], bb, PAD):
            obs = [o for o in bpy.data.objects if o.name == name] or []
            if not obs or obs[0].type == 'EMPTY':
                obs = [o for o in bpy.data.objects if o.parent and o.parent.name == name and o.type == 'MESH']
            P = np.concatenate([U.eval_world_coords(o, 1) for o in obs])
            q = U.project_pts(P)
            x0, y0, x1, y1 = t['b']
            inside = int(((q[:, 0] > x0 - PAD) & (q[:, 0] < x1 + PAD) & (q[:, 1] > y0 - PAD) & (q[:, 1] < y1 + PAD)).sum())
            if inside == 0:
                continue
            # 겹친 넓이(pt²)
            w = min(t['b'][2], bb[2]) - max(t['b'][0], bb[0]); h = min(t['b'][3], bb[3]) - max(t['b'][1], bb[1])
            hits.append({'text': t['c'], 'kind': t['kind'], 'object': name, 'coll': cn, 'area': round(max(0, w) * max(0, h), 1), 'verts_in': inside})
outside = [n for n, (cn, bb) in boxes.items() if bb[0] < -2 or bb[1] < -2 or bb[2] > 1193 or bb[3] > 1686]
tt = []
for i, a in enumerate(T):
    for b in T[i + 1:]:
        if ov(a['b'], b['b'], 0) and not (a['kind'] == 'title' and b['kind'] == 'title'):
            tt.append((a['c'], b['c']))
# BUSY: 지명·라벨·SUPPORT·DETAIL·CORE 글 상자 안에 밭·길·물결·파도·점선 길 꼭짓점이 있으면 '배경 복잡'
busy = []
BG = [n for n in ('F_centuriatio', 'W_water_marks', 'S_core_path', 'B_pons') if bpy.data.objects.get(n)] + [o.name for o in bpy.data.objects if o.name.startswith('R_') and o.type == 'MESH']
BGQ = {n: U.project_pts(U.eval_world_coords(bpy.data.objects[n], 1)) for n in BG}
for t in T:
    if t['kind'] not in ('place', 'label', 'support', 'detail', 'core'):
        continue
    x0, y0, x1, y1 = t['b']
    for n, q in BGQ.items():
        k = int(((q[:, 0] > x0 - 2) & (q[:, 0] < x1 + 2) & (q[:, 1] > y0 - 2) & (q[:, 1] < y1 + 2)).sum())
        if k > 0 and not (t['id'] == 'CORE3' and n == 'S_core_path'):   # ③→④ 연결 점선은 설계(배지 사이)
            busy.append({'text': t['c'], 'bg': n, 'verts': k})
for b_ in busy:
    print('배경', b_['text'], '←', b_['bg'], b_['verts'])
print('글 배경 복잡', len(busy))
rnd = globals().get('AUDIT_ROUND', 0)
res = {'round': rnd, 'busy_backgrounds': busy, 'text_object_overlaps': hits, 'outside_frame': outside, 'text_text_overlaps': tt,
       'n_objects': len(boxes)}
json.dump(res, open(ROOT + 'loop/audit_r%d.json' % rnd, 'w'), ensure_ascii=False, indent=1)
for h in sorted(hits, key=lambda x: -x['area']):
    print('겹침', h['kind'], h['text'], '↔', h['object'], h['area'])
print('프레임 밖', outside)
print('글끼리', tt)
print('합계: 글↔물체', len(hits), '| 프레임 밖', len(outside), '| 글끼리', len(tt))
