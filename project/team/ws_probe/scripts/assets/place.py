"""오브젝트 배치 도구 (Blender 텍스트로 쓰지 않고 exec로 불러 씀).
- ground_origin(ob): 원점을 바닥 중심으로(메시 좌표 이동), 변환 적용
- fit_contain(ob, box, rotz=None, align='bottom'): 화면 상자 box(pt) 안에 '들어가게' 균일 축척(가로·세로 중 작은 쪽) + 이동
- in_frame(ob, safe=8): 화면 경계 상자가 프레임 안(여백 safe pt)인지
"""
import bpy
import math
import numpy as np
from mathutils import Matrix

U = bpy.data.texts['asset_utils.py'].as_module()


def ground_origin(ob):
    me = ob.data
    M = ob.matrix_world.copy()
    me.transform(M)
    ob.matrix_world = Matrix.Identity(4)
    co = np.empty(len(me.vertices) * 3)
    me.vertices.foreach_get('co', co)
    co = co.reshape(-1, 3)
    mn, mx = co.min(0), co.max(0)
    off = np.array([(mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2, mn[2]])
    co -= off
    me.vertices.foreach_set('co', co.ravel())
    me.update()
    ob.location = tuple(off)
    ob.rotation_mode = 'XYZ'


def fit_contain(ob, box, rotz=None, align='bottom', iters=4, step=1):
    if rotz is not None:
        ob.rotation_euler = (0, 0, math.radians(rotz))
    for _ in range(iters):
        bpy.context.view_layer.update()
        g = U.screen_bbox(ob, step)
        s = min((box[2] - box[0]) / max(1e-6, g[2] - g[0]), (box[3] - box[1]) / max(1e-6, g[3] - g[1]))
        ob.scale = ob.scale * s
        bpy.context.view_layer.update()
        g = U.screen_bbox(ob, step)
        du = (box[0] + box[2]) / 2 - (g[0] + g[2]) / 2
        dv = (box[3] - g[3]) if align == 'bottom' else ((box[1] + box[3]) / 2 - (g[1] + g[3]) / 2)
        cu, cv = (g[0] + g[2]) / 2, g[3]
        base = U.pt_to_world(cu, cv, 0)
        moved = U.pt_to_world(cu + du, cv + dv, 0)
        ob.location = ob.location + (moved - base)
    bpy.context.view_layer.update()
    return [round(x, 1) for x in U.screen_bbox(ob, step)]


def in_frame(ob, safe=8, step=1):
    g = U.screen_bbox(ob, step)
    return g[0] >= safe and g[1] >= safe and g[2] <= U.FRAME_W - safe and g[3] <= U.FRAME_H - safe
