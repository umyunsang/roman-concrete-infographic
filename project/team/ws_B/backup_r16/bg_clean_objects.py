"""(백그라운드 Blender) Meshy 계열 SUPPORT·DETAIL 오브젝트 표면 정리 (14:47 사용자: "삼각형 때문에 보기 힘든 부분 수정")
원인: Meshy 메시는 조각난(비다양체) 덩어리라, 줄이면서 면 방향이 뒤섞임(폼페이 마을 32% 뒤집힘) → Workbench에서 검은 얼룩.
처리: 복셀 재구성(물샐틈없는 겉면, 방향 일관) → 목표 수로 줄이기 → 거의 평평한 면 합치기 → 평면 음영.
blender -b --factory-startup <파일> --python bg_clean_objects.py
"""
import math
import bpy

JOBS = {   # 이름: (복셀 크기 = 최대 치수 비율, 목표 삼각형)
    'L08_pompeii':          (0.010, 14000),
    'L08_pompeii_site':     (0.0065, 16000),   # 비계 기둥이 가늘어 더 촘촘히
    'L11_privernum_wall':   (0.009, 12000),
    'L09_portus_lighthouse': (0.008, 10000),
    'L09_portus_mole':      (0.009, 9000),
    'L12_harbor_pilae':     (0.009, 9000),
    'D2_lime_kiln':         (0.010, 9000),
    'S_lab_island':         (0.009, 10000),
    'L04_palatine':         (0.009, 14000),
    'L03_forum_temple':     (0.008, 12000),
}


def apply(ob, m):
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
        bpy.ops.object.modifier_apply(modifier=m.name)


def ntri(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


for n, (vr, tgt) in JOBS.items():
    ob = bpy.data.objects.get(n)
    if not ob:
        print('MISSING', n); continue
    for m in list(ob.modifiers):
        ob.modifiers.remove(m)
    co = [v.co for v in ob.data.vertices]
    dim = max(max(c[i] for c in co) - min(c[i] for c in co) for i in range(3))
    n0 = ntri(ob)
    m = ob.modifiers.new('rm', 'REMESH'); m.mode = 'VOXEL'; m.voxel_size = dim * vr; m.use_smooth_shade = False
    apply(ob, m)
    n1 = ntri(ob)
    if n1 > tgt:
        m = ob.modifiers.new('dec', 'DECIMATE'); m.decimate_type = 'COLLAPSE'; m.ratio = tgt / n1; apply(ob, m)
    m = ob.modifiers.new('pl', 'DECIMATE'); m.decimate_type = 'DISSOLVE'; m.angle_limit = math.radians(3.5); apply(ob, m)
    for p in ob.data.polygons:
        p.use_smooth = False
    print('CLEAN', n, n0, '-> remesh', n1, '->', ntri(ob))
for coll in (bpy.data.meshes,):
    for d in list(coll):
        if d.users == 0:
            coll.remove(d)
for scr in bpy.data.screens:
    for area in scr.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_perspective = 'CAMERA'
bpy.ops.wm.save_mainfile()
print('SAVED')
