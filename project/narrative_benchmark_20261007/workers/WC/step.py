"""WC step (wave 1): CORE ③④⑤ figures, seawater tank (D1) and CORE ① building.

Run:  Blender -b <in.blend> --factory-startup --python step.py -- <out.blend> [render_prefix]

Idempotent: every object that is edited keeps its v8_14 source data in a custom property ('wc_src') the first time,
and every run rebuilds from that source, so step(step(x)) == step(x). Objects are found by name; terrain heights,
screen positions and camera maths are recomputed at run time (layout/common.py Screen/Terrain).

Ownership: only WC objects change (OWNED_RE). Before saving, mesh/matrix/material fingerprints of every other object
are compared with the input; any difference aborts the save. Materials used by other workers' objects are copied
(labstone -> RC.v12_wc.lab_bench, base_modern_concrete -> RC.v12_wc.d1_tank). Token exceptions owned by WC:
RC.v12.base_water_process (water token) and RC.v12_5.crack_groove (all users are WC objects).
"""
import bpy, bmesh, sys, json, math, re, hashlib, runpy
from pathlib import Path
import numpy as np
from mathutils import Vector, Matrix, noise
from mathutils.bvhtree import BVHTree

NB = Path('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work')
sys.path.insert(0, str(NB / 'workers/layout'))
from common import Screen, world_verts, Terrain  # noqa: E402

LOG = []


def log(*a):
    s = ' '.join(str(x) for x in a)
    LOG.append(s)
    print('WC', s, flush=True)


# ----------------------------------------------------------------------------------------------- ownership
OWNED_RE = [r'^NB_lime_clast_specimen', r'^NB_core4_sequence_', r'^R8_(calcium_step2|crack_step1|crack_step2|healed_step3|water_step1)$',
            r'^D1_', r'^R1_healed_clast\d+$', r'^R1_lab_bench$', r'^R1_leak_', r'^R1_specimen_(healed|leaking)$',
            r'^R3_(healed_fill|leak_crack)$', r'^NB_modern_building$', r'^R1_frame_rust$', r'^R3_frame_crack_col2?$']
TOKEN_EXCEPT = {'RC.v12.base_water_process', 'RC.v12_5.crack_groove'}


def owned(name):
    return any(re.match(p, name) for p in OWNED_RE)


def fingerprint_foreign():
    fp = {}
    for o in bpy.data.objects:
        if owned(o.name):
            continue
        h = hashlib.sha1()
        h.update(np.array(o.matrix_world, np.float64).round(6).tobytes())
        h.update(str((o.hide_render, o.parent.name if o.parent else None, [c.name for c in o.users_collection])).encode())
        if o.type == 'MESH':
            me = o.data
            co = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get('co', co)
            lp = np.empty(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', lp)
            h.update(co.tobytes()); h.update(lp.tobytes())
            for s in o.material_slots:
                m = s.material
                h.update((m.name if m else 'None').encode())
                if m is not None and m.name not in TOKEN_EXCEPT:
                    h.update(np.array(m.diffuse_color, np.float32).tobytes())
        fp[o.name] = h.hexdigest()
    return fp


# ----------------------------------------------------------------------------------------------- colour helpers
def hex_lin(hx):
    hx = hx.lstrip('#')
    out = []
    for i in (0, 2, 4):
        c = int(hx[i:i + 2], 16) / 255.0
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return out


def set_mat_hex(m, hx):
    lin = hex_lin(hx)
    m.diffuse_color = (*lin, 1.0)
    if m.use_nodes and m.node_tree:
        for n in m.node_tree.nodes:
            if n.type == 'BSDF_PRINCIPLED':
                n.inputs['Base Color'].default_value = (*lin, 1.0)


def mat_copy(src, name, hx):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials[src].copy()
        m.name = name
    set_mat_hex(m, hx)
    return m


def set_single_material(o, m):
    o.data.materials.clear()
    o.data.materials.append(m)
    for s in o.material_slots:
        s.material = m


# ----------------------------------------------------------------------------------------------- data helpers
def need(n):
    o = bpy.data.objects.get(n)
    if o is None:
        raise RuntimeError(f'WC step: object {n!r} missing')
    return o


def src_store(o, extra=None):
    """store the v8_14 source state once; return it (dict)."""
    if 'wc_src' in o.keys():
        return json.loads(o['wc_src'])
    d = {'mw': [list(r) for r in o.matrix_world], 'loc': list(o.location), 'rot': list(o.rotation_euler),
         'scale': list(o.scale), 'mpi': [list(r) for r in o.matrix_parent_inverse],
         'parent': o.parent.name if o.parent else None}
    if o.type == 'MESH':
        d['co'] = [list(v.co) for v in o.data.vertices]
        d['mats'] = [s.material.name if s.material else None for s in o.material_slots]
    if extra:
        d.update(extra)
    o['wc_src'] = json.dumps(d)
    return d


def write_mesh(o, verts, faces, smooth=False, sharp_angle=None):
    me = o.data
    bm = bmesh.new()
    vs = [bm.verts.new(Vector(v)) for v in verts]
    for f in faces:
        bm.faces.new([vs[i] for i in f])
    for f in bm.faces:
        f.smooth = smooth
    if sharp_angle is not None:
        for e in bm.edges:
            if len(e.link_faces) == 2 and e.calc_face_angle(0.0) > sharp_angle:
                e.smooth = False
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    me.update()
    return me


def new_mesh_object(name, like):
    o = bpy.data.objects.get(name)
    if o is None:
        me = bpy.data.meshes.new(name)
        o = bpy.data.objects.new(name, me)
        for c in like.users_collection:
            c.objects.link(o)
    return o


def frame_from_normal(n, ref):
    z = Vector(n).normalized()
    x = Vector(ref) - z * Vector(ref).dot(z)
    if x.length < 1e-6:
        x = Vector((1, 0, 0)) - z * z.x
    x.normalize()
    y = z.cross(x)
    return x, y, z


def lump_geometry(a, b, c, seed, amp=0.15, freq=1.7, subdiv=2, lobe=1.0):
    """irregular lime lump spanning about [-a,a] x [-b,b] x [-c,c]: two or three overlapping noisy ellipsoids
    (a bilobed / knobbly outline, not a sphere). Local frame, z = surface normal."""
    rng = np.random.default_rng(seed)
    flip = 1 if rng.random() < 0.5 else -1
    k = lobe          # 1 = clearly bilobed outline, 0 = single noisy ellipsoid
    lobes = [((-0.36 * a * k, -0.08 * b * flip * k, 0.0), ((1 - 0.36 * k) * a, (1 - 0.14 * k) * b, c)),
             ((0.40 * a * k, 0.14 * b * flip * k, -0.05 * c), ((1 - 0.40 * k) * a, (1 - 0.32 * k) * b, 0.86 * c))]
    if rng.random() < 0.6:
        lobes.append(((0.02 * a, -0.50 * b * flip * k, -0.1 * c), (0.36 * a, 0.42 * b, 0.7 * c)))
    verts, faces = [], []
    for li, (ctr, rad) in enumerate(lobes):
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=1.0)
        off = Vector((seed * 7.31 + li * 1.9, seed * 3.17 - li * 2.3, seed * 5.53 + li * 0.7))
        base = len(verts)
        for v in bm.verts:
            p = v.co.normalized()
            r = 1.0 + amp * noise.noise(p * freq + off)
            q = p * r
            verts.append((ctr[0] + q.x * rad[0], ctr[1] + q.y * rad[1], ctr[2] + q.z * rad[2]))
        faces += [[base + v.index for v in f.verts] for f in bm.faces]
        bm.free()
    return verts, faces


def place_lump(o, center, frame, axes, seed, parent=None, amp=0.15, lobe=1.0):
    x, y, z = frame
    verts, faces = lump_geometry(*axes, seed=seed, amp=amp, lobe=lobe)
    R = Matrix((x, y, z)).transposed()
    world = [center + R @ Vector(v) for v in verts]
    o.parent = None
    o.matrix_world = Matrix.Translation(center)
    write_mesh(o, [tuple(w - center) for w in world], faces, smooth=True)
    if parent is not None:
        mw = o.matrix_world.copy()
        o.parent = parent
        o.matrix_parent_inverse = Matrix.Identity(4)
        o.matrix_world = mw


def ribbon(points, width, miter_limit=3.0):
    """points: list of 2D Vectors; returns (left, right) offset lists with mitred joins (square end caps)."""
    P = [Vector(p) for p in points]
    hw = width / 2
    L, Rr = [], []
    for i in range(len(P)):
        if i == 0:
            d = (P[1] - P[0]).normalized(); nrm = Vector((-d.y, d.x)); off = nrm * hw
        elif i == len(P) - 1:
            d = (P[-1] - P[-2]).normalized(); nrm = Vector((-d.y, d.x)); off = nrm * hw
        else:
            d0 = (P[i] - P[i - 1]).normalized(); d1 = (P[i + 1] - P[i]).normalized()
            n0 = Vector((-d0.y, d0.x)); n1 = Vector((-d1.y, d1.x))
            m = (n0 + n1)
            if m.length < 1e-6:
                m = n0
            m.normalize()
            cosang = max(m.dot(n0), 1.0 / miter_limit)
            off = m * (hw / cosang)
        L.append(P[i] + off); Rr.append(P[i] - off)
    return L, Rr


def ribbon_mesh(points, width, to3d, subdiv=1, front=None):
    """flat ribbon along a 2D polyline mapped by to3d(u,v)->Vector. subdiv: extra points per segment (for curved hosts)."""
    pts = []
    for i in range(len(points) - 1):
        a, b = Vector(points[i]), Vector(points[i + 1])
        for k in range(subdiv):
            pts.append(a.lerp(b, k / subdiv))
    pts.append(Vector(points[-1]))
    # keep the mitre only at the original corners: rebuild offsets per original segment direction
    L, Rr = ribbon(pts, width)
    verts = [to3d(p) for p in L] + [to3d(p) for p in Rr]
    n = len(pts)
    faces = [[i, i + 1, n + i + 1, n + i] for i in range(n - 1)]
    if front is not None:   # face the camera side of the host (Workbench shades back faces dark)
        a, b, c = verts[faces[0][0]], verts[faces[0][1]], verts[faces[0][2]]
        if (b - a).cross(c - a).dot(Vector(front)) < 0:
            faces = [f[::-1] for f in faces]
    return verts, faces


# ----------------------------------------------------------------------------------------------- main parts
WATER_HEX = '#54C0CF'   # Oklch 0.75/0.10/207.7: same hue as v12 water (#3F9DAA), lighter (CVD + in-groove water)
CRACK_HEX = '#3E332C'   # Oklch 0.33/0.02/54: print-safe groove (rendered L* ~17-19 instead of 7-15)
LAB_BENCH_HEX = '#6C7E81'  # Oklch 0.58/0.022/209: modern slate (K9), darker than the lighter water puddle
LIT_NORMAL = (0.45, -0.55, 0.70)  # custom normal for flat film strips: brightest studio-light direction (probe_normals2)


def part_tokens():
    water = bpy.data.materials['RC.v12.base_water_process']
    set_mat_hex(water, WATER_HEX)
    crack = bpy.data.materials['RC.v12_5.crack_groove']
    set_mat_hex(crack, CRACK_HEX)
    users = [o.name for o in bpy.data.objects if o.type == 'MESH' and any(s.material == crack for s in o.material_slots)]
    bad = [u for u in users if not owned(u)]
    if bad:
        raise RuntimeError(f'crack token used by non-WC objects {bad}')
    log('tokens: water', WATER_HEX, 'crack', CRACK_HEX, '(crack users all WC:', users, ')')


# ---------------------------------------------------------------- ③ lime clast specimen
C3_GRAINS = [  # (pt x, pt y, major extent BU, aspect a/b, angle deg in face, face, lobe)
    # face short sides: -y 7.555 (cap 0.755), +x 5.285 (cap 0.53), top 5.285 (cap 0.53). Every clast >= 3pt on screen
    # (OBJ_VALUE-20); on -y one large + three small clasts give CV >= 0.30; top and +x carry one off-centre clast each.
    (458.5, 1163.5, 0.52, 1.5, -25, 'top', 1.0),   # top face, at the block's top-left salient corner
    (458.5, 1243.0, 0.46, 1.3, 25, '-y', 1.0),     # lower-left salient corner
    (493.0, 1203.0, 0.75, 1.05, -30, '-y', 0.3),   # largest clast (9.9% of the face short side)
    (508.0, 1250.0, 0.46, 1.3, 35, '-y', 1.0),
    (462.0, 1200.0, 0.46, 1.3, 10, '-y', 1.0),
    (539.0, 1200.0, 0.52, 1.4, 60, '+x', 1.0),
]


def part_core3(S):
    sp = need('NB_lime_clast_specimen')
    dg = bpy.context.evaluated_depsgraph_get()
    ev = sp.evaluated_get(dg); me = ev.to_mesh(); mw = sp.matrix_world
    bvh = BVHTree.FromPolygons([mw @ v.co for v in me.vertices], [list(p.vertices) for p in me.polygons])
    ev.to_mesh_clear()
    mat = bpy.data.materials['RC.v12.base_lime_calcium_crystal']
    like = need('NB_lime_clast_specimen_LIME00')
    Wsp = world_verts(sp); mn, mx = Wsp.min(0), Wsp.max(0)
    log('core3: -y top edge pt', [tuple(np.round(S.to_pt(Vector(p)), 1)) for p in ((mn[0], mn[1], mx[2]), (mx[0], mn[1], mx[2]), (mx[0], mn[1], mn[2]), (mn[0], mn[1], mn[2]))])
    for i, (px, py, d, asp, ang, face, lobe) in enumerate(C3_GRAINS):
        name = f'NB_lime_clast_specimen_LIME{i:02d}'
        o = bpy.data.objects.get(name) or new_mesh_object(name, like)
        if o.type == 'MESH':
            src_store(o)
        hits, nrms = [], []
        for dx, dy in [(0, 0), (-1.2, 0), (1.2, 0), (0, -1.2), (0, 1.2)]:
            org, dirv = S.ray((px + dx, py + dy))
            h = bvh.ray_cast(org, dirv)
            if h[0] is None:
                raise RuntimeError(f'core3 grain {i}: ray missed specimen at {(px + dx, py + dy)}')
            hits.append(h[0]); nrms.append(h[1])
        p = hits[0]
        n = sum(nrms, Vector()).normalized()
        want = {'-y': Vector((0, -1, 0)), '+x': Vector((1, 0, 0)), 'top': Vector((0, 0, 1))}[face]
        if n.dot(want) < 0.6:
            log(f'core3 grain {i}: normal {tuple(round(c, 2) for c in n)} not on face {face}; snapping toward face')
        n = (n * 0.5 + want * 0.5).normalized()
        # in-face reference direction: face horizontal (screen-right component) rotated by ang
        href = Vector((0, 1, 0)) if face == '+x' else Vector((1, 0, 0))
        x, y, z = frame_from_normal(n, href)
        t = math.radians(ang)
        x2 = x * math.cos(t) + y * math.sin(t); y2 = z.cross(x2)
        a = d / 2; b = a / asp; c = 0.62 * a
        place_lump(o, p + n * (0.20 * c), (x2, y2, n), (a, b, c), seed=31 + i, parent=sp, lobe=lobe)
        set_single_material(o, mat)
        o.hide_render = False
    for o in bpy.data.objects:
        m = re.match(r'^NB_lime_clast_specimen_LIME(\d+)$', o.name)
        if m and int(m.group(1)) >= len(C3_GRAINS):
            o.hide_render = True
    log('core3: grains', len(C3_GRAINS), 'rebuilt as irregular lumps')


# ---------------------------------------------------------------- ④ three cubes
C4_SHIFT_PT = 21.0          # coordinator: cube group exactly 21.0pt up on screen
C4_GRAIN = [0.355, 0.26]    # step1 / step2 grain major diameters (BU, side 3.588 -> 9.9% / 7.2%)
C4_DROP_TOP_PT = 1164.0     # pre-shift screen y of the topmost droplet tip (post-shift 1143.0 -> d_own 14.5 <= 0.5*33.5)


def cubes_from_gray03(g3):
    me = g3.data
    bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    comp = [-1] * len(bm.verts); c = 0
    for v in bm.verts:
        if comp[v.index] >= 0:
            continue
        st = [v]; comp[v.index] = c
        while st:
            u = st.pop()
            for e in u.link_edges:
                w = e.other_vert(u)
                if comp[w.index] < 0:
                    comp[w.index] = c; st.append(w)
        c += 1
    bm.free()
    Wv = world_verts(g3); comp = np.array(comp)
    cubes = []
    for k in range(c):
        P = Wv[comp == k]
        mn, mx = P.min(0), P.max(0)
        face = P[np.abs(P[:, 1] - mn[1]) < 1e-4]        # -y face plane verts -> flat region
        cubes.append({'min': mn, 'max': mx, 's': float(mx[0] - mn[0]),
                      'flat_u': (float(face[:, 0].min() - mn[0]), float(face[:, 0].max() - mn[0])),
                      'flat_v': (float(face[:, 2].min() - mn[2]), float(face[:, 2].max() - mn[2]))})
    cubes.sort(key=lambda d: d['min'][0])
    return cubes


def crack_polyline(src_co, ymin, zmin, s):
    """centreline (u,v) of the v8_14 step-1 crack (+x face quads, 4 verts each) in face units."""
    Q = np.array(src_co)
    pts = []
    for q in range(len(Q) // 4):
        a, b, c, d = Q[4 * q:4 * q + 4]
        A = (a + d) / 2; B = (b + c) / 2
        pts.append((A, B))
    poly = [pts[0][0]]
    for i in range(len(pts) - 1):
        poly.append((pts[i][1] + pts[i + 1][0]) / 2)
    poly.append(pts[-1][1])
    return [((p[1] - ymin) / s, (p[2] - zmin) / s) for p in poly]


def part_core4(S):
    par = need('NB_core4_sequence')
    kids = [need(n) for n in ('NB_core4_sequence_GRAY00', 'NB_core4_sequence_GRAY01', 'NB_core4_sequence_GRAY02',
                              'NB_core4_sequence_GRAY03', 'NB_core4_sequence_GRAY04')]
    srcs = {k.name: src_store(k) for k in kids}
    r8 = {n: need(n) for n in ('R8_crack_step1', 'R8_crack_step2', 'R8_water_step1', 'R8_calcium_step2', 'R8_healed_step3')}
    r8src = {n: src_store(o) for n, o in r8.items()}
    # 1) restore children to source, measure the exact screen shift per world z, move children (not the empty) up
    for k in kids:
        k.location = srcs[k.name]['loc']
    bpy.context.view_layer.update()
    g3 = kids[3]
    cubes0 = cubes_from_gray03(g3)
    corners = []
    for cb in cubes0:
        for x in (cb['min'][0], cb['max'][0]):
            for y in (cb['min'][1], cb['max'][1]):
                for z in (cb['min'][2], cb['max'][2]):
                    corners.append((x, y, z))
    C = np.array(corners)
    p0 = S.project(C); p1 = S.project(C + np.array([0, 0, 1.0]))
    dy_per = (p1[:, 1] - p0[:, 1]).mean()
    dz = -C4_SHIFT_PT / dy_per
    sc = par.matrix_world.to_scale()[2]
    for k in kids:
        loc = Vector(srcs[k.name]['loc']); loc.z += dz / sc
        k.location = loc
    bpy.context.view_layer.update()
    p2 = S.project(C + np.array([0, 0, dz]))
    sh = p2 - p0
    log('core4: world dz %.4f -> screen shift x %.3f..%.3f y %.3f..%.3f pt' % (dz, sh[:, 0].min(), sh[:, 0].max(), sh[:, 1].min(), sh[:, 1].max()))
    cubes = cubes_from_gray03(g3)
    # 2) crack centreline (v8_14 step-1 crack lived on cube 0's +x face; rotated -90deg about the cube axis -> -y face, same u)
    src_cube0 = cubes0[0]
    poly = crack_polyline(r8src['R8_crack_step1']['co'], src_cube0['min'][1], src_cube0['min'][2], src_cube0['s'])
    fv1 = src_cube0['flat_v'][1] / src_cube0['s']
    poly[0] = (poly[0][0], fv1)                     # the groove opens on the top edge (water entrance)
    log('core4: crack polyline (u,v)', [(round(u, 3), round(v, 3)) for u, v in poly])
    W_CRACK, W_FILL = 0.30, 0.31                    # D28: 2.5pt groove / 2.6pt fill on screen (flat strips on the -y face)

    def face_map(cb, off):
        s = cb['s']; mn = cb['min']
        return lambda p: Vector((mn[0] + p[0] * s, mn[1] - off, mn[2] + p[1] * s))

    def strip(o, cb, pts, width, off, mat, up_normals=False):
        o.parent = None
        o.matrix_world = Matrix.Identity(4)
        verts, faces = ribbon_mesh(pts, width / cb['s'], face_map(cb, off), front=(0, -1, 0))
        me = write_mesh(o, [tuple(v) for v in verts], faces)
        if up_normals:   # film strips (water / calcite): lit like a wet, light-catching film (same token, no new colour)
            me.normals_split_custom_set([LIT_NORMAL] * len(me.loops))
        set_single_material(o, mat)

    crack_m = bpy.data.materials['RC.v12_5.crack_groove']
    water_m = bpy.data.materials['RC.v12.base_water_process']
    lime_m = bpy.data.materials['RC.v12.base_lime_calcium_crystal']
    gi = 1                                           # grain sits on the upper bend (polyline point 1)
    strip(r8['R8_crack_step1'], cubes[0], poly, W_CRACK, 0.04, crack_m)
    strip(r8['R8_crack_step2'], cubes[1], poly, W_CRACK, 0.04, crack_m)
    strip(r8['R8_water_step1'], cubes[0], poly[:gi + 1], W_CRACK, 0.075, water_m, up_normals=True)
    strip(r8['R8_calcium_step2'], cubes[1], poly[gi:gi + 3], W_CRACK * 0.62, 0.075, lime_m, up_normals=True)
    strip(r8['R8_healed_step3'], cubes[2], poly, W_FILL, 0.04, lime_m, up_normals=True)
    # 3) grains (GRAY02, one mesh, two lumps) on the bend, steps 1 and 2
    g2 = kids[2]
    gverts, gfaces = [], []
    Mi = g2.matrix_world.inverted()
    for k, dmaj in enumerate(C4_GRAIN):
        cb = cubes[k]
        u, v = poly[gi]
        a = dmaj / 2; b = a / 1.5; c = 0.6 * a
        ctr = face_map(cb, 0.085)((u, v))            # in front of the groove / water / calcite strips
        x, y, z = frame_from_normal(Vector((0, -1, 0)), Vector((1, 0, 0)))
        t = math.radians(28 + 40 * k)
        x2 = x * math.cos(t) + y * math.sin(t); y2 = z.cross(x2)
        vv, ff = lump_geometry(a, b, c, seed=71 + k)
        R = Matrix((x2, y2, z)).transposed()
        base = len(gverts)
        gverts += [tuple(Mi @ (ctr + R @ Vector(p))) for p in vv]
        gfaces += [[base + i for i in f] for f in ff]
    write_mesh(g2, gverts, gfaces, smooth=True)
    set_single_material(g2, lime_m)
    # 4) droplets (GRAY04): teardrops in a vertical column above the entrance of cube 0
    g4 = kids[4]
    cb = cubes[0]
    E = face_map(cb, 0.0)(poly[0])
    Ept = S.to_pt(E)
    r = 0.165
    drops = []
    # find z for bottom drop so its lowest point is 2.6pt above the entrance; top tip at C4_DROP_TOP_PT - dshift
    top_target = C4_DROP_TOP_PT - C4_SHIFT_PT

    def zpt(z):
        return S.to_pt(Vector((E.x, E.y - 0.20, z)))[1]
    lo, hi = E.z, E.z + 8
    for _ in range(60):
        m = (lo + hi) / 2
        if zpt(m - r) > Ept[1] - 2.6:
            lo = m
        else:
            hi = m
    z_bot = (lo + hi) / 2
    lo, hi = E.z, E.z + 12
    for _ in range(60):
        m = (lo + hi) / 2
        if zpt(m + 1.7 * r) > top_target:
            lo = m
        else:
            hi = m
    z_top = (lo + hi) / 2
    n_drops = 4
    dverts, dfaces = [], []
    Mi4 = g4.matrix_world.inverted()
    prof = [(0.0, -1.0)] + [(math.sin(t), -math.cos(t)) for t in np.linspace(0.25, math.pi / 2, 6)] + \
           [((1 - q) ** 1.35, 1.7 * q) for q in np.linspace(0.15, 0.85, 6)] + [(0.0, 1.7)]
    nseg = 14
    for i in range(n_drops):
        zc = z_bot + (z_top - z_bot) * i / (n_drops - 1)
        ctr = Vector((E.x, E.y - 0.20, zc))
        base = len(dverts)
        ring_idx = []
        for j, (rr, zz) in enumerate(prof):
            if rr < 1e-6:
                ring_idx.append([len(dverts)]); dverts.append(tuple(Mi4 @ (ctr + Vector((0, 0, zz * r)))))
            else:
                ids = []
                for kk in range(nseg):
                    t = 2 * math.pi * kk / nseg
                    ids.append(len(dverts)); dverts.append(tuple(Mi4 @ (ctr + Vector((rr * r * math.cos(t), rr * r * math.sin(t), zz * r)))))
                ring_idx.append(ids)
        for j in range(len(ring_idx) - 1):
            A, B = ring_idx[j], ring_idx[j + 1]
            if len(A) == 1:
                for kk in range(nseg):
                    dfaces.append([A[0], B[(kk + 1) % nseg], B[kk]])
            elif len(B) == 1:
                for kk in range(nseg):
                    dfaces.append([A[kk], A[(kk + 1) % nseg], B[0]])
            else:
                for kk in range(nseg):
                    dfaces.append([A[kk], A[(kk + 1) % nseg], B[(kk + 1) % nseg], B[kk]])
    write_mesh(g4, dverts, dfaces, smooth=True)
    set_single_material(g4, water_m)
    log('core4: entrance pt', tuple(round(c, 1) for c in Ept), 'drops z', round(z_bot, 3), '..', round(z_top, 3))


# ---------------------------------------------------------------- ⑤ lab specimens
C5_GRAINS = {'R1_healed_clast0': (0.74, 1.1, 15, 0.3), 'R1_healed_clast1': (0.45, 1.25, -25, 0.9), 'R1_healed_clast2': (0.45, 1.25, 40, 0.9)}


def cyl_axis(o):
    W = world_verts(o)
    return Vector(((W[:, 0].min() + W[:, 0].max()) / 2, (W[:, 1].min() + W[:, 1].max()) / 2)), \
        (W[:, 0].max() - W[:, 0].min()) / 2, W[:, 2].min(), W[:, 2].max()


def part_core5(S):
    matrix = bpy.data.materials['RC.v12.base_lime_specimen_matrix']
    lime_m = bpy.data.materials['RC.v12.base_lime_calcium_crystal']
    crack_m = bpy.data.materials['RC.v12_5.crack_groove']
    for n in ('R1_specimen_healed', 'R1_specimen_leaking'):
        o = need(n); src_store(o)
        set_single_material(o, matrix)
        # side normals horizontal: cap rims sharp (removes the top-to-bottom darkening of smooth caps)
        bm = bmesh.new(); bm.from_mesh(o.data)
        for f in bm.faces:
            f.smooth = abs(f.normal.z) < 0.5
        for e in bm.edges:
            if len(e.link_faces) == 2:
                e.smooth = not (e.calc_face_angle(0.0) > math.radians(50))
        bm.to_mesh(o.data); bm.free(); o.data.update()
    bench = need('R1_lab_bench'); src_store(bench)
    bm_ = mat_copy('RC.v12.labstone', 'RC.v12_wc.lab_bench', LAB_BENCH_HEX)
    set_single_material(bench, bm_)
    for strip_name, host_name, mat in (('R3_leak_crack', 'R1_specimen_leaking', crack_m), ('R3_healed_fill', 'R1_specimen_healed', lime_m)):
        o = need(strip_name); src = src_store(o)
        host = need(host_name)
        ax, R, z0, z1 = cyl_axis(host)
        Q = np.array(src['co'])
        cl = [(Q[2 * i] + Q[2 * i + 1]) / 2 for i in range(len(Q) // 2)]
        width = float(np.mean([np.linalg.norm(Q[2 * i] - Q[2 * i + 1]) for i in range(len(Q) // 2)]))
        Rout = R + 0.03
        pts = []
        for p in cl:
            th = math.atan2(p[1] - ax.y, p[0] - ax.x)
            pts.append((th * Rout, p[2]))
        to3d = lambda q: Vector((ax.x + Rout * math.cos(q[0] / Rout), ax.y + Rout * math.sin(q[0] / Rout), q[1]))
        o.parent = None; o.matrix_world = Matrix.Identity(4)
        mid_th = pts[len(pts) // 2][0] / Rout
        verts, faces = ribbon_mesh(pts, width, to3d, subdiv=8, front=(math.cos(mid_th), math.sin(mid_th), 0))
        me = write_mesh(o, [tuple(v) for v in verts], faces, smooth=True)
        if mat is lime_m:
            me.normals_split_custom_set([LIT_NORMAL] * len(me.loops))
        set_single_material(o, mat)
        log(f'core5: {strip_name} rebuilt on r={Rout:.4f} (host R {R:.4f}), width {width:.3f}')
    host = need('R1_specimen_healed'); ax, R, z0, z1 = cyl_axis(host)
    for i, (n, (d, asp, ang, lobe)) in enumerate(C5_GRAINS.items()):
        o = need(n); src = src_store(o)
        c0 = Vector((src['mw'][0][3], src['mw'][1][3], src['mw'][2][3]))
        th = math.atan2(c0.y - ax.y, c0.x - ax.x)
        nrm = Vector((math.cos(th), math.sin(th), 0))
        a = d / 2; b = a / asp; c = 0.95 * a
        ctr = Vector((ax.x, ax.y, c0.z)) + nrm * (R + 0.5 * c)
        x, y, z = frame_from_normal(nrm, Vector((0, 0, 1)))
        t = math.radians(ang)
        x2 = x * math.cos(t) + y * math.sin(t); y2 = z.cross(x2)
        o.scale = (1, 1, 1); o.rotation_euler = (0, 0, 0)
        place_lump(o, ctr, (x2, y2, nrm), (a, b, c), seed=91 + i, lobe=lobe)
        set_single_material(o, lime_m)
    log('core5: specimens -> RCONC token, grains', list(C5_GRAINS))


# ---------------------------------------------------------------- D1 seawater tank
D1_MOVE = {  # top-face crystals -> wet side faces, band just above the water line (local z of D1_material)
    'D1_crystal01': ('-y', -0.50, 0.80, 25, -15), 'D1_crystal05': ('-y', -0.22, 0.88, 40, 10),
    'D1_crystal13': ('-y', 0.05, 0.79, 22, 12), 'D1_crystal20': ('-y', 0.24, 0.90, 30, -8),
    'D1_crystal07': ('+x', -0.52, 0.82, 26, 10), 'D1_crystal15': ('+x', -0.20, 0.90, 34, -12),
    'D1_crystal17': ('+x', 0.12, 0.80, 22, 8), 'D1_crystal25': ('+x', 0.40, 0.88, 30, -6),
}
D1_WALL_INNER = 0.865   # inner wall faces (was 1.08): visible water band 0.43 -> 0.215


def part_d1():
    tank_m = mat_copy('RC.v12.base_modern_concrete', 'RC.v12_wc.d1_tank', '#6E7980')
    for n in ('D1_tank_floor', 'D1_tank_wall0', 'D1_tank_wall1', 'D1_tank_wall2', 'D1_tank_wall3'):
        o = need(n); src = src_store(o)
        set_single_material(o, tank_m)
        if n == 'D1_tank_floor':
            continue
        axis = 1 if n in ('D1_tank_wall0', 'D1_tank_wall1') else 0
        sign = 1 if n in ('D1_tank_wall0', 'D1_tank_wall2') else -1
        outer = 1.2
        half = (outer - D1_WALL_INNER) / 2
        loc = list(src['loc']); loc[axis] = sign * (outer + D1_WALL_INNER) / 2
        o.location = loc
        co = np.array(src['co']); old_half = np.abs(co[:, axis]).max()
        co[:, axis] = co[:, axis] / old_half * half
        for v, c in zip(o.data.vertices, co):
            v.co = Vector(c)
        o.data.update()
    for n, (face, t, z, tilt, yaw) in D1_MOVE.items():
        o = need(n); src = src_store(o)
        co = np.array(src['co'])
        cent = co.mean(0)
        r = np.linalg.norm(co - cent, axis=1)
        # base ring = 6 verts farther from the axis; axis from the two ring centroids
        # decide rings by alternate indices (topology: even = one end, odd = other)
        e0, e1 = co[0::2], co[1::2]
        rad0 = np.linalg.norm(e0 - e0.mean(0), axis=1).mean(); rad1 = np.linalg.norm(e1 - e1.mean(0), axis=1).mean()
        base, tip = (e0, e1) if rad0 > rad1 else (e1, e0)
        rb, rt = max(rad0, rad1), min(rad0, rad1)
        length = float(np.linalg.norm(tip.mean(0) - base.mean(0)))
        if face == '-y':
            nrm = Vector((0, -1, 0)); p = Vector((t, -0.65 + 0.012, z))
            side = Vector((1, 0, 0))
        else:
            nrm = Vector((1, 0, 0)); p = Vector((0.65 - 0.012, t, z))
            side = Vector((0, 1, 0))
        d = (nrm * math.cos(math.radians(tilt)) + Vector((0, 0, 1)) * math.sin(math.radians(tilt)))
        d = (Matrix.Rotation(math.radians(yaw), 3, 'Z') @ d).normalized()
        x, y, zz = frame_from_normal(d, side)
        mid = p + d * (length / 2)
        verts = []
        for i in range(12):
            k = i // 2; ang = 2 * math.pi * k / 6
            rr, h = (rb, -length / 2) if (i % 2 == 0) == (rad0 > rad1) else (rt, length / 2)
            q = d * h + (x * math.cos(ang) + y * math.sin(ang)) * rr
            verts.append(q)
        o.location = mid
        for v, q in zip(o.data.vertices, verts):
            v.co = q
        bm = bmesh.new(); bm.from_mesh(o.data)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(o.data); bm.free(); o.data.update()
    log('D1: tank walls inner faces ->', D1_WALL_INNER, '; tank colour #6E7980; moved crystals', list(D1_MOVE))


# ---------------------------------------------------------------- ① modern building
C1_OBJS = ('NB_modern_building', 'R1_frame_rust', 'R3_frame_crack_col', 'R3_frame_crack_col2')
C1_SCALE = 0.95
C1_LEFT_PT = 697.5      # target screen x of the building's left end (text 790:146-148 ink right 678.5 -> 19pt)


def part_core1(S):
    objs = [need(n) for n in C1_OBJS]
    srcs = [src_store(o) for o in objs]
    M0 = [Matrix(s['mw']) for s in srcs]
    for o, m in zip(objs, M0):
        o.parent = None; o.matrix_world = m
    bpy.context.view_layer.update()
    nb = objs[0]
    W0 = world_verts(nb)
    zmin = W0[:, 2].min()
    base = W0[W0[:, 2] < zmin + 0.6]
    c = Vector((float((W0[:, 0].min() + W0[:, 0].max()) / 2), float((W0[:, 1].min() + W0[:, 1].max()) / 2), float(zmin)))
    Sc = Matrix.Translation(c) @ Matrix.Scale(C1_SCALE, 4) @ Matrix.Translation(-c)
    # screen-left move along the screen-right world vector (depth unchanged)
    Wall = np.vstack([world_verts(o) for o in objs])
    Ws = (np.array(Sc) @ np.c_[Wall, np.ones(len(Wall))].T).T[:, :3]
    left = S.project(Ws)[:, 0].min()
    right_w = Vector((1, 1, 0)).normalized()
    lo, hi = -8.0, 4.0
    for _ in range(60):
        m = (lo + hi) / 2
        Wm = Ws + np.array(right_w * m)
        if S.project(Wm)[:, 0].min() > C1_LEFT_PT:
            hi = m
        else:
            lo = m
    shift = right_w * ((lo + hi) / 2)
    T = Matrix.Translation(shift) @ Sc
    # re-seat on the terrain: front bottom edges (camera side: y-min edge and x-max edge) sampled every 0.25
    land = need('T_land'); terr = Terrain(land)
    Wb = (np.array(T) @ np.c_[W0, np.ones(len(W0))].T).T[:, :3]
    zb = Wb[:, 2].min()
    x0, x1 = Wb[:, 0].min(), Wb[:, 0].max(); y0, y1 = Wb[:, 1].min(), Wb[:, 1].max()
    bvh_b = BVHTree.FromPolygons([Vector(v) for v in Wb], [list(p.vertices) for p in nb.data.polygons])
    gaps = []
    for (px, py) in [(x, y0 + 0.15) for x in np.linspace(x0 + 0.15, x1 - 0.15, 40)] + [(x1 - 0.15, y) for y in np.linspace(y0 + 0.15, y1 - 0.15, 40)]:
        h = bvh_b.ray_cast(Vector((px, py, zb - 5)), Vector((0, 0, 1)))
        if h[0] is None or h[0].z > zb + 0.8:
            continue
        gaps.append(h[0].z - terr.z(px, py))
    gaps = np.array(gaps)
    dz = -float(np.max(gaps)) + 0.03            # max visible gap 0.03 BU (0.26pt <= 0.41); burial <= spread-0.03 (<1pt)
    T = Matrix.Translation((0, 0, dz)) @ T
    for o, m in zip(objs, M0):
        o.matrix_world = T @ m
    bpy.context.view_layer.update()
    log('core1: scale %.2f about %s, shift %s, dz %.3f; edge gaps before dz: min %.3f max %.3f (n %d) -> burial max %.3f BU'
        % (C1_SCALE, tuple(round(v, 2) for v in c), tuple(round(v, 3) for v in shift), dz, gaps.min(), gaps.max(), len(gaps),
           float(np.max(gaps) - np.min(gaps)) - 0.03))


# ----------------------------------------------------------------------------------------------- driver
def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    if not argv:
        raise SystemExit(__doc__)
    out = Path(argv[0]).resolve()
    src = Path(bpy.data.filepath).resolve()
    if out == src or out.parent == (NB / 'out').resolve():
        raise SystemExit(f'refusing to write {out} (input or $W/out)')
    S = Screen()
    fp0 = fingerprint_foreign()
    part_tokens()
    part_core1(S)
    part_core3(S)
    part_core4(S)
    part_core5(S)
    part_d1()
    bpy.context.view_layer.update()
    fp1 = fingerprint_foreign()
    diff = [n for n in fp0 if fp0[n] != fp1.get(n)] + [n for n in fp1 if n not in fp0]
    if diff:
        raise RuntimeError(f'foreign objects changed: {diff[:20]}')
    log('ownership check: %d foreign objects unchanged' % len(fp0))
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(out), compress=True, copy=False)
    log('saved', out)
    if len(argv) > 1:
        H = runpy.run_path(str(NB / 'scripts/integrate_assets.py'), run_name='helpers')
        r = H['render_two_pass'](Path(argv[1]).resolve().with_suffix('.png'))
        log('render', json.dumps(r))
    (out.parent / (out.stem + '_log.json')).write_text(json.dumps(LOG, ensure_ascii=False, indent=1))


main()
