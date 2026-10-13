"""백그라운드 Blender로 장면 최적화 (GUI Blender가 무거운 작업 중 강제종료되므로).
blender -b --factory-startup <roman_concrete_map.blend> --python bg_optimize.py
1) 쓰지 않는 것 삭제(옛 콜로세움·안쪽 사발·프록시·기준점·옛 수도교·임시 보관) 2) 무거운 오브젝트 단순화(오브젝트당 5만↑ 유지)
3) 강 수면 격자 성기게 4) 고아 데이터 정리 5) 3D 뷰를 카메라 시점으로 저장
"""
import bpy

removed = []
for cn in ('25_COL_INNER', '10_PROXY', '00_REF', '90_STAGING'):
    c = bpy.data.collections.get(cn)
    if not c:
        continue
    for o in list(c.objects):
        removed.append(o.name); bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.collections.remove(c)
for n in ('COL_colosseum', 'L05_aqueduct', 'T_ground', 'L01_apennines'):
    o = bpy.data.objects.get(n)
    if o:
        removed.append(n); bpy.data.objects.remove(o, do_unlink=True)
print('REMOVED', len(removed))

TARGET = {
    'COL_ruined': 320000, 'L07_vesuvius': 80000, 'L03_forum_vesta': 70000, 'L04_palatine': 70000,
    'L09_portus_lighthouse': 60000, 'L03_forum_temple': 60000, 'L08_pompeii_site': 70000, 'L08_pompeii': 70000,
    'L11_privernum_wall': 60000, 'L09_portus_mole': 55000, 'D2_lime_kiln': 55000, 'L12_harbor_pilae': 55000, 'S_lab_island': 55000,
}
dg = bpy.context.evaluated_depsgraph_get()
for n, tgt in TARGET.items():
    ob = bpy.data.objects.get(n)
    if not ob:
        print('MISSING', n); continue
    n0 = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    if n0 <= tgt * 1.05:
        print('KEEP', n, n0); continue
    m = ob.modifiers.new('dec', 'DECIMATE'); m.decimate_type = 'COLLAPSE'; m.ratio = tgt / n0; m.use_collapse_triangulate = True
    while ob.modifiers.find('dec') > 0:
        ob.modifiers.move(ob.modifiers.find('dec'), ob.modifiers.find('dec') - 1)
    bpy.context.view_layer.objects.active = ob
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
        bpy.ops.object.modifier_apply(modifier='dec')
    for p in ob.data.polygons:
        p.use_smooth = False
    print('DEC', n, n0, '->', sum(len(p.vertices) - 2 for p in ob.data.polygons))

# 강 수면: 1.0pt 격자(17만) → 다음 terrain.py 실행 때 2.0pt로 (여기선 데시메이트로 바로 줄임)
ob = bpy.data.objects.get('L02_tiber')
if ob:
    n0 = len(ob.data.polygons)
    m = ob.modifiers.new('dec', 'DECIMATE'); m.decimate_type = 'COLLAPSE'; m.ratio = 0.3
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
        bpy.ops.object.modifier_apply(modifier='dec')
    print('DEC L02_tiber', n0, '->', len(ob.data.polygons))

for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.textures):
    for d in list(coll):
        if d.users == 0:
            coll.remove(d)

# 3D 뷰: 카메라 시점(파일에 화면 배치가 같이 저장됨)
for scr in bpy.data.screens:
    for area in scr.areas:
        if area.type == 'VIEW_3D':
            sp = area.spaces.active
            sp.region_3d.view_perspective = 'CAMERA'
tot = 0
for ob in bpy.data.objects:
    if ob.type == 'MESH' and not ob.hide_render:
        tot += sum(len(p.vertices) - 2 for p in ob.data.polygons)
print('TOTAL_VISIBLE_BASE_TRIS', tot)
bpy.ops.wm.save_mainfile()
print('SAVED')
