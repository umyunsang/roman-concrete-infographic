"""Figma 최종안(1191x1684pt) 좌표 <-> Blender 세계 좌표 변환 (정사영·원근 모두).

카메라 CAM_iso: 2026-10-07 14:05부터 **원근**(사용자 결정: 땅이 사다리꼴로 보이는 시야 영역).
rotation (54.7356°, 0, 45°), sensor_fit VERTICAL. 화면 pt는 카메라 프레임(view_frame) 안 비율로 정의.
- pt_to_world(u, v, h): 화면 (u, v)를 지나는 카메라 광선과 z=h 평면의 교점
- world_to_pt(p): 세계 점이 렌더에서 보이는 화면 pt
"""
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

FRAME_W, FRAME_H, PT = 1191.0, 1684.0, 0.1


def _frame():
    bpy.context.view_layer.update()
    cam = bpy.data.objects['CAM_iso']
    fr = [Vector(c) for c in cam.data.view_frame(scene=bpy.context.scene)]   # 오른위, 오른아래, 왼아래, 왼위 (카메라 지역 좌표)
    return cam, cam.matrix_world.copy(), fr


def pt_to_world(u, v, h=0.0):
    """Figma 프레임 좌표 (u, v)[pt]에 보이는, 높이 z=h 평면 위의 세계 점."""
    cam, M, (tr, br, bl, tl) = _frame()
    x, y = u / FRAME_W, v / FRAME_H
    p_loc = tl.lerp(tr, x).lerp(bl.lerp(br, x), y)
    p = M @ p_loc
    if cam.data.type == 'ORTHO':
        d = M.to_3x3() @ Vector((0, 0, -1))
    else:
        d = p - M.translation
    t = (h - p.z) / d.z
    return p + d * t


def world_to_pt(p):
    """세계 점이 렌더에서 보이는 Figma 프레임 좌표 (u, v)[pt]."""
    cam = bpy.data.objects['CAM_iso']
    c = world_to_camera_view(bpy.context.scene, cam, Vector(p))
    return c.x * FRAME_W, (1 - c.y) * FRAME_H
