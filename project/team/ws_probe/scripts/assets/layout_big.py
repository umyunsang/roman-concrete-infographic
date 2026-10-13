"""15:41 사용자: DETAIL 모형·CORE 작업 장면을 '글 자리만큼' 크게(≈150×90pt) 글 바로 옆에.
글 상자(Figma): CORE① 528–668×386–474, ② 70–215×756–844, ③ 409–559×1036–1124, ④ 639–816×1036–1124, ⑤ 991–1141×816–904
DETAIL 글: ① 36–170×412–460, ② 36–161×1036–1083, ③ 250–392×1344–1408, ④(옮김) 650–804×1305–1352
Blender에서: exec(open(<이 파일>).read())
"""
import bpy
ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_probe/'
exec(open(ROOT + 'scripts/assets/place.py').read())
SCENES = {
    'C1_pozzolana_quarry': (680, 384, 832, 478),     # CORE ① 오른쪽
    'C2_hot_mixing':       (66, 852, 222, 948),      # CORE ② 아래
    'C3_arch_building':    (422, 1132, 578, 1226),   # CORE ③ 아래
    'C4_crack_repair':     (636, 1132, 818, 1226),   # CORE ④ 아래
    'C5_researchers':      (988, 716, 1146, 810),    # CORE ⑤ 위
}
res = {}
for n, box in SCENES.items():
    ob = bpy.data.objects[n]
    res[n] = fit_contain(ob, box, align='bottom', step=1)
# DETAIL 묶음(빈 부모) — detail_models.py의 fit_group 사용
DM = {'D1_material': (70, 332, 164, 406), 'D2_making': (28, 950, 172, 1030), 'D3_structure': (246, 1188, 334, 1338),
      'D4_crack': (640, 1232, 820, 1300)}


def kids(e):
    return [o for o in bpy.data.collections['50_DETAIL_MODEL'].objects if o.parent == e and o.type == 'MESH']


def fit_group(e, want, iters=5):
    for _ in range(iters):
        bpy.context.view_layer.update()
        g = U.screen_bbox(kids(e), 1)
        s = min((want[2] - want[0]) / (g[2] - g[0]), (want[3] - want[1]) / (g[3] - g[1]))
        e.scale = e.scale * s
        bpy.context.view_layer.update()
        g = U.screen_bbox(kids(e), 1)
        du = (want[0] + want[2]) / 2 - (g[0] + g[2]) / 2; dv = want[3] - g[3]
        base = U.pt_to_world((g[0] + g[2]) / 2, g[3], 0); mv = U.pt_to_world((g[0] + g[2]) / 2 + du, g[3] + dv, 0)
        e.location = e.location + (mv - base)
    bpy.context.view_layer.update()
    return [round(x, 1) for x in U.screen_bbox(kids(e), 1)]


for n, box in DM.items():
    res[n] = fit_group(bpy.data.objects[n], box)
for k, v in res.items():
    print(k, v)
