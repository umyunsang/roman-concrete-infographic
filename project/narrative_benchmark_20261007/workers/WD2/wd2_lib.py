"""WD2 geometry/material helpers used by step.py (Blender only)."""
import bpy, bmesh, math
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree


# ------------------------------------------------------------------ colour / material
def srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lin_to_srgb(c):
    c = max(0.0, min(1.0, c))
    return c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def hex_lin(h):
    return tuple(srgb_to_lin(int(h[i:i + 2], 16) / 255) for i in (1, 3, 5))


def lin_hex(rgb):
    return '#' + ''.join(f'{round(lin_to_srgb(c) * 255):02X}' for c in rgb[:3])


def set_mat_color(m, hex_):
    lin = hex_lin(hex_)
    m.diffuse_color = (*lin, 1.0)
    if m.use_nodes and m.node_tree:
        for n in m.node_tree.nodes:
            if n.type == 'BSDF_PRINCIPLED':
                n.inputs['Base Color'].default_value = (*lin, 1.0)
    return m


def material_copy(name, template_name, hex_):
    """find-or-create `name` as a copy of template (so render settings match), colour hex_."""
    m = bpy.data.materials.get(name)
    if m is None:
        t = bpy.data.materials.get(template_name)
        m = t.copy() if t else bpy.data.materials.new(name)
        m.name = name
    return set_mat_color(m, hex_)


def mat_hex(m):
    return lin_hex(m.diffuse_color)


# ------------------------------------------------------------------ mesh helpers
def islands_bm(bm):
    bm.faces.ensure_lookup_table()
    seen = set(); out = []
    for f in bm.faces:
        if f.index in seen:
            continue
        st = [f]; seen.add(f.index); fs = []
        while st:
            a = st.pop(); fs.append(a.index)
            for e in a.edges:
                for g in e.link_faces:
                    if g.index not in seen:
                        seen.add(g.index); st.append(g)
        out.append(sorted(fs))
    return out


def islands(me):
    bm = bmesh.new(); bm.from_mesh(me)
    out = islands_bm(bm); bm.free()
    return out


def box_bm(bm, x0, x1, y0, y1, z0, z1, mat=0, bevel=0.0, segs=2):
    """add an axis-aligned box to bm (optionally bevelled); returns its faces."""
    vs = [bm.verts.new((x, y, z)) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    idx = [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)]
    fs = [bm.faces.new([vs[i] for i in q]) for q in idx]
    for f in fs:
        f.material_index = mat
    if bevel > 0:
        edges = list({e for f in fs for e in f.edges})
        res = bmesh.ops.bevel(bm, geom=edges + vs, offset=bevel, segments=segs, affect='EDGES', profile=0.5,
                              clamp_overlap=True)
        fs = [f for f in res['faces']] + [f for f in fs if f.is_valid]
        for f in res['faces']:
            f.material_index = mat
    return fs


def cyl_bm(bm, cx, cy, r, z0, z1, mat=0, segs=24, r_top=None):
    r_top = r if r_top is None else r_top
    bot = [bm.verts.new((cx + r * math.cos(2 * math.pi * i / segs), cy + r * math.sin(2 * math.pi * i / segs), z0)) for i in range(segs)]
    top = [bm.verts.new((cx + r_top * math.cos(2 * math.pi * i / segs), cy + r_top * math.sin(2 * math.pi * i / segs), z1)) for i in range(segs)]
    fs = []
    for i in range(segs):
        j = (i + 1) % segs
        fs.append(bm.faces.new((bot[i], bot[j], top[j], top[i])))
    fs.append(bm.faces.new(list(reversed(bot))))
    fs.append(bm.faces.new(top))
    for f in fs:
        f.material_index = mat
    return fs


def mesh_from_bm(name, bm):
    me = bpy.data.meshes.get(name)
    if me is None:
        me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me); me.update()
    return me


def boolean_diff(me, cutters_me, solver='EXACT'):
    """return a new mesh = me minus cutters (both in the same local space); temp objects are removed."""
    coll = bpy.context.scene.collection
    a = bpy.data.objects.new('_wd2_bool_a', me); coll.objects.link(a)
    b = bpy.data.objects.new('_wd2_bool_b', cutters_me); coll.objects.link(b)
    b.hide_render = True
    mod = a.modifiers.new('cut', 'BOOLEAN'); mod.operation = 'DIFFERENCE'; mod.object = b; mod.solver = solver
    dg = bpy.context.evaluated_depsgraph_get(); dg.update()
    ev = a.evaluated_get(dg)
    out = bpy.data.meshes.new_from_object(ev)
    bpy.data.objects.remove(a); bpy.data.objects.remove(b)
    bpy.data.meshes.remove(cutters_me)
    return out


def append_mesh(bm, me, mat_map=None, matrix=None):
    """append mesh `me` into bm (optionally transformed), remapping material indices by mat_map dict."""
    tmp = bmesh.new(); tmp.from_mesh(me)
    if matrix is not None:
        bmesh.ops.transform(tmp, matrix=matrix, verts=tmp.verts)
    vmap = {}
    for v in tmp.verts:
        vmap[v.index] = bm.verts.new(v.co)
    tmp.verts.index_update()
    for f in tmp.faces:
        try:
            nf = bm.faces.new([vmap[v.index] for v in f.verts])
        except ValueError:
            continue
        nf.material_index = mat_map.get(f.material_index, f.material_index) if mat_map else f.material_index
        nf.smooth = f.smooth
    tmp.free()


# ------------------------------------------------------------------ ray helpers
def bvh_world(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    verts, polys = [], []
    for o in objs:
        ev = o.evaluated_get(dg); me = ev.to_mesh(); mw = o.matrix_world; b = len(verts)
        verts += [mw @ v.co for v in me.vertices]; polys += [[b + i for i in p.vertices] for p in me.polygons]
        ev.to_mesh_clear()
    return BVHTree.FromPolygons(verts, polys)


def ray_down_z(bvh, x, y, top=60.0):
    h = bvh.ray_cast(Vector((x, y, top)), Vector((0, 0, -1)))
    return h[0].z if h[0] is not None else None
