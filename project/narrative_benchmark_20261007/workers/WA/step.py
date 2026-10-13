"""WA step (wave 1, input v8_14): header band icons, title gate, CORE markers, d3 section leaders, case pins.

Run: Blender -b <in.blend> --factory-startup --python step.py -- <out.blend> [render_prefix]
  Opens any input blend that has the WA objects, applies only WA's changes, checks that no object outside WA's
  ownership changed (mesh, matrix, materials, material values), saves <out.blend>. With render_prefix it also renders
  the two passes (integrate_assets.render_two_pass) and writes <prefix>_wa_report.json.
Idempotent: generated objects are deleted and rebuilt from fixed parameters, colours are absolute, positions are
absolute targets measured on screen at run time (label centres from text_spec, tower silhouette by ray, harbour
mole/sea by ray), one-off mesh edits (gate band inset, colosseum decimate) are guarded by a mesh custom property.

Owned objects: H_* (header band icons, title gate), S_core1~5_badge/underline, S_lead03~S_lead10, S_sect*,
S_pin_harbor*, S_pin_pompeii*. (S_lead02, S_lead_dot2 belong to WB.)
"""
import bpy, bmesh, sys, json, math, hashlib, runpy
from pathlib import Path
import numpy as np
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent
ROOT = next((p for p in [HERE, *HERE.parents] if (p / 'scripts/integrate_assets.py').exists()), HERE.parents[1])
sys.path.insert(0, str(ROOT / 'workers/layout'))
from common import Screen, world_verts, set_world_verts, bvh_of, map_visible_objects, W_PT, H_PT   # noqa: E402

import os
TEXT_SPEC = Path(os.environ.get('WA_TEXT_SPEC', ROOT / 'review_loop/text_spec_r11.json'))   # Figma label boxes (pt);
# text is never moved by this step. Export a newer text_spec and set WA_TEXT_SPEC to re-centre the icons on moved labels.
PROTECTED_DIR = (ROOT / 'out').resolve()
TAG = 'RC.v12_15.'                                       # new WA materials

# ------------------------------------------------------------------------------------------------ parameters
# header rows: icons are centred on their Figma label and stand on one baseline (footprint y, OBJ_PLACE-06)
ROW_FOOT_Y = 124.75                 # pt, sources row today 124.4-125.0; recipe row is brought down to it
LABEL_OF = {'lime': '790:90', 'ash': '790:91', 'stones': '790:92', 'mold': '790:93',
            'books': '790:87', 'research': '790:88', 'colosseum': '790:89'}
# colours (sRGB hex, absolute)
HEX_GATE_SURFACE = '#D7CDB8'        # base_header_surface #EADFC8 x0.83 linear (OBJ_VALUE-09)
HEX_GATE_TRIM = '#C5B190'           # base_header_trim    #D6C09D x0.83 linear
HEX_LIME_PILE = '#F1E6CF'           # lime heap only (OBJ_COLOR-26 / OV04): stops the 62% clipping
HEX_ASH_PILE = '#4A443F'            # Pozzolane Nere: POZZ window C<=0.02, L*<=50 (OBJ_COLOR-13)
HEX_PAPYRUS = '#C7B795'             # scroll sheet: LINEN (h 75-95, C<=0.06, lit L*>=70), contour vs paper
HEX_UNDERLINE = '#923218'           # CORE title underline only (OBJ_COLOR-12, fixed condition 5 #983821)
GATE_BAND_PT = 3.25                 # outer band + archivolt width on the gate front (OBJ_VALUE-09, OBJ_FORM-06)
OVERLAY_FRONT = 149.8133            # depth used for dots (same as S_pin_pompeii_dot)
OVERLAY_MID = 149.9                 # section edges / brick joints, between fill (150) and dots
DOT_R_PT = 1.7                      # leader / pin dot radius (S_sect_dot, S_pin_*_dot)
STONES_SCALE = 1.2                  # rubble group size in H_stones space (label 790:92 is 45 pt wide)
SCROLL_SCALE = 1.15                 # scroll pair in H_books space
DOT_INSET_PT = 1.7                  # dot centre inside the target face (OBJ_PLACE-29 >= 1pt)

OWNED_S = ({f'S_core{i}_{p}' for i in range(1, 6) for p in ('badge', 'underline')}
           | {f'S_lead{i:02d}' for i in range(3, 11)})


def owned(name):
    return (name.startswith('H_') or name in OWNED_S or name.startswith('S_sect')
            or name.startswith('S_pin_harbor') or name.startswith('S_pin_pompeii'))


def need(name):
    o = bpy.data.objects.get(name)
    if o is None:
        raise RuntimeError(f'WA step: object {name!r} not found in {bpy.data.filepath}')
    return o


# ------------------------------------------------------------------------------------------------ fingerprint
def mat_fp(m):
    d = {'diffuse': [round(c, 6) for c in m.diffuse_color], 'rough': round(m.roughness, 6),
         'metal': round(m.metallic, 6)}
    if m.node_tree:
        vals = []
        for n in sorted(m.node_tree.nodes, key=lambda n: n.name):
            for i in n.inputs:
                if hasattr(i, 'default_value'):
                    try:
                        v = [round(x, 6) for x in i.default_value]
                    except TypeError:
                        v = i.default_value
                    vals.append((n.name, i.identifier, str(v)))
        d['nodes'] = hashlib.sha1(repr(vals).encode()).hexdigest()
    return d


def fingerprint():
    F = {'objects': {}, 'materials': {}}
    used = set()
    for o in bpy.data.objects:
        if owned(o.name):
            continue
        e = {'mw': hashlib.sha1(np.array(o.matrix_world).round(6).tobytes()).hexdigest(),
             'mats': [s.material.name if s.material else None for s in o.material_slots],
             'hide_render': o.hide_render, 'parent': o.parent.name if o.parent else None,
             'collections': sorted(c.name for c in o.users_collection)}
        if o.type == 'MESH':
            me = o.data
            co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co)
            mi = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', mi)
            e['mesh'] = hashlib.sha1(co.round(6).tobytes() + mi.tobytes()).hexdigest()
            e['mods'] = [(m.type, m.show_render) for m in o.modifiers]
        F['objects'][o.name] = e
        used.update(x for x in e['mats'] if x)
    for n in sorted(used):
        F['materials'][n] = mat_fp(bpy.data.materials[n])
    return F


def fp_diff(a, b):
    out = []
    for k in ('objects', 'materials'):
        for n in sorted(set(a[k]) | set(b[k])):
            if a[k].get(n) != b[k].get(n):
                out.append(f'{k}:{n}')
    return out


# ------------------------------------------------------------------------------------------------ colours
def s2l(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_lin(h):
    return tuple(s2l(int(h[i:i + 2], 16) / 255) for i in (1, 3, 5))


def set_color(m, hexcol):
    lin = hex_lin(hexcol)
    m.diffuse_color = (*lin, 1.0)
    if m.node_tree:
        for n in m.node_tree.nodes:
            if n.type == 'BSDF_PRINCIPLED':
                n.inputs['Base Color'].default_value = (*lin, 1.0)


def ensure_mat(name, hexcol, template):
    """WA-only material: copy of a template (same Workbench roughness/metallic), colour set absolutely."""
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials[template].copy()
        m.name = name
    set_color(m, hexcol)
    return m


def mat_users(m):
    return {o.name for o in bpy.data.objects for s in o.material_slots if s.material == m}


def assert_owned_only(m):
    bad = sorted(n for n in mat_users(m) if not owned(n))
    if bad:
        raise RuntimeError(f'WA step: material {m.name} is shared with non-owned objects {bad[:5]}; not editing it')


def set_single_material(o, m):
    o.data.materials.clear()
    o.data.materials.append(m)
    for p in o.data.polygons:
        p.material_index = 0


# ------------------------------------------------------------------------------------------------ screen helpers
S = None
FWD = None


def init_screen():
    global S, FWD
    S = Screen()
    FWD = -(S.cam.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()


def depth_of(p):
    return (Vector(p) - S.origin).dot(FWD)


def world_at(pt, depth):
    """world point at the given camera depth whose S.project() is exactly pt (inverse of the projection matrix;
    Screen.ray's view-frame interpolation differs from S.project by up to ~0.04 pt)."""
    x, y = 2.0 * pt[0] / W_PT - 1.0, 1.0 - 2.0 * pt[1] / H_PT
    h0 = np.linalg.solve(S.M, np.array([x, y, -1.0, 1.0])); h1 = np.linalg.solve(S.M, np.array([x, y, 0.999, 1.0]))
    p0 = h0[:3] / h0[3]; p1 = h1[:3] / h1[3]                      # float64 all the way
    d = (p1 - p0) / np.linalg.norm(p1 - p0)
    o = np.array(S.origin, dtype=float); f = np.array(FWD, dtype=float)
    t = (depth - (p0 - o) @ f) / (d @ f)
    return Vector(p0 + d * t)


def pt_of(p):
    return S.project(np.array([list(p)]))[0]


def eval_world_verts(o):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = o.evaluated_get(dg)
    me = ev.to_mesh()
    co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    M = np.array(ev.matrix_world)
    ev.to_mesh_clear()
    return (np.c_[co, np.ones(len(co))] @ M.T)[:, :3]


def group_measure(objs, tol=0.02):
    bpy.context.view_layer.update()
    Wv = np.concatenate([eval_world_verts(o) for o in objs])
    P = S.project(Wv)
    zmin = Wv[:, 2].min()
    low = Wv[Wv[:, 2] <= zmin + tol]
    foot = S.project(np.array([[low[:, 0].mean(), low[:, 1].mean(), zmin]]))[0]
    return {'x0': float(P[:, 0].min()), 'x1': float(P[:, 0].max()), 'y0': float(P[:, 1].min()),
            'y1': float(P[:, 1].max()), 'foot_x': float(foot[0]), 'foot_y': float(foot[1]),
            'cx': float((P[:, 0].min() + P[:, 0].max()) / 2)}


def pt_per_world(p):
    p = Vector(p)
    r = S.cam.matrix_world.col[0].xyz.normalized()
    return float(np.linalg.norm(pt_of(p + r) - pt_of(p)))


def align_group(parent, objs, cx_target, foot_target, iters=6):
    right = S.cam.matrix_world.col[0].xyz.normalized()
    g = None
    for _ in range(iters):
        g = group_measure(objs)
        dx = cx_target - g['cx']; dy = foot_target - g['foot_y']
        if abs(dx) < 0.005 and abs(dy) < 0.005:
            break
        k = pt_per_world(parent.matrix_world.translation)
        parent.location = parent.location + right * (dx / k) + Vector((0, 0, -dy / k))
    return group_measure(objs)


def label_centres():
    spec = json.loads(TEXT_SPEC.read_text())
    box = {t[0]: t[1] for t in spec['texts']}
    return {k: (box[v][0] + box[v][2] / 2.0, box[v][1]) for k, v in LABEL_OF.items()}


# ------------------------------------------------------------------------------------------------ mesh builders
def new_obj(name, bm, parent, mat, collection, smooth=False):
    old = bpy.data.objects.get(name)
    if old is not None:
        me_old = old.data
        bpy.data.objects.remove(old, do_unlink=True)
        if me_old is not None and me_old.users == 0:
            bpy.data.meshes.remove(me_old)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = smooth
    o = bpy.data.objects.new(name, me)
    collection.objects.link(o)
    o.parent = parent
    o.matrix_parent_inverse = Matrix.Identity(4)
    if mat is not None:
        me.materials.append(mat)
    return o


def remove_obj(name):
    o = bpy.data.objects.get(name)
    if o is None:
        return False
    me = o.data if o.type == 'MESH' else None
    bpy.data.objects.remove(o, do_unlink=True)
    if me is not None and me.users == 0:
        bpy.data.meshes.remove(me)
    return True


def bm_cylinder(r, h, seg=32, axis='Z', center=(0, 0, 0), z0=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r, depth=h)
    if axis == 'X':
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, 'Y'))
    bmesh.ops.translate(bm, verts=bm.verts, vec=Vector(center))
    return bm


def bm_box(sx, sy, sz):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=bm.verts)
    return bm


def bm_broken_stone(size, cuts):
    """box cut by planes (normal, distance from centre) -> angular rubble piece, resting on z=0."""
    bm = bm_box(*size)
    for n, d in cuts:
        n = Vector(n).normalized()
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        res = bmesh.ops.bisect_plane(bm, geom=geom, plane_co=n * d, plane_no=n, clear_outer=True)
        cut_edges = [e for e in res['geom_cut'] if isinstance(e, bmesh.types.BMEdge)]
        if cut_edges:
            bmesh.ops.edgeloop_fill(bm, edges=cut_edges)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    zmin = min(v.co.z for v in bm.verts)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, -zmin))
    return bm


def spiral_section(R, r0, turns, t, seg_per_turn=40, tail=0.0):
    """closed (y, z) outline of a rolled sheet seen end-on, axis at origin; the outer end of the sheet is at the
    bottom (z = -R) and, if tail > 0, continues flat toward the viewer (-y) lying on the floor."""
    Th = 2 * math.pi * turns
    n = max(8, int(seg_per_turn * turns))
    th = np.linspace(0.0, Th, n + 1)
    rr = r0 + (R - r0) * th / Th
    # angle measured so that the sheet ends at the bottom (phi = -90 deg) and winds such that the tangent there
    # points to -y (the free sheet runs toward the camera)
    phi = -math.pi / 2 - (Th - th)
    outer = np.c_[-rr * np.cos(phi), rr * np.sin(phi)]
    inner = np.c_[-(rr - t) * np.cos(phi), (rr - t) * np.sin(phi)]
    pts = list(map(tuple, outer))
    if tail > 0:
        pts.append((-tail, -R)); pts.append((-tail, -R + t))
    pts += list(map(tuple, inner[::-1]))
    return pts


def bm_roll(R, r0, turns, t, L, tail=0.0):
    """rolled papyrus: spiral section extruded along local x, resting on z=0 (axis at z=R)."""
    sec = spiral_section(R, r0, turns, t, tail=tail)
    bm = bmesh.new()
    a = [bm.verts.new((-L / 2, y, z + R)) for y, z in sec]
    b = [bm.verts.new((L / 2, y, z + R)) for y, z in sec]
    n = len(sec)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))
    bm.faces.new(a[::-1]); bm.faces.new(b)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def bm_rod_with_knobs(L, R_axis_z, rod_r, protrude, knob_r, knob_len):
    bm = bm_cylinder(rod_r, L + 2 * protrude, seg=16, axis='X', center=(0, 0, R_axis_z))
    for s in (-1, 1):
        k = bm_cylinder(knob_r, knob_len, seg=16, axis='X',
                        center=(s * (L / 2 + protrude - knob_len / 2), 0, R_axis_z))
        tmp = bpy.data.meshes.new('_wa_tmp'); k.to_mesh(tmp); k.free(); bm.from_mesh(tmp); bpy.data.meshes.remove(tmp)
    return bm


def bm_lumpy(seed, r=0.5, amp=0.42):
    """irregular lime lump: icosphere with three low-frequency bulges and a flattened underside."""
    rng = np.random.default_rng(seed)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
    dirs = rng.normal(size=(3, 3)); dirs /= np.linalg.norm(dirs, axis=1)[:, None]
    w = rng.uniform(0.6, 1.0, 3)
    for v in bm.verts:
        n = np.array(v.co.normalized())
        f = 1.0 + amp * float(sum(w[k] * max(0.0, n @ dirs[k]) ** 2 for k in range(3))) - amp * 0.35
        if n[2] < -0.3:
            f *= 0.8
        v.co = Vector(n * r * f)
    return bm


def bm_transform(bm, rot_z_deg=0.0, rot_x_deg=0.0, rot_y_deg=0.0, loc=(0, 0, 0)):
    M = (Matrix.Translation(Vector(loc)) @ Matrix.Rotation(math.radians(rot_z_deg), 4, 'Z')
         @ Matrix.Rotation(math.radians(rot_y_deg), 4, 'Y') @ Matrix.Rotation(math.radians(rot_x_deg), 4, 'X'))
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    return bm


# ------------------------------------------------------------------------------------------------ header gate
def fix_gate(rep):
    body = need('H_gate_body')
    surf = bpy.data.materials['RC.v12.base_header_surface']
    trim = bpy.data.materials['RC.v12.base_header_trim']
    for m in (surf, trim):
        assert_owned_only(m)
    set_color(surf, HEX_GATE_SURFACE)
    set_color(trim, HEX_GATE_TRIM)
    me = body.data
    if me.users != 1:
        body.data = me = me.copy()
    if [m.name if m else None for m in me.materials] != [surf.name, trim.name]:
        me.materials.clear(); me.materials.append(surf); me.materials.append(trim)
    # band width in local units: 3.25 pt measured on the front face
    mw = body.matrix_world
    p0 = mw @ Vector((0, -0.55, 3.0)); p1 = mw @ Vector((1, -0.55, 3.0))
    pt_per_local = float(np.linalg.norm(pt_of(p1) - pt_of(p0)))
    thick = GATE_BAND_PT / pt_per_local
    done = bool(me.get('wa_band', 0))
    bm = bmesh.new(); bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    front = [f for f in bm.faces if f.normal.y < -0.99]
    if not done:
        for f in bm.faces:
            f.material_index = 0
        res = bmesh.ops.inset_region(bm, faces=front, thickness=thick, depth=0.0, use_boundary=True,
                                     use_even_offset=True, use_interpolate=True)
        for f in res['faces']:
            f.material_index = 1
        me['wa_band'] = 1
    # top face (lit strip at the top edge, clipped to 255 before) -> trim tone
    for f in bm.faces:
        if f.normal.z > 0.99:
            f.material_index = 1
    bm.to_mesh(me); bm.free(); me.update()
    rep['gate'] = {'band_pt': GATE_BAND_PT, 'band_local': round(thick, 5), 'pt_per_local': round(pt_per_local, 3),
                   'inset_applied_now': not done}
    # keystone: wedge whose underside sits on the intrados crown (OBJ_FORM-19)
    ks = need('H_gate_keystone')
    crown_local = Vector((0, -0.55, 1.25))
    bvh, _ = bvh_of([body])
    ksm = ks.data
    if ksm.users != 1:
        ks.data = ksm = ksm.copy()
    kv = world_verts(ks)
    kP = S.project(kv)
    cx = float(kP[:, 0].mean())
    # crown on screen: first row below the cornice where the body no longer covers the keystone centre column
    crown_y = None
    for y in np.arange(166.0, 200.0, 0.05):
        o, d = S.ray((cx, y))
        if bvh.ray_cast(o, d)[0] is None:
            crown_y = float(y); break
    if crown_y is None:
        raise RuntimeError('WA step: arch crown not found under the keystone')
    # work in the keystone's own axes: local z = its height (the block is tilted forward, so world z is not)
    me_k = ks.data
    co = np.array([v.co[:] for v in me_k.vertices])
    zl = co[:, 2]
    top = zl > zl.mean(); bot = ~top
    M = ks.matrix_world
    bi = np.where(bot)[0]
    i0 = int(bi[np.argmin([depth_of(M @ Vector(co[i])) for i in bi])])     # front-bottom corner
    zt = float(zl[top].mean())
    lo, hi = zt - 2.0 * (zt - float(zl.min())) - 1.0, zt
    for _ in range(60):                    # bottom local z so that the front-bottom corner sits on the crown
        mid = (lo + hi) / 2
        y = pt_of(M @ Vector((co[i0][0], co[i0][1], mid)))[1]
        if y > crown_y:
            lo = mid
        else:
            hi = mid
    zb = (lo + hi) / 2
    cxl = float(co[top][:, 0].mean()); half = float(np.abs(co[top][:, 0] - cxl).max())
    cur_y = float(pt_of(M @ Vector(co[i0]))[1])
    done_k = abs(cur_y - crown_y) < 0.02 and np.allclose(np.abs(co[bi, 0] - cxl), half * 0.67, atol=1e-5)
    if not done_k:                                # (re-run: wedge already on the crown -> mesh left untouched)
        new = co.copy()
        for i in bi:
            new[i, 2] = zb
            new[i, 0] = cxl + np.sign(co[i, 0] - cxl) * half * 0.67  # wedge, bottom 0.67 of the top width
        me_k.vertices.foreach_set('co', new.ravel()); me_k.update()
    newW = world_verts(ks)

    kP2 = S.project(world_verts(ks))
    rep['keystone'] = {'crown_y': crown_y, 'bottom_y_before': round(float(kP[:, 1].max()), 2),
                       'bottom_y_after_front': round(float(pt_of(newW[i0])[1]), 2),
                       'top_w_pt': round(float(kP2[top][:, 0].max() - kP2[top][:, 0].min()), 2),
                       'bottom_w_pt': round(float(kP2[~top][:, 0].max() - kP2[~top][:, 0].min()), 2)}


# ------------------------------------------------------------------------------------------------ BASIC recipe
def fix_recipe(rep, labels):
    hdr = need('H_mold').users_collection[0]
    toolwood = bpy.data.materials['RC.v12.toolwood']
    # piles: own materials, smooth shading
    lime = need('H_lime_pile'); ash = need('H_ash_pile')
    m_lime = ensure_mat(TAG + 'header_lime_pile', HEX_LIME_PILE, 'RC.v12.base_lime_calcium_crystal')
    m_ash = ensure_mat(TAG + 'header_ash_pile', HEX_ASH_PILE, 'RC.v12.base_pozzolan')
    for o, m in ((lime, m_lime), (ash, m_ash)):
        if o.data.users != 1:
            o.data = o.data.copy()
        set_single_material(o, m)
        me = o.data
        if not me.get('wa_smoothed', 0):          # OBJ_FORM-17: radial scan ridges near the apex -> relax once
            bm = bmesh.new(); bm.from_mesh(me)
            zmin = min(v.co.z for v in bm.verts); zmax = max(v.co.z for v in bm.verts)
            inner = [v for v in bm.verts if v.co.z > zmin + 0.03 * (zmax - zmin)]
            for _ in range(6):
                bmesh.ops.smooth_vert(bm, verts=inner, factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
            bm.to_mesh(me); bm.free(); me['wa_smoothed'] = 1
        for p in me.polygons:
            p.use_smooth = p.normal.z > -0.9          # side smooth, flat underside stays flat
    # wooden boards under both heaps (OBJ_FORM-06 / OBJ_INFO-02: the white heap gets a dark base contour; both
    # heaps get one so the pair stays a controlled comparison)
    for par_name, pile in (('H_lime', lime), ('H_ash', ash)):
        par = need(par_name)
        co = np.empty(len(pile.data.vertices) * 3); pile.data.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
        ML = np.array(pile.matrix_parent_inverse @ pile.matrix_basis)                  # pile in parent space
        loc = (np.c_[co, np.ones(len(co))] @ ML.T)[:, :3]
        rad = float(np.hypot(loc[:, 0], loc[:, 1]).max()); zb = float(loc[:, 2].min())
        bm = bm_cylinder(rad * 1.10, 0.07, seg=48, center=(0, 0, zb - 0.035))
        new_obj(par_name + '_board', bm, par, toolwood, hdr)
    # mold planks -> wood token (OBJ_COLOR-01)
    for i in range(4):
        set_single_material(need(f'H_mold_plank{i}'), toolwood)
    # lime grains in the mold: graded sizes (OBJ_FORM-03-B04), absolute scale from the original 0.2303 sphere
    # lime grains in the mold: graded sizes and lumpy outlines (OBJ_FORM-03-B04: CV >= 0.30, roundness <= 0.85);
    # the grain meshes are rebuilt from a fixed seed every run, the object transforms keep their centres
    diam = [0.20, 0.13, 0.17, 0.095, 0.075]
    for i, d in enumerate(diam):
        g = need(f'H_mold_lime{i}')
        if g.data.users != 1:
            g.data = g.data.copy()
        bm = bm_lumpy(100 + i)
        bm.to_mesh(g.data); g.data.update()
        for p in g.data.polygons:
            p.use_smooth = True
        co = np.array([v.co[:] for v in g.data.vertices])
        s = d / float((co.max(0) - co.min(0)).max())
        g.scale = (s, s, s)
    # broken stones + brick (OBJ_FORM-08-B03): rebuilt every run
    parent = need('H_stones')
    stone_mat = bpy.data.materials['RC.v12.base_stone_middle']
    brick_src = bpy.data.objects.get('D3_brick_course1')
    brick_mat = brick_src.material_slots[0].material if brick_src and brick_src.material_slots else \
        bpy.data.materials['RC.v12.base_pozzolan']
    for n in [o.name for o in bpy.data.objects if o.name.startswith('H_stone') and o.type == 'MESH']:
        remove_obj(n)
    a = bm_broken_stone((0.80, 0.70, 0.62), [((0.55, -0.45, 0.70), 0.26), ((-0.75, -0.25, 0.60), 0.25),
                                             ((0.15, 0.65, 0.75), 0.27), ((-0.55, 0.70, -0.25), 0.31),
                                             ((0.80, 0.35, -0.10), 0.33)])
    bm_transform(a, rot_z_deg=8, loc=(-0.56, -0.06, 0))
    b = bm_broken_stone((0.70, 0.62, 0.54), [((-0.50, -0.55, 0.65), 0.21), ((0.70, -0.20, 0.55), 0.22),
                                             ((0.10, 0.75, 0.55), 0.22), ((0.60, 0.65, -0.20), 0.27),
                                             ((-0.85, 0.20, 0.30), 0.27)])
    bm_transform(b, rot_z_deg=-20, loc=(0.04, 0.40, 0))
    # flat Roman brick (bessalis-like slab, thickness/short side 0.19) standing on its long edge, leaning back
    # 12 deg against stone B, broad face toward the viewer
    brick = bm_box(0.72, 0.09, 0.48)
    bmesh.ops.translate(brick, verts=brick.verts, vec=(0, 0, 0.24))
    bm_transform(brick, rot_x_deg=12, rot_z_deg=-18, loc=(0.64, 0.04, 0.0))
    zmin = min(v.co.z for v in brick.verts)
    bmesh.ops.translate(brick, verts=brick.verts, vec=(0, 0, -zmin))
    objs = []
    for bm in (a, b, brick):
        bmesh.ops.scale(bm, vec=(STONES_SCALE,) * 3, verts=bm.verts)
    for name, bm, m in (('H_stone0', a, stone_mat), ('H_stone1', b, stone_mat), ('H_stone_brick', brick, brick_mat)):
        o = new_obj(name, bm, parent, m, hdr)
        mod = o.modifiers.new('Bevel', 'BEVEL'); mod.width = 0.012; mod.segments = 1; mod.limit_method = 'ANGLE'
        objs.append(o)
    # baseline + centring on labels
    kids = lambda pre: [o for o in bpy.data.objects if o.name.startswith(pre) and o.type == 'MESH']
    groups = {'lime': ('H_lime', kids('H_lime_')), 'ash': ('H_ash', kids('H_ash_')), 'stones': ('H_stones', objs),
              'mold': ('H_mold', [o for o in bpy.data.objects if o.name.startswith('H_mold_') and o.type == 'MESH'])}
    out = {}
    for k, (pn, members) in groups.items():
        before = group_measure(members)
        after = align_group(need(pn), members, labels[k][0], ROW_FOOT_Y)
        out[k] = {'label_cx': labels[k][0], 'before': {x: round(before[x], 2) for x in ('cx', 'foot_y', 'x0', 'x1', 'y0', 'y1')},
                  'after': {x: round(after[x], 2) for x in ('cx', 'foot_y', 'x0', 'x1', 'y0', 'y1')}}
    rep['recipe'] = out
    rep['recipe_brick_material'] = brick_mat.name


# ------------------------------------------------------------------------------------------------ BASIC sources
def fix_sources(rep, labels):
    hdr = need('H_books').users_collection[0]
    linen = ensure_mat(TAG + 'papyrus', HEX_PAPYRUS, 'RC.v12.linen')   # LINEN window, darker than paper
    toolwood = bpy.data.materials['RC.v12.toolwood']
    # 1. scrolls instead of codices (OBJ_FORM-08-B05 blocker)
    books = need('H_books')
    for n in [o.name for o in bpy.data.objects if o.name.startswith('H_book') and o.type == 'MESH']:
        remove_obj(n)
    R1, R2, L1, L2 = 0.25, 0.23, 1.12, 1.04
    # front scroll, partly unrolled toward the viewer
    s1 = bm_roll(R1, 0.06, 2.4, 0.045, L1, tail=0.50)
    k1 = bm_rod_with_knobs(L1, R1, 0.05, 0.10, 0.085, 0.07)
    # back scroll, closed, turned a little
    s2 = bm_roll(R2, 0.055, 2.2, 0.043, L2, tail=0.0)
    k2 = bm_rod_with_knobs(L2, R2, 0.048, 0.10, 0.08, 0.065)
    for bm in (s2, k2):
        bm_transform(bm, rot_z_deg=-12, loc=(0.12, 0.60, 0.0))
    for bm in (s1, k1):
        bm_transform(bm, rot_z_deg=10, loc=(-0.05, -0.05, 0.0))
    for bm in (s1, k1, s2, k2):
        bmesh.ops.scale(bm, vec=(SCROLL_SCALE,) * 3, verts=bm.verts)
    scroll_objs = [new_obj('H_book_scroll1_sheet', s1, books, linen, hdr, smooth=False),
                   new_obj('H_book_scroll1_rod', k1, books, toolwood, hdr, smooth=True),
                   new_obj('H_book_scroll2_sheet', s2, books, linen, hdr, smooth=False),
                   new_obj('H_book_scroll2_rod', k2, books, toolwood, hdr, smooth=True)]
    for o in scroll_objs:
        for p in o.data.polygons:
            # curved sheet sides smooth, flat ends / tail flat
            p.use_smooth = abs(p.normal.x) < 0.5 and not (abs(p.normal.z) > 0.98)
    # 2. drill core of Roman concrete, broken in three, no metal bands (OBJ_INFO-15, OBJ_FORM-03-B06)
    res = need('H_research')
    for n in [o.name for o in bpy.data.objects if (o.name.startswith('H_core_')) and o.type == 'MESH']:
        remove_obj(n)
    rconc = bpy.data.materials['RC.v12.base_lime_specimen_matrix']
    limem = bpy.data.materials['RC.v12.base_lime_calcium_crystal']
    r = 0.30
    segs = [(0.0, 0.66, 0.0, 0.0), (0.69, 1.17, 3.5, -1.5), (1.20, 1.62, -4.5, 2.0)]   # z0, z1, tilt_x, tilt_y (deg)
    core_objs = []
    for i, (z0, z1, tx, ty) in enumerate(segs):
        bm = bm_cylinder(r, z1 - z0, seg=40, center=(0, 0, (z0 + z1) / 2))
        # oblique fracture faces: tilt the top cap of the lower pieces / the bottom cap of the upper pieces
        for v in bm.verts:
            if i < 2 and v.co.z > (z0 + z1) / 2:
                v.co.z += 0.06 * (v.co.x / r) * (1 if i == 0 else -1)
            if i > 0 and v.co.z < (z0 + z1) / 2:
                v.co.z += 0.06 * (v.co.x / r) * (1 if i == 1 else -1)
        if tx or ty:
            c = Vector((0, 0, z0))
            M = Matrix.Translation(c) @ Matrix.Rotation(math.radians(tx), 4, 'X') @ \
                Matrix.Rotation(math.radians(ty), 4, 'Y') @ Matrix.Translation(-c)
            bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
        o = new_obj(f'H_core_seg{i}', bm, res, rconc, hdr, smooth=False)
        for p in o.data.polygons:
            p.use_smooth = abs(p.normal.z) < 0.7
        core_objs.append(o)
    # white lime grains on the viewer side (local -y), 3-4 pt
    grains = [(-0.12, 0.36, 0.055), (0.10, 0.93, 0.065), (-0.06, 1.42, 0.05)]
    for j, (gx, gz, gr) in enumerate(grains):
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=gr)
        yy = -math.sqrt(max(r * r - gx * gx, 0)) + gr * 0.45
        bmesh.ops.translate(bm, verts=bm.verts, vec=(gx, yy, gz))
        core_objs.append(new_obj(f'H_core_lime{j}', bm, res, limem, hdr, smooth=True))
    # lens follows the taller, thinner core: ring centre near the top right of the core
    ring = need('H_lens_ring'); handle = need('H_lens_handle')
    # absolute local placement (original: ring at its own loc); keep the ring/handle relation fixed
    if 'wa_lens_rel' not in res:
        res['wa_lens_rel'] = [list(ring.location), list(handle.location)]
    rl, hl = [Vector(v) for v in res['wa_lens_rel']]
    shift = Vector((-0.22, 0.0, 0.0))
    ring.location = rl + shift; handle.location = hl + shift
    lens_objs = [ring, handle]
    # 3. mini colosseum: left as is. Decimate 5% lowers the surface-detail measure only ~6% and already breaks the
    #    seat tiers; 3% / 2% + smoothing destroys the arcade (renders: crops/col_variants.png) -> OBJ_FORM-21 kept open.
    col = need('H_colosseum_mini')
    rep['colosseum_faces'] = len(col.data.polygons)
    # baseline + centring on labels
    groups = {'books': (books, scroll_objs), 'research': (res, core_objs + lens_objs), 'colosseum': (need('H_colosseum'), [col])}
    out = {}
    for k, (par, members) in groups.items():
        before = group_measure(members)
        after = align_group(par, members, labels[k][0], ROW_FOOT_Y)
        out[k] = {'label_cx': labels[k][0], 'before': {x: round(before[x], 2) for x in ('cx', 'foot_y', 'x0', 'x1', 'y0', 'y1')},
                  'after': {x: round(after[x], 2) for x in ('cx', 'foot_y', 'x0', 'x1', 'y0', 'y1')}}
    rep['sources'] = out
    # unused metal-band material stays in the file without users (not deleted: other files may reference it)


# ------------------------------------------------------------------------------------------------ CORE markers
def fix_core_markers(rep):
    src = bpy.data.materials['RC.v12.base_badge_2']
    m = ensure_mat(TAG + 'base_badge_2_ul', HEX_UNDERLINE, 'RC.v12.base_badge_2')
    for i in range(1, 6):
        set_single_material(need(f'S_core{i}_underline'), m)
    rep['underline_material'] = {m.name: HEX_UNDERLINE}


# ------------------------------------------------------------------------------------------------ 2D helpers
def move_depth(o, depth):
    """slide every vertex along its camera ray to the given depth (screen position unchanged)."""
    Wv = world_verts(o)
    org = np.array(S.origin); f = np.array(FWD)
    d = (Wv - org) @ f
    if np.abs(d - depth).max() < 1e-4:
        return
    Wn = org + (Wv - org) * (depth / d)[:, None]
    set_world_verts(o, Wn)


def screen_pts(o):
    Wv = world_verts(o)
    return S.project(Wv), (Wv - np.array(S.origin)) @ np.array(FWD)


def set_screen_pts(o, P, depth):
    Wn = np.array([list(world_at(p, depth)) for p in P])
    set_world_verts(o, Wn)


def make_dot(name, centre, collection, mat, depth=OVERLAY_FRONT, r=DOT_R_PT, seg=12):
    ring = [(centre[0] + r * math.cos(2 * math.pi * k / seg), centre[1] + r * math.sin(2 * math.pi * k / seg))
            for k in range(seg)]
    bm = bmesh.new()
    c = bm.verts.new(world_at(centre, depth))
    vs = [bm.verts.new(world_at(p, depth)) for p in ring]
    for k in range(seg):
        bm.faces.new((c, vs[k], vs[(k + 1) % seg]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = new_obj(name, bm, None, mat, collection)
    # face the camera like the other dots
    me = o.data
    for p in me.polygons:
        n = p.normal
        if n.dot(FWD) > 0:
            p.flip()
    return o


def set_hline(o, x0, x1):
    """leader quad (4 verts, horizontal): set its two ends in screen x, keep y and depth."""
    P, d = screen_pts(o)
    left = P[:, 0] < P[:, 0].mean()
    if np.abs(P[left, 0] - x0).max() < 0.005 and np.abs(P[~left, 0] - x1).max() < 0.005:
        return                                   # already there (re-run): leave the mesh bit-identical
    P = P.copy(); P[left, 0] = x0; P[~left, 0] = x1
    set_screen_pts(o, P, float(np.median(d)))


# ------------------------------------------------------------------------------------------------ d3 section
def fix_d3(rep):
    coll = need('S_sect0').users_collection[0]
    line = bpy.data.materials['RC.v12.base_line']
    tower = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith('D3_')
             and not o.name.startswith('D3_press')]
    bvh, owner = bvh_of(tower)

    def silhouette(y, x_from=340.0, x_to=280.0):
        for x in np.arange(x_from, x_to, -0.025):
            o, d = S.ray((x, y))
            h = bvh.ray_cast(o, d)
            if h[0] is not None:
                return float(x), owner[h[2]]
        raise RuntimeError(f'WA step: no tower silhouette at y {y}')

    out = {}
    pairs = [(0, 'S_lead03', 'S_lead04'), (1, 'S_lead05', 'S_lead06'), (2, 'S_lead07', 'S_lead08'),
             (3, 'S_lead09', 'S_lead10')]
    for k, ln, rn in pairs:
        L = need(ln); Rr = need(rn)
        PL, dL = screen_pts(L)
        y = round(float(PL[:, 1].mean()), 2)          # rounded: the silhouette scan is then deterministic
        sx, hit = silhouette(y)
        tdot_c = (sx - DOT_INSET_PT, y)
        make_dot(f'S_sect_tdot{k}', tdot_c, coll, line)
        right_end = float(PL[:, 0].max())
        set_hline(L, tdot_c[0] + 0.5, right_end)
        # section side: dot 1.7 pt inside the layer, drawn in front of fill and edge
        sect = need(f'S_sect{k}')
        PS, _ = screen_pts(sect)
        sect_left = float(PS[:, 0].min())
        dot = need(f'S_sect_dot{k}')
        PD, _ = screen_pts(dot)
        cy = float((PD[:, 1].min() + PD[:, 1].max()) / 2)
        new_c = (sect_left + DOT_INSET_PT, cy)
        # rebuild the dot as the same 12-gon fan at the new centre, front depth
        for v_i, p in enumerate(PD):
            pass
        cx_old = float((PD[:, 0].min() + PD[:, 0].max()) / 2)
        _, dD = screen_pts(dot)
        if abs(new_c[0] - cx_old) > 0.005 or abs(float(np.median(dD)) - OVERLAY_FRONT) > 1e-4:
            PDn = PD.copy(); PDn[:, 0] += new_c[0] - cx_old; PDn[:, 1] += new_c[1] - cy
            set_screen_pts(dot, PDn, OVERLAY_FRONT)
        PR, dR = screen_pts(Rr)
        set_hline(Rr, float(PR[:, 0].min()), new_c[0] - 0.5)
        out[ln] = {'y': round(y, 2), 'silhouette_x': round(sx, 2), 'hit': hit, 'tower_dot_c': [round(tdot_c[0], 2), round(y, 2)],
                   'left_end': round(tdot_c[0] + 0.5, 2), 'gap_line_to_silhouette_pt': 0.0}
        out[rn] = {'section_left': round(sect_left, 2), 'dot_c': [round(new_c[0], 2), round(cy, 2)]}
    # brick joints and layer edges in front of the fill (OBJ_FORM-18)
    for n in ['S_sect_brick1227', 'S_sect_brick1233', 'S_sect_brick1239'] + [f'S_sect{k}_edge' for k in range(4)]:
        move_depth(need(n), OVERLAY_MID)
    rep['d3'] = out


# ------------------------------------------------------------------------------------------------ pins
def fix_pins(rep):
    mv = [o for o in map_visible_objects()]
    bvh, owner = bvh_of(mv)

    def hit(p):
        o, d = S.ray(p)
        h = bvh.ray_cast(o, d)
        return owner[h[2]] if h[0] is not None else None

    def sea_dist(c, rmax=4.0, step=0.05):
        best = 99.0
        for dx in np.arange(-rmax, rmax + 1e-9, step):
            for dy in np.arange(-rmax, rmax + 1e-9, step):
                r = math.hypot(dx, dy)
                if r < best and hit((c[0] + dx, c[1] + dy)) == 'L10_sea':
                    best = r
        return best

    dot = need('S_pin_harbor_dot'); dash = need('S_pin_harbor')
    PD, dD = screen_pts(dot)
    c_old = (float((PD[:, 0].min() + PD[:, 0].max()) / 2), float((PD[:, 1].min() + PD[:, 1].max()) / 2))
    target = DOT_R_PT          # whole dot on the mole (inside >= 1 pt is the pass line)
    cands = [c_old, (c_old[0] - 0.5, c_old[1] - 0.9)]
    best = None
    for c in cands:
        if hit(c) == 'L09_portus_mole' and sea_dist(c, 2.5, 0.05) >= target - 1e-6:
            best = c; break
    if best is None:   # small search for the nearest point with the dot fully on the mole
        for rr in np.arange(0.25, 3.01, 0.25):
            for a in np.arange(0, 360, 15):
                c = (c_old[0] + rr * math.cos(math.radians(a)), c_old[1] + rr * math.sin(math.radians(a)))
                if hit(c) == 'L09_portus_mole' and sea_dist(c, 2.5, 0.05) >= target:
                    best = c; break
            if best:
                break
    if best is None:
        best = c_old
    sd_before = sea_dist(c_old)
    delta = np.array(best) - np.array(c_old)
    if np.abs(delta).max() < 0.005 and abs(float(np.median(dD)) - OVERLAY_FRONT) < 1e-4:
        delta = np.zeros(2)                       # re-run: dot already placed
    else:
        set_screen_pts(dot, PD + delta, OVERLAY_FRONT)
    # dashed line: far end fixed, start follows the dot (linear stretch along the line)
    PH, dH = screen_pts(dash)
    E = PH[np.argmax(np.linalg.norm(PH - np.array(c_old), axis=1))]
    u = np.array(c_old) - E; Lr = np.linalg.norm(u); u = u / Lr
    t = np.clip(((PH - E) @ u) / Lr, 0, 1)
    if np.abs(delta).max() > 0:
        PHn = PH + t[:, None] * delta[None, :]
        set_screen_pts(dash, PHn, float(np.median(dH)))
    rep['pin_harbor'] = {'centre_before': [round(c, 2) for c in c_old], 'centre_after': [round(c, 2) for c in best],
                         'sea_dist_before': round(sd_before, 3), 'sea_dist_after': round(sea_dist(best), 3),
                         'dot_depth': OVERLAY_FRONT}


# ------------------------------------------------------------------------------------------------ main
def apply():
    init_screen()
    rep = {}
    before = fingerprint()
    labels = label_centres()
    rep['labels'] = {k: round(v[0], 2) for k, v in labels.items()}
    fix_gate(rep)
    fix_recipe(rep, labels)
    fix_sources(rep, labels)
    fix_core_markers(rep)
    fix_d3(rep)
    fix_pins(rep)
    for n in ('RC.v12.base_road_foundation', 'RC.v12.base_steel_if_separate', 'RC.v12.base_modern_concrete'):
        m = bpy.data.materials.get(n)
        if m is not None and not mat_users(m):
            m.use_fake_user = True                # registry tokens stay in the file even without users
    bpy.context.view_layer.update()
    after = fingerprint()
    diff = fp_diff(before, after)
    rep['ownership_check'] = {'non_owned_objects': len(after['objects']), 'materials_checked': len(after['materials']),
                              'changed': diff}
    if diff:
        raise RuntimeError('WA step: non-owned data changed, not saving: ' + ', '.join(diff[:20]))
    return rep


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    if not argv:
        raise SystemExit('usage: blender -b in.blend --factory-startup --python step.py -- out.blend [render_prefix]')
    out = Path(argv[0]).resolve(); src = Path(bpy.data.filepath).resolve()
    if out == src or out.parent == PROTECTED_DIR or out.exists() and out.parent == PROTECTED_DIR:
        raise SystemExit(f'WA step: refusing to write {out}')
    rep = apply()
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(out), copy=True)
    rep['input'] = str(src); rep['output'] = str(out)
    if len(argv) > 1:
        prefix = Path(argv[1]).resolve()
        H = runpy.run_path(str(ROOT / 'scripts/integrate_assets.py'), run_name='helpers')
        rep['render'] = H['render_two_pass'](prefix.with_suffix('.png'))
        prefix.with_name(prefix.name + '_wa_report.json').write_text(json.dumps(rep, ensure_ascii=False, indent=1))
    print('WA_STEP ' + json.dumps(rep, ensure_ascii=False))


if __name__ == '__main__':
    main()
