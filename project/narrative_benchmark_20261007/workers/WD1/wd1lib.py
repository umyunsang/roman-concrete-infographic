"""wd1lib.py - helpers for the WD1 (large landmarks) step: screen maths, ray masks, numpy morphology, fingerprints.
Imported by step.py inside Blender (no scipy there)."""
import bpy, hashlib, math
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

W_PT, H_PT = 1191, 1684
OVERLAY = {'80_SHAPES', '81_NOSHADOW', '85_HEADER'}


class Screen:
    def __init__(self):
        self.sc = bpy.context.scene
        self.cam = self.sc.camera
        self.frame = [self.cam.matrix_world @ v for v in self.cam.data.view_frame(scene=self.sc)]
        self.origin = self.cam.matrix_world.translation.copy()
        dg = bpy.context.evaluated_depsgraph_get()
        r = self.sc.render
        P = self.cam.calc_matrix_camera(dg, x=r.resolution_x, y=r.resolution_y, scale_x=r.pixel_aspect_x, scale_y=r.pixel_aspect_y)
        self.M = np.array(P @ self.cam.matrix_world.inverted())
        test = [Vector(p) for p in ((0, 0, 0), (-30, 40, 1), (25, -20, 0), (-60, 30, 3))]
        a = np.array([self.to_pt(p) for p in test]); b = self.project(np.array([p[:] for p in test]))
        assert np.abs(a - b).max() < 1e-3, (a, b)

    def to_pt(self, p):
        v = world_to_camera_view(self.sc, self.cam, Vector(p))
        return np.array((v.x * W_PT, (1 - v.y) * H_PT))

    def project(self, Wp):
        Wp = np.asarray(Wp, float)
        H = np.c_[Wp, np.ones(len(Wp))] @ self.M.T
        ndc = H[:, :2] / H[:, 3:4]
        return np.c_[(ndc[:, 0] + 1) / 2 * W_PT, (1 - (ndc[:, 1] + 1) / 2) * H_PT]

    def ray(self, pt):
        u, v = pt[0] / W_PT, 1 - pt[1] / H_PT
        tr, br, bl, tl = self.frame
        return self.origin, ((bl + (br - bl) * u + (tl - bl) * v) - self.origin).normalized()

    def wu_per_pt(self, p):
        r = self.cam.matrix_world.col[0].xyz.normalized()
        p = Vector(p)
        return 1.0 / np.linalg.norm(self.to_pt(p + r) - self.to_pt(p))


def world_verts(o):
    me = o.data
    co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    M = np.array(o.matrix_world)
    return (np.c_[co, np.ones(len(co))] @ M.T)[:, :3]


def local_from_world(o, Wp):
    Mi = np.array(o.matrix_world.inverted())
    return (np.c_[Wp, np.ones(len(Wp))] @ Mi.T)[:, :3]


def map_visible_objects(include_overlay=False):
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


def bvh_of(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    verts, polys, owner, fidx = [], [], [], []
    for o in objs:
        ev = o.evaluated_get(dg); me = ev.to_mesh(); mw = o.matrix_world; b = len(verts)
        verts += [mw @ v.co for v in me.vertices]
        polys += [[b + i for i in p.vertices] for p in me.polygons]
        owner += [o.name] * len(me.polygons); fidx += list(range(len(me.polygons)))
        ev.to_mesh_clear()
    return BVHTree.FromPolygons(verts, polys), owner, fidx


class Terrain:
    def __init__(self, land):
        self.bvh, _, _ = bvh_of([land])

    def z(self, x, y):
        h = self.bvh.ray_cast(Vector((x, y, 500)), Vector((0, 0, -1)))[0]
        return h.z if h else 0.0


def ray_grid(S, box, ppt, bvh_all, owner, fidx, bvh_own=None):
    """per pixel (pixel centres) first hit among all map objects: (name index grid, names, face grid, hit points)."""
    x0, x1, y0, y1 = box
    xs = np.arange(x0, x1, 1 / ppt) + 0.5 / ppt; ys = np.arange(y0, y1, 1 / ppt) + 0.5 / ppt
    names = []; nm = {}
    hit = -np.ones((len(ys), len(xs)), np.int32); face = -np.ones_like(hit); pts = np.zeros(hit.shape + (3,))
    own_only = np.zeros(hit.shape, bool); own_face = -np.ones_like(hit)
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            org, d = S.ray((x, y))
            loc, n, idx, dist = bvh_all.ray_cast(org, d)
            if idx is not None:
                o = owner[idx]
                if o not in nm:
                    nm[o] = len(names); names.append(o)
                hit[j, i] = nm[o]; face[j, i] = fidx[idx]; pts[j, i] = loc[:]
            if bvh_own is not None:
                loc2, n2, idx2, d2 = bvh_own.ray_cast(org, d)
                if idx2 is not None:
                    own_only[j, i] = True; own_face[j, i] = idx2
    return {'hit': hit, 'names': names, 'face': face, 'pts': pts, 'own_only': own_only, 'own_face': own_face,
            'box': box, 'ppt': ppt}


def _shift(m, dy, dx):
    out = np.zeros_like(m)
    H, Wd = m.shape
    ys0, ys1 = max(0, dy), min(H, H + dy); xs0, xs1 = max(0, dx), min(Wd, Wd + dx)
    out[ys0:ys1, xs0:xs1] = m[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
    return out


def disk(r):
    return [(dy, dx) for dy in range(-r, r + 1) for dx in range(-r, r + 1) if dy * dy + dx * dx <= r * r]


def erode(m, offs):
    out = np.ones_like(m)
    for dy, dx in offs:
        out &= _shift(m, dy, dx)
    return out


def dilate(m, offs):
    out = np.zeros_like(m)
    for dy, dx in offs:
        out |= _shift(m, dy, dx)
    return out


def label(m):
    """8-connected components: list of (ys, xs) arrays."""
    seen = np.zeros_like(m); comps = []
    H, Wd = m.shape
    for y0, x0 in zip(*np.nonzero(m)):
        if seen[y0, x0]:
            continue
        st = [(y0, x0)]; seen[y0, x0] = True; ys = []; xs = []
        while st:
            y, x = st.pop(); ys.append(y); xs.append(x)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < H and 0 <= xx < Wd and m[yy, xx] and not seen[yy, xx]:
                        seen[yy, xx] = True; st.append((yy, xx))
        comps.append((np.array(ys), np.array(xs)))
    return comps


def comp_len_pt(ys, xs, ppt):
    P = np.c_[xs, ys].astype(float) / ppt
    if len(P) > 2500:
        return float(np.ptp(P, 0).max())
    D = np.sqrt(((P[:, None] - P[None]) ** 2).sum(-1))
    return float(D.max())


def fill_holes(m):
    """True inside m or in regions of ~m not connected to the border."""
    outside = np.zeros_like(m)
    H, Wd = m.shape
    st = [(y, x) for y in range(H) for x in (0, Wd - 1) if not m[y, x]] + [(y, x) for x in range(Wd) for y in (0, H - 1) if not m[y, x]]
    for y, x in st:
        outside[y, x] = True
    while st:
        y, x = st.pop()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < H and 0 <= xx < Wd and not m[yy, xx] and not outside[yy, xx]:
                outside[yy, xx] = True; st.append((yy, xx))
    return ~outside


# ---------------------------------------------------------------- fingerprints (ownership check)
def mesh_hash(me):
    h = hashlib.sha256()
    co = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get('co', co); h.update(np.round(co, 5).tobytes())
    pv = np.empty(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', pv); h.update(pv.tobytes())
    mi = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', mi); h.update(mi.tobytes())
    return h.hexdigest()[:16]


def mat_sig(m):
    if m is None:
        return None
    return [m.name, [round(c, 5) for c in m.diffuse_color], round(m.metallic, 4), round(m.roughness, 4)]


def fingerprint(exclude):
    fp = {}
    for o in bpy.data.objects:
        if o.name in exclude:
            continue
        e = {'mw': [round(v, 5) for row in o.matrix_world for v in row], 'hide': [o.hide_render, o.hide_viewport],
             'mats': [mat_sig(s.material) for s in o.material_slots], 'data': o.data.name if o.data else None,
             'mods': [(m.name, m.type, m.show_render) for m in o.modifiers]}
        if o.type == 'MESH':
            e['mesh'] = mesh_hash(o.data)
        fp[o.name] = e
    return fp


def srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lin_to_srgb(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def hex_to_lin(hx):
    hx = hx.lstrip('#')
    return [srgb_to_lin(int(hx[i:i + 2], 16) / 255) for i in (0, 2, 4)]


def lin_to_hex(c):
    return '#' + ''.join('%02X' % int(round(max(0, min(1, lin_to_srgb(v))) * 255)) for v in c[:3])
