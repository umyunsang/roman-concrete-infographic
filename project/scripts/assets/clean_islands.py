"""R6 오브젝트 정리
- 떨어진 작은 조각(전체 꼭짓점의 MIN_FRAC 미만 덩어리) 지우기: 봉우리 L01_*, Meshy 계열, 팔라티노 등
- 베수비오: 기울이면서 옆으로 튀어나온 가장자리 띠(지역 높이 하위 3%) 지우기
- DETAIL의 떠 있는 부분(누르는 화살표·열 줄·물방울)은 81_NOSHADOW로(그림자 없는 두 번째 패스에서 렌더)
Blender에서: exec(open(<이 파일>).read())
"""
import bpy
import bmesh
import numpy as np

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/'
U = bpy.data.texts['asset_utils.py'].as_module()
MIN_FRAC = 0.03


def drop_islands(ob, min_frac=MIN_FRAC):
    bm = bmesh.new(); bm.from_mesh(ob.data)
    # glTF로 들어온 메시는 평면 음영 때문에 면마다 꼭짓점이 따로 → 먼저 합쳐야 '덩어리'를 셀 수 있음
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bm.verts.ensure_lookup_table(); bm.verts.index_update()
    seen = set(); comps = []
    for v in bm.verts:
        if v.index in seen:
            continue
        stack = [v]; comp = []
        seen.add(v.index)
        while stack:
            x = stack.pop(); comp.append(x)
            for e in x.link_edges:
                y = e.other_vert(x)
                if y.index not in seen:
                    seen.add(y.index); stack.append(y)
        comps.append(comp)
    n = len(bm.verts)
    big = max(len(c) for c in comps) if comps else 0
    kill = [v for c in comps if len(c) < max(min_frac * n, 1) and len(c) < big for v in c]
    if kill:
        bmesh.ops.delete(bm, geom=kill, context='VERTS')
    bm.to_mesh(ob.data); bm.free(); ob.data.update()
    return len(comps), len(kill)


out = {}
# 작업 장면(C*)의 사람·도구는 원래 떨어진 덩어리라 건드리지 않음. 봉우리·팔라티노만.
# KEEP_LARGEST(R7): 봉우리는 가장 큰 덩어리만(frac 0.5), 콜로세움은 0.2% 미만 조각 제거
TARGETS = {n: 0.5 for n in [o.name for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith('L01_')]}
TARGETS['COL_ruined'] = 0.002
for n, frac in TARGETS.items():
    ob = bpy.data.objects[n]
    if ob.data.users > 1:
        continue
    out[n] = drop_islands(ob, frac)

RUN_VESUVIUS = globals().get('RUN_VESUVIUS', False)
if RUN_VESUVIUS:
    # 베수비오 가장자리 띠
    v = bpy.data.objects['L07_vesuvius']
    me = v.data
    co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    zcut = np.percentile(co[:, 2], 3.0)
    bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    kill = [bm.verts[i] for i in np.nonzero(co[:, 2] < zcut)[0]]
    bmesh.ops.delete(bm, geom=kill, context='VERTS'); bm.to_mesh(me); bm.free(); me.update()
    out['L07_vesuvius_skirt_removed'] = len(kill)
    out['L07_vesuvius_islands'] = drop_islands(v, 0.02)


# 떠 있는 DETAIL 부분 → 81_NOSHADOW
NS = U.coll('81_NOSHADOW')
moved = 0
for o in list(bpy.data.objects):
    if o.name.startswith(('D3_press', 'D2_heat', 'D4_drop')):
        mw = o.matrix_world.copy()
        for c in list(o.users_collection):
            c.objects.unlink(o)
        NS.objects.link(o)
        o.matrix_world = mw
        moved += 1
out['noshadow_moved'] = moved
for k, vv in out.items():
    print(k, vv)
