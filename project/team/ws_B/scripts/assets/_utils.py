"""월드맵 에셋 공용 도구 (Blender 텍스트 블록 'asset_utils.py'로도 들어감).

- coll(name): 컬렉션 얻기/만들기
- finalize_import(root_name, new_name): 가져온 Sketchfab 계층을 메시 하나로 합치고 재질 제거, 90_STAGING(x=+800)으로
- mesh_from_arrays(name, verts, faces, coll): numpy/list로 메시 만들기
- tri_count(ob): 평가된 메시 삼각형 수(모디파이어 포함)
- screen_bbox(ob): 렌더 화면 경계 상자 (pt) — 평가된 꼭짓점 전부를 numpy로 투영
- place_bbox(ob, bbox, h=0): 화면 상자 (x0,y0,x1,y1)에 맞게 축척·이동(바닥 중심 = 상자 아래쪽 근처)
"""
import bpy
import bmesh
import numpy as np
from mathutils import Vector, Matrix

A = bpy.data.texts['anchors.py'].as_module()
pt_to_world, world_to_pt, PT = A.pt_to_world, A.world_to_pt, A.PT
FRAME_W, FRAME_H = A.FRAME_W, A.FRAME_H


def coll(name):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c


def link_only(ob, c):
    for cc in list(ob.users_collection):
        cc.objects.unlink(ob)
    c.objects.link(ob)


def remove_obj(name):
    ob = bpy.data.objects.get(name)
    if ob:
        me = ob.data if ob.type == 'MESH' else None
        bpy.data.objects.remove(ob, do_unlink=True)
        if me and me.users == 0:
            bpy.data.meshes.remove(me)


def _descendants(ob):
    out = []
    for ch in ob.children:
        out.append(ch)
        out += _descendants(ch)
    return out


def finalize_import(root_name, new_name):
    """Sketchfab 가져오기 계층(root_name)을 메시 하나(new_name)로. 재질 제거, 회전 방식 XYZ."""
    root = bpy.data.objects[root_name]
    bpy.context.view_layer.update()
    objs = [root] + _descendants(root)
    meshes = [o for o in objs if o.type == 'MESH']
    deps = bpy.context.evaluated_depsgraph_get()
    bm = bmesh.new()
    for o in meshes:
        me = o.data
        tmp = me.copy()
        tmp.transform(o.matrix_world)
        bm.from_mesh(tmp)
        bpy.data.meshes.remove(tmp)
    me_new = bpy.data.meshes.new(new_name)
    bm.to_mesh(me_new)
    bm.free()
    me_new.materials.clear()
    ob = bpy.data.objects.new(new_name, me_new)
    for o in reversed(objs):
        d = o.data if o.type == 'MESH' else None
        bpy.data.objects.remove(o, do_unlink=True)
        if d is not None and d.users == 0:
            bpy.data.meshes.remove(d)
    coll('90_STAGING').objects.link(ob)
    ob.rotation_mode = 'XYZ'
    # 원점을 바닥 중심으로
    co = np.empty(len(me_new.vertices) * 3, dtype=np.float64)
    me_new.vertices.foreach_get('co', co)
    co = co.reshape(-1, 3)
    mn, mx = co.min(0), co.max(0)
    off = np.array([(mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2, mn[2]])
    co -= off
    me_new.vertices.foreach_set('co', co.ravel())
    me_new.update()
    ob.location = (800.0, 0.0, 0.0)
    return ob


def mesh_from_arrays(name, verts, faces, c, smooth=False):
    remove_obj(name)
    me = bpy.data.meshes.new(name)
    verts = np.asarray(verts, dtype=np.float32)
    me.vertices.add(len(verts))
    me.vertices.foreach_set('co', verts.ravel())
    if isinstance(faces, np.ndarray) and faces.ndim == 2:
        n, k = faces.shape
        me.loops.add(n * k)
        me.loops.foreach_set('vertex_index', faces.astype(np.int32).ravel())
        me.polygons.add(n)
        me.polygons.foreach_set('loop_start', (np.arange(n) * k).astype(np.int32))
        me.polygons.foreach_set('loop_total', np.full(n, k, dtype=np.int32))
    else:
        flat = [i for f in faces for i in f]
        me.loops.add(len(flat))
        me.loops.foreach_set('vertex_index', flat)
        starts, s = [], 0
        for f in faces:
            starts.append(s)
            s += len(f)
        me.polygons.add(len(faces))
        me.polygons.foreach_set('loop_start', starts)
        me.polygons.foreach_set('loop_total', [len(f) for f in faces])
    me.update(calc_edges=True)
    me.validate()
    if smooth:
        me.shade_smooth()
    ob = bpy.data.objects.new(name, me)
    c.objects.link(ob)
    ob.rotation_mode = 'XYZ'
    return ob


def tri_count(ob):
    deps = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(deps)
    me = ev.to_mesh()
    me.calc_loop_triangles()
    n = len(me.loop_triangles)
    ev.to_mesh_clear()
    return n


def eval_world_coords(ob, step=1):
    deps = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(deps)
    me = ev.to_mesh()
    co = np.empty(len(me.vertices) * 3, dtype=np.float64)
    me.vertices.foreach_get('co', co)
    ev.to_mesh_clear()
    co = co.reshape(-1, 3)[::step]
    M = np.array(ob.matrix_world)
    return co @ M[:3, :3].T + M[:3, 3]


def _cam_frame():
    bpy.context.view_layer.update()
    cam = bpy.data.objects['CAM_iso']
    fr = [np.array(c) for c in cam.data.view_frame(scene=bpy.context.scene)]   # 오른위, 오른아래, 왼아래, 왼위
    return cam, np.array(cam.matrix_world), fr


def project_pts(P):
    """세계 점 배열 → 화면 pt 배열 (정사영·원근 모두)."""
    cam, M, (tr, br, bl, tl) = _cam_frame()
    Mi = np.linalg.inv(M)
    pc = P @ Mi[:3, :3].T + Mi[:3, 3]
    if cam.data.type == 'ORTHO':
        x, y = pc[:, 0], pc[:, 1]
    else:
        s = tr[2] / pc[:, 2]
        x, y = pc[:, 0] * s, pc[:, 1] * s
    u = (x - bl[0]) / (tr[0] - bl[0]) * FRAME_W
    v = (tr[1] - y) / (tr[1] - bl[1]) * FRAME_H
    return np.stack([u, v], 1)


def pts_to_world(uv, h=0.0):
    """화면 pt 배열 (..., 2) → 높이 h 평면 위 세계 점 (..., 3). h는 스칼라 또는 (...) 배열."""
    cam, M, (tr, br, bl, tl) = _cam_frame()
    uv = np.asarray(uv, dtype=np.float64)
    x = uv[..., 0:1] / FRAME_W
    y = uv[..., 1:2] / FRAME_H
    top = tl + (tr - tl) * x
    bot = bl + (br - bl) * x
    pl = top + (bot - top) * y
    p = pl @ M[:3, :3].T + M[:3, 3]
    if cam.data.type == 'ORTHO':
        d = np.broadcast_to(M[:3, :3] @ np.array([0.0, 0.0, -1.0]), p.shape)
    else:
        d = p - M[:3, 3]
    h = np.asarray(h, dtype=np.float64)
    t = (h[..., None] if h.ndim else h) - p[..., 2:3]
    t = t / d[..., 2:3]
    return p + d * t


def rise_per_unit(uv):
    """땅 점(화면 uv)을 1단위 올리면 화면에서 몇 pt 위로 가는지 (원근에선 자리마다 다름)."""
    g = pts_to_world(uv, 0.0)
    g1 = g.reshape(-1, 3).copy()
    g1[:, 2] += 1.0
    v1 = project_pts(g1)[:, 1].reshape(np.asarray(uv).shape[:-1])
    return np.asarray(uv)[..., 1] - v1


def screen_bbox(obs, step=1):
    if not isinstance(obs, (list, tuple)):
        obs = [obs]
    uv = np.concatenate([project_pts(eval_world_coords(o, step)) for o in obs])
    return (float(uv[:, 0].min()), float(uv[:, 1].min()), float(uv[:, 0].max()), float(uv[:, 1].max()))


def bbox_err(got, want):
    return max(abs(g - w) for g, w in zip(got, want))


def fit_to_bbox(obs, want, iters=3, keep_z=False, step=1):
    """obs(원점 = 바닥 중심)를 화면 상자 want에 맞게 균일 축척 + 이동 반복."""
    if not isinstance(obs, (list, tuple)):
        obs = [obs]
    for _ in range(iters):
        bpy.context.view_layer.update()
        got = screen_bbox(obs, step)
        sx = (want[2] - want[0]) / max(1e-6, got[2] - got[0])
        sy = (want[3] - want[1]) / max(1e-6, got[3] - got[1])
        s = (sx + sy) / 2
        for o in obs:
            o.scale = o.scale * s
        bpy.context.view_layer.update()
        got = screen_bbox(obs, step)
        du = (want[0] + want[2]) / 2 - (got[0] + got[2]) / 2
        dv = (want[1] + want[3]) / 2 - (got[1] + got[3]) / 2
        # 화면 이동 (du, dv) → 같은 높이 평면 위 세계 이동
        cu, cv = (got[0] + got[2]) / 2, got[3]
        base = pt_to_world(cu, cv, 0)
        moved = pt_to_world(cu + du, cv + dv, 0)
        dw = moved - base
        for o in obs:
            o.location = o.location + dw
    bpy.context.view_layer.update()
    return screen_bbox(obs, step)
