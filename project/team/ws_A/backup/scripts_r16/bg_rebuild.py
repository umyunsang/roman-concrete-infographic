"""(백그라운드 Blender) 땅·수도교·밭/길/나무 다시 만들고, 오브젝트 단순화(5만 기준 폐기 후 목표), 정리 후 저장.
blender -b --factory-startup <파일> --python bg_rebuild.py
먼저: make_full_grid.py(백그라운드) → terrain_polys.py → terrain_hf.py(시스템 python3)
"""
import bpy

S = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_A/scripts/assets/'
for n in ('S_scrub_rocks',):
    o = bpy.data.objects.get(n)
    if o:
        bpy.data.objects.remove(o, do_unlink=True)
for f in ('terrain_mesh.py', 'aqueduct.py', 'fill_plains.py'):
    exec(compile(open(S + f).read(), f, 'exec'), {'__name__': '__main__'})
    print('RAN', f)

TARGET = {   # 포스터에서 보이는 크기에 맞춘 목표 (14:44 사용자: 5만 기준 폐기)
    'COL_ruined': 200000, 'L07_vesuvius': 30000, 'L03_forum_vesta': 40000, 'L04_palatine': 35000,
    'L09_portus_lighthouse': 25000, 'L03_forum_temple': 25000, 'L08_pompeii_site': 35000, 'L08_pompeii': 35000,
    'L11_privernum_wall': 25000, 'L09_portus_mole': 20000, 'D2_lime_kiln': 20000, 'L12_harbor_pilae': 20000, 'S_lab_island': 20000,
}
for n, tgt in TARGET.items():
    ob = bpy.data.objects.get(n)
    if not ob:
        print('MISSING', n); continue
    for _ in range(2):
        n0 = sum(len(p.vertices) - 2 for p in ob.data.polygons)
        if n0 <= tgt * 1.1:
            break
        m = ob.modifiers.new('dec', 'DECIMATE'); m.decimate_type = 'COLLAPSE'; m.ratio = tgt / n0; m.use_collapse_triangulate = True
        while ob.modifiers.find('dec') > 0:
            ob.modifiers.move(ob.modifiers.find('dec'), ob.modifiers.find('dec') - 1)
        with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
            bpy.ops.object.modifier_apply(modifier='dec')
    for p in ob.data.polygons:
        p.use_smooth = False
    print('DEC', n, '->', sum(len(p.vertices) - 2 for p in ob.data.polygons))
for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.textures):
    for d in list(coll):
        if d.users == 0:
            coll.remove(d)
for scr in bpy.data.screens:
    for area in scr.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_perspective = 'CAMERA'
tot = 0; rows = []
dg = bpy.context.evaluated_depsgraph_get()
for ob in bpy.data.objects:
    if ob.type == 'MESH' and not ob.hide_render and all(not c.hide_render for c in ob.users_collection):
        n = sum(len(p.vertices) - 2 for p in ob.data.polygons); tot += n; rows.append((n, ob.name))
rows.sort(reverse=True)
print('TOP', rows[:8])
print('TOTAL_VISIBLE_BASE_TRIS', tot)
bpy.ops.wm.save_mainfile()
print('SAVED')
