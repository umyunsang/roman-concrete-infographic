"""화면 좌표(pt)로 그리는 평면 도형을 Blender에 만들기 — 선·화살표·점·원·점선 (15:26 사용자: 오버레이는 글만, 도형은 모두 Blender)
도형은 카메라를 향한 평면(카메라 시선에 수직)에 놓이며, 기준점(ref) 깊이에 둔다 → 그 자리의 물체와 같은 깊이, 화면에선 정확히 지정한 pt에 보임.
Workbench 그림자가 생기지 않게 visible_shadow=False.
사용: S = exec로 불러서 line(name, [(u,v),...], width_pt, ref_world, gray), arrow(...), dot(...), ring(...), dashed(...)
"""
import math
import bpy
import numpy as np
from mathutils import Vector

U = bpy.data.texts['asset_utils.py'].as_module()


def _cam():
    bpy.context.view_layer.update()
    cam = bpy.data.objects['CAM_iso']
    return cam, cam.matrix_world.translation.copy(), (cam.matrix_world.to_3x3() @ Vector((0, 0, -1))).normalized()


def to_plane(uv, ref):
    """화면 pt 배열 → 기준점 깊이의 카메라 평면 위 세계 점"""
    cam, C, f = _cam()
    uv = np.asarray(uv, float).reshape(-1, 2)
    G = U.pts_to_world(uv, 0.0)
    out = []
    dref = (Vector(ref) - C).dot(f)
    for g in G:
        d = (Vector(g) - C).normalized()
        t = dref / d.dot(f)
        out.append(C + d * t)
    return np.array([tuple(p) for p in out])


def _mesh(name, verts, faces, coll, gray, lift=0.0):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.update()
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    ob.color = (gray, gray, gray, 1)
    try:
        ob.visible_shadow = False
    except Exception:
        pass
    if lift:
        cam, C, f = _cam()
        ob.location = -f * lift          # 카메라 쪽으로 살짝(가려지지 않게)
    return ob


def polyline_strip(uv, width):
    """화면 폴리라인 → 두께 width(pt)의 띠 다각형들(화면 pt)"""
    uv = np.asarray(uv, float)
    quads = []
    for a, b in zip(uv[:-1], uv[1:]):
        d = b - a; L = np.linalg.norm(d)
        if L < 1e-6:
            continue
        n = np.array([-d[1], d[0]]) / L * width / 2
        quads.append([a + n, b + n, b - n, a - n])
    return quads


def line(name, uv, width, ref, coll, gray=0.1, lift=0.05):
    polys = polyline_strip(uv, width)
    verts, faces = [], []
    for q in polys:
        P = to_plane(q, ref); b = len(verts); verts += list(P); faces.append((b, b + 1, b + 2, b + 3))
    return _mesh(name, verts, faces, coll, gray, lift)


def dashed(name, uv, width, on, off, ref, coll, gray=0.3, lift=0.05):
    uv = np.asarray(uv, float)
    seg = np.r_[0, np.cumsum(np.hypot(*np.diff(uv, axis=0).T))]
    pieces = []
    s = 0.0
    while s < seg[-1]:
        e = min(seg[-1], s + on)
        ss = np.linspace(s, e, 4)
        pieces.append(np.c_[np.interp(ss, seg, uv[:, 0]), np.interp(ss, seg, uv[:, 1])])
        s = e + off
    verts, faces = [], []
    for p in pieces:
        for q in polyline_strip(p, width):
            P = to_plane(q, ref); b = len(verts); verts += list(P); faces.append((b, b + 1, b + 2, b + 3))
    return _mesh(name, verts, faces, coll, gray, lift)


def disc(name, center, r, ref, coll, gray=0.07, n=32, lift=0.05):
    c = np.asarray(center, float)
    ring_ = [c + r * np.array([math.cos(2 * math.pi * k / n), math.sin(2 * math.pi * k / n)]) for k in range(n)]
    P = to_plane([c] + ring_, ref)
    faces = [(0, k + 1, (k + 1) % n + 1) for k in range(n)]
    return _mesh(name, P, faces, coll, gray, lift)


def arrow(name, a, b, width, head, ref, coll, gray=0.15, lift=0.05):
    a = np.asarray(a, float); b = np.asarray(b, float)
    d = (b - a) / np.linalg.norm(b - a); n = np.array([-d[1], d[0]])
    shaft_end = b - d * head
    q = [a + n * width / 2, shaft_end + n * width / 2, shaft_end - n * width / 2, a - n * width / 2]
    tri = [shaft_end + n * head * 0.55, b, shaft_end - n * head * 0.55]
    P = to_plane(q + tri, ref)
    return _mesh(name, P, [(0, 1, 2, 3), (4, 5, 6)], coll, gray, lift)
