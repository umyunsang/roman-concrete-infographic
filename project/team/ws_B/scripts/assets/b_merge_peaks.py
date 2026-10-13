"""워커 B · 비평 6 (산맥): 봉우리(L01_*)와 땅(T_land)이 다른 물체라 Workbench 윤곽선이 봉우리 밑동에 '잘린 선'을 그려
'담요 위에 얹은 바위'처럼 보임 → 봉우리 메시를 줄여(약 7천 삼각형) T_land 한 물체에 합치고 부드러운 음영, 원래 L01_*는 렌더에서 숨김
(자리·모양 그대로, 감사는 b_audit_extra가 숨긴 L01_*로 계속 검사). terrain_mesh2.py 뒤에 실행. 한 번만(T_land['b_peaks_merged'])."""
import bpy
import bmesh
U = bpy.data.texts['asset_utils.py'].as_module()
land = bpy.data.objects['T_land']
TARGET = 7000
if not land.get('b_peaks_merged'):
    bm = bmesh.new(); bm.from_mesh(land.data)
    n0 = len(bm.faces)
    Mi = land.matrix_world.inverted()
    deps = bpy.context.evaluated_depsgraph_get()
    added = 0
    for o in sorted([o for o in bpy.data.objects if o.name.startswith('L01_') and o.type == 'MESH'], key=lambda o: o.name):
        o.hide_render = False
        nt = len(o.data.polygons) * 2
        m = o.modifiers.new('b_dec', 'DECIMATE'); m.ratio = min(1.0, TARGET / max(1, nt))
        bpy.context.view_layer.update(); deps = bpy.context.evaluated_depsgraph_get()
        ev = o.evaluated_get(deps); me = ev.to_mesh()
        tmp = me.copy(); ev.to_mesh_clear()
        o.modifiers.remove(m)
        tmp.transform(Mi @ o.matrix_world)
        bm.from_mesh(tmp)
        added += len(tmp.polygons)
        bpy.data.meshes.remove(tmp)
        o.hide_render = True
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(land.data); bm.free(); land.data.update()
    land['b_peaks_merged'] = True
    print('peaks merged into T_land: faces', n0, '+', added, '→ tris', U.tri_count(land))
else:
    print('peaks already merged')
