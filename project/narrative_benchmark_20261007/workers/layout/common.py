"""Shared helpers for the layout worker (camera/screen maths, terrain, visibility). Imported by step.py and
measure_export.py inside Blender. Formulas are the ones in scripts/user_v8_13.py and review_r8_fixes_v8_11.py."""
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

W_PT, H_PT = 1191, 1684
OVERLAY = {'80_SHAPES', '81_NOSHADOW', '85_HEADER'}


def need(name):
    o = bpy.data.objects.get(name)
    if o is None:
        raise RuntimeError(f'layout step: object {name!r} not found in {bpy.data.filepath}')
    return o


class Screen:
    def __init__(self):
        self.sc = bpy.context.scene
        self.cam = self.sc.camera
        if self.cam is None:
            raise RuntimeError('scene has no camera')
        self.frame = [self.cam.matrix_world @ v for v in self.cam.data.view_frame(scene=self.sc)]
        self.origin = self.cam.matrix_world.translation.copy()
        dg = bpy.context.evaluated_depsgraph_get()
        r = self.sc.render
        P = self.cam.calc_matrix_camera(dg, x=r.resolution_x, y=r.resolution_y,
                                        scale_x=r.pixel_aspect_x, scale_y=r.pixel_aspect_y)
        self.M = np.array(P @ self.cam.matrix_world.inverted())
        # the vectorised projection must agree with world_to_camera_view
        test = [Vector((x, y, z)) for x, y, z in ((0, 0, 0), (-30, 40, 1), (25, -20, 0), (-60, 30, 3))]
        a = np.array([self.to_pt(p) for p in test]); b = self.project(np.array([p[:] for p in test]))
        assert np.abs(a - b).max() < 1e-3, (a, b)

    def to_pt(self, p):
        v = world_to_camera_view(self.sc, self.cam, p)
        return np.array((v.x * W_PT, (1 - v.y) * H_PT))

    def project(self, W):
        W = np.asarray(W, float)
        H = np.c_[W, np.ones(len(W))] @ self.M.T
        ndc = H[:, :2] / H[:, 3:4]
        return np.c_[(ndc[:, 0] + 1) / 2 * W_PT, (1 - (ndc[:, 1] + 1) / 2) * H_PT]

    def ray(self, pt):
        u, v = pt[0] / W_PT, 1 - pt[1] / H_PT
        tr, br, bl, tl = self.frame
        return self.origin, ((bl + (br - bl) * u + (tl - bl) * v) - self.origin).normalized()

    def world_per_pt(self, p):
        r = self.cam.matrix_world.col[0].xyz.normalized()
        return 1.0 / np.linalg.norm(self.to_pt(p + r) - self.to_pt(p))


def world_verts(o):
    me = o.data
    co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    M = np.array(o.matrix_world)
    return (np.c_[co, np.ones(len(co))] @ M.T)[:, :3]


def set_world_verts(o, W):
    Mi = np.array(o.matrix_world.inverted())
    co = (np.c_[W, np.ones(len(W))] @ Mi.T)[:, :3]
    o.data.vertices.foreach_set('co', co.ravel()); o.data.update()


def bvh_of(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    verts, polys, owner = [], [], []
    for o in objs:
        ev = o.evaluated_get(dg); me = ev.to_mesh(); mw = o.matrix_world; b = len(verts)
        verts += [mw @ v.co for v in me.vertices]; polys += [[b + i for i in p.vertices] for p in me.polygons]
        owner += [o.name] * len(me.polygons)
        ev.to_mesh_clear()
    return BVHTree.FromPolygons(verts, polys), owner


class Terrain:
    def __init__(self, land):
        self.bvh, _ = bvh_of([land])

    def z(self, x, y):
        h = self.bvh.ray_cast(Vector((x, y, 500)), Vector((0, 0, -1)))[0]
        return h.z if h else 0.0


def map_visible_objects(include_overlay=False):
    """mesh objects rendered in the map pass (render_two_pass hides the overlay collections there)."""
    vl = bpy.context.view_layer
    vis = set()

    def walk(lc, hidden):
        c = lc.collection
        h = hidden or lc.exclude or c.hide_render
        if not include_overlay and c.name in OVERLAY:
            h = True
        for o in c.objects:
            if not h and not o.hide_render and o.type == 'MESH':
                vis.add(o.name)
        for ch in lc.children:
            walk(ch, h)
    walk(vl.layer_collection, False)
    return [bpy.data.objects[n] for n in sorted(vis)]


def overlay_objects():
    allv = {o.name for o in map_visible_objects(include_overlay=True)}
    mapv = {o.name for o in map_visible_objects()}
    return [bpy.data.objects[n] for n in sorted(allv - mapv)]


def screen_tris(o, S):
    """projected loop triangles of an evaluated object: (verts_pt (n,2), tris (m,3))."""
    dg = bpy.context.evaluated_depsgraph_get()
    ev = o.evaluated_get(dg); me = ev.to_mesh(); me.calc_loop_triangles()
    co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    M = np.array(o.matrix_world); Wv = (np.c_[co, np.ones(len(co))] @ M.T)[:, :3]
    tri = np.empty(len(me.loop_triangles) * 3, np.int32); me.loop_triangles.foreach_get('vertices', tri)
    ev.to_mesh_clear()
    return S.project(Wv) if len(Wv) else np.zeros((0, 2)), tri.reshape(-1, 3)


def sample_tris(P, T, roi, spacing=0.5):
    """points covering the triangles (vertices, edges, interior) with <= spacing pt gaps, limited to roi."""
    if len(T) == 0:
        return np.zeros((0, 2))
    x0, x1, y0, y1 = roi
    tri = P[T]
    keep = (tri[:, :, 0].max(1) >= x0) & (tri[:, :, 0].min(1) <= x1) & (tri[:, :, 1].max(1) >= y0) & (tri[:, :, 1].min(1) <= y1)
    tri = tri[keep]
    if len(tri) == 0:
        return np.zeros((0, 2))
    L = np.max(np.linalg.norm(tri - np.roll(tri, 1, axis=1), axis=2), axis=1)
    n = np.clip(np.ceil(L / spacing).astype(int), 1, 400)
    out = []
    for k in np.unique(n):
        sel = tri[n == k]
        ij = np.array([(i, j) for i in range(k + 1) for j in range(k + 1 - i)], float) / k
        w = np.c_[1 - ij.sum(1), ij]                      # barycentric weights
        out.append(np.einsum('wk,tkd->twd', w, sel).reshape(-1, 2))
    return np.concatenate(out)
