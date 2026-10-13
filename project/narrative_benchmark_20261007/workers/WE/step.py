"""WE step (wave 1, worker WE: terrain, roads, bridges, fields, water) for the Roman-concrete A2 poster.

Run: Blender -b <in.blend> --factory-startup --python step.py -- <out.blend> [render_prefix]
  - refuses to write the input file, any existing file in out/ or a published out/ name, or a non-.blend path
  - with render_prefix: also renders integrate_assets.render_two_pass(<prefix>.png) (48 %, 2 px/pt)
Only the WE objects are changed (OWNED + the new paving-bed object). Before saving, every other object's mesh,
matrix, material slots and the colours of the materials they use are compared with the input; any difference
aborts the save.

Idempotent: the first run stores the original vertex positions of every WE mesh it reshapes in the point
attribute ORIG; any later run (on its own output) first restores those positions and recomputes everything from
them, so the result is the same. Deletions are decided from fixed criteria on the original geometry (a second run
finds nothing more to delete); the paving bed is rebuilt from scratch.

The fixes are listed in FIXES below (finding ids of review_loop/obj_r11/findings_by_asset.md).
"""
import bpy, bmesh, sys, json, math, re, hashlib, os, runpy, time
from pathlib import Path
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

HERE = Path(__file__).resolve().parent
NB = next((p for p in [HERE, *HERE.parents] if (p / 'scripts/integrate_assets.py').exists()), HERE.parents[1])
OUT_DIR = NB / 'out'
sys.path.insert(0, str(NB / 'workers/layout'))
from common import Screen, world_verts, map_visible_objects, overlay_objects   # noqa: E402

MARK = 'rc_we_wave1'
ORIG = 'rc_we_orig_co'
OWNED = ['T_land', 'R_core_road', 'R_via_appia', 'R1_road_landing1', 'R1_road_landing5', 'R1_road5_bed',
         'B_pons1', 'B_pons1_parapet0', 'B_pons1_parapet1', 'B_pons2', 'B_pons2_parapet0', 'B_pons2_parapet1',
         'R4_bridge_west_bed', 'F_centuriatio', 'L02_tiber', 'L10_sea', 'W_water_marks']
BED_NAME = 'R_we_paving_bed'
CREATED = [BED_NAME]
OWNED_SET = set(OWNED) | set(CREATED)
NOT_GROUND = {'T_land', 'L02_tiber', 'L10_sea', 'W_water_marks'}
FIELD_ATTR = 'rc_v12_13_field_role'
ROLE_VINE, ROLE_STRAW = 12, 13
STRAW_MIN = 0.495      # tallest pile 0.614 -> ratio 1.24 <= 1.25
KERB_MIN_FACES = 40          # workers/roads/step.py: < 40 faces = paving part, >= 40 = kerb ribbon
OPS = os.environ.get('WE_OPS', 'all')
REP = {}
T_START = time.time()


def on(op):
    return OPS == 'all' or op in OPS.split(',')


def log(k, v):
    REP[k] = v
    print(f'WE {k} [{time.time() - T_START:.0f}s]: ' + json.dumps(v, ensure_ascii=False, default=lambda x: x.tolist() if hasattr(x, 'tolist') else str(x))[:1500], flush=True)


def need(name):
    o = bpy.data.objects.get(name)
    if o is None or o.type != 'MESH':
        raise RuntimeError(f'WE step: mesh object {name!r} not found in {bpy.data.filepath}')
    return o


def own_mesh(o):
    if o.data.users > 1:
        o.data = o.data.copy()
    return o.data


def restore_or_snapshot(o):
    """first run: store the original local coordinates; later runs: put them back."""
    me = own_mesh(o)
    co = np.empty(len(me.vertices) * 3)
    a = me.attributes.get(ORIG)
    if a is not None and a.domain == 'POINT' and a.data_type == 'FLOAT_VECTOR':
        a.data.foreach_get('vector', co)
        me.vertices.foreach_set('co', co); me.update()
        return 'restored'
    if a is not None:
        me.attributes.remove(a)
    me.vertices.foreach_get('co', co)
    a = me.attributes.new(ORIG, 'FLOAT_VECTOR', 'POINT')
    a.data.foreach_set('vector', co)
    return 'snapshot'


def set_world_verts(o, W):
    Mi = np.array(o.matrix_world.inverted())
    co = (np.c_[W, np.ones(len(W))] @ Mi.T)[:, :3]
    o.data.vertices.foreach_set('co', co.ravel()); o.data.update()


def mesh_topo(o):
    me = o.data
    ls = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get('loop_start', ls)
    lt = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get('loop_total', lt)
    lv = np.empty(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', lv)
    E = np.empty(len(me.edges) * 2, np.int32); me.edges.foreach_get('vertices', E)
    return ls, lt, lv, E.reshape(-1, 2)


def vert_islands(nv, E):
    parent = np.arange(nv)

    def find(a):
        r = a
        while parent[r] != r:
            r = parent[r]
        while parent[a] != r:
            parent[a], a = r, parent[a]
        return r
    for a, b in E:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    roots = np.array([find(i) for i in range(nv)])
    _, lab = np.unique(roots, return_inverse=True)
    return lab


def islands(o):
    """(vertex island labels, face island labels, ls, lt, lv)"""
    ls, lt, lv, E = mesh_topo(o)
    lab = vert_islands(len(o.data.vertices), E)
    flab = lab[lv[ls]] if len(ls) else np.zeros(0, int)
    return lab, flab, ls, lt, lv


def bvh_from(objs, face_filter=None):
    dg = bpy.context.evaluated_depsgraph_get()
    verts, polys = [], []
    for o in objs:
        ev = o.evaluated_get(dg); me = ev.to_mesh()
        co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
        Wv = (np.c_[co, np.ones(len(co))] @ np.array(o.matrix_world).T)[:, :3]
        b = len(verts); verts.extend(map(tuple, Wv))
        keep = face_filter(o, me) if face_filter else None
        for p in me.polygons:
            if keep is None or keep[p.index]:
                polys.append([b + i for i in p.vertices])
        ev.to_mesh_clear()
    return BVHTree.FromPolygons(verts, polys) if polys else None


class Ground:
    """ray-down height queries on a BVH."""
    def __init__(self, bvh):
        self.bvh = bvh

    def z(self, x, y, top=60.0):
        h = self.bvh.ray_cast(Vector((x, y, top)), Vector((0, 0, -1)))[0]
        return h.z if h else float('nan')

    def zs(self, XY, top=60.0):
        return np.array([self.z(float(x), float(y), top) for x, y in XY])


def terrain():
    return Ground(bvh_from([need('T_land')]))


# ------------------------------------------------------------------ guards
def fingerprint(skip):
    fp = {}
    for o in bpy.data.objects:
        if o.name in skip:
            continue
        h = hashlib.sha1()
        h.update(np.array(o.matrix_world, np.float64).round(7).tobytes())
        if o.type == 'MESH':
            me = o.data
            co = np.empty(len(me.vertices) * 3, np.float64); me.vertices.foreach_get('co', co); h.update(co.round(6).tobytes())
            pv = np.empty(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', pv); h.update(pv.tobytes())
            mi = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', mi); h.update(mi.tobytes())
        for s in o.material_slots:
            m = s.material
            h.update(repr(m.name if m else None).encode())
            if m:
                h.update(np.array(m.diffuse_color).round(6).tobytes())
                if m.node_tree:
                    for n in m.node_tree.nodes:
                        if n.type == 'BSDF_PRINCIPLED':
                            h.update(np.array(n.inputs['Base Color'].default_value).round(6).tobytes())
        h.update(repr((o.hide_render, o.parent.name if o.parent else None, [(m.type, m.name) for m in getattr(o, 'modifiers', [])])).encode())
        fp[o.name] = h.hexdigest()
    return fp


# ------------------------------------------------------------------ fields (F_centuriatio)
class Fields:
    def __init__(self, S):
        self.S = S
        self.o = need('F_centuriatio')
        self.load()

    def load(self):
        o = self.o; me = o.data
        self.lab, self.flab, self.ls, self.lt, self.lv = islands(o)
        self.n = int(self.lab.max()) + 1 if len(self.lab) else 0
        role = np.zeros(len(me.polygons), np.int32)
        me.attributes[FIELD_ATTR].data.foreach_get('value', role)
        self.role = role
        cnt = np.zeros((self.n, 16), int)
        np.add.at(cnt, (self.flab, np.clip(role, 0, 15)), 1)
        ir = cnt.argmax(1)
        self.kind = np.where(ir == ROLE_STRAW, 'straw', np.where(ir == ROLE_VINE, 'vine', 'plate'))
        self.W = world_verts(o)
        self.P = self.S.project(self.W)
        self.cen = np.array([self.W[self.lab == k].mean(0) for k in range(self.n)])
        self.pcen = self.S.project(self.cen)

    def members(self, k):
        return np.nonzero(self.lab == k)[0]

    def islands_in(self, box, kinds=('plate',)):
        x0, x1, y0, y1 = box
        return [k for k in range(self.n) if self.kind[k] in kinds and x0 <= self.pcen[k, 0] <= x1 and y0 <= self.pcen[k, 1] <= y1]

    def props_on(self, plates, margin=0.05):
        """straw / vine islands whose centroid lies on the xy box of one of the plates."""
        out = []
        for k in range(self.n):
            if self.kind[k] == 'plate':
                continue
            c = self.cen[k]
            for p in plates:
                w = self.W[self.lab == p]
                if w[:, 0].min() - margin <= c[0] <= w[:, 0].max() + margin and w[:, 1].min() - margin <= c[1] <= w[:, 1].max() + margin:
                    out.append(k); break
        return out


def aqueduct_piers(T, max_above=1.3):
    """xy convex hulls of the L05_aqua_claudia blocks that reach down to the ground (pier bases)."""
    a = bpy.data.objects.get('L05_aqua_claudia')
    if a is None:
        return []
    lab, flab, ls, lt, lv = islands(a)
    W = world_verts(a)
    hulls = []
    for k in range(int(lab.max()) + 1):
        w = W[lab == k]
        c = w.mean(0)
        g = T.z(c[0], c[1])
        if not np.isfinite(g) or w[:, 2].min() > g + max_above:
            continue
        hulls.append(convex_hull(w[:, :2]))
    return hulls


def convex_hull(P):
    P = np.unique(np.round(P, 6), axis=0)
    if len(P) < 3:
        return P
    P = P[np.lexsort((P[:, 1], P[:, 0]))]

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for p in P:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(tuple(p))
    for p in P[::-1]:
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(tuple(p))
    return np.array(lower[:-1] + upper[:-1])


def poly_dist(Q, H):
    """signed-ish distance of points Q (n,2) to convex polygon H (ccw): <= 0 inside, else euclidean distance."""
    Q = np.asarray(Q, float)
    n = len(H)
    inside = np.ones(len(Q), bool)
    dmin = np.full(len(Q), np.inf)
    for i in range(n):
        a = H[i]; b = H[(i + 1) % n]; e = b - a
        cr = e[0] * (Q[:, 1] - a[1]) - e[1] * (Q[:, 0] - a[0])
        inside &= cr >= 0
        t = np.clip(((Q - a) @ e) / max(e @ e, 1e-12), 0, 1)
        d = np.linalg.norm(Q - (a + t[:, None] * e), axis=1)
        dmin = np.minimum(dmin, d)
    return np.where(inside, -dmin, dmin)


def dist_to_hulls(Q, hulls):
    d = np.full(len(Q), np.inf)
    for H in hulls:
        if len(H) < 3:
            continue
        lo = H.min(0) - 1.0; hi = H.max(0) + 1.0
        m = (Q[:, 0] > lo[0]) & (Q[:, 0] < hi[0]) & (Q[:, 1] > lo[1]) & (Q[:, 1] < hi[1])
        if m.any():
            d[m] = np.minimum(d[m], poly_dist(Q[m], H))
    return d


def delete_faces_and_islands(o, face_mask):
    """delete the faces in face_mask and any vertex left without faces."""
    if not face_mask.any():
        return 0
    me = o.data
    bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
    dead = [bm.faces[i] for i in np.nonzero(face_mask)[0]]
    bmesh.ops.delete(bm, geom=dead, context='FACES_ONLY')
    loose = [v for v in bm.verts if not v.link_faces]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context='VERTS')
    bm.to_mesh(me); bm.free(); me.update()
    return int(face_mask.sum())


def fields_aqueduct(F, T):
    """fields_e OP07: no straw pile / vine stake / plate face inside an aqueduct pier footprint (+0.3 / +0.1)."""
    hulls = aqueduct_piers(T)
    if not hulls:
        log('fields_aqueduct', {'piers': 0}); return
    d = dist_to_hulls(F.W[:, :2], hulls)
    kill_isl = set()
    for k in range(F.n):
        if F.kind[k] in ('straw', 'vine') and d[F.lab == k].min() < 0.30:
            kill_isl.add(k)
    face_mask = np.isin(F.flab, list(kill_isl)) if kill_isl else np.zeros(len(F.flab), bool)
    # plate faces: sample each face (vertices + centre + edge midpoints); any sample within 0.10 of a pier -> delete
    n_plate = 0
    fc = np.array([F.W[F.lv[F.ls[f]:F.ls[f] + F.lt[f]], :2].mean(0) for f in range(len(F.flab))])
    near = (F.kind[F.flab] == 'plate') & (dist_to_hulls(fc, hulls) < 2.5)
    for f in np.nonzero(near)[0]:
        vs = F.lv[F.ls[f]:F.ls[f] + F.lt[f]]
        P = F.W[vs, :2]
        S = np.vstack([P, P.mean(0)[None], (P + np.roll(P, -1, 0)) / 2, (P + P.mean(0)) / 2])
        if dist_to_hulls(S, hulls).min() < 0.10:
            face_mask[f] = True; n_plate += 1
    straws = sorted(int(k) for k in kill_isl if F.kind[k] == 'straw'); vines = sorted(int(k) for k in kill_isl if F.kind[k] == 'vine')
    info = {'pier_hulls': len(hulls), 'straw_islands_deleted': len(straws), 'vine_islands_deleted': len(vines),
            'straw_deleted_at_pt': [F.pcen[k].round(1).tolist() for k in straws],
            'vine_deleted_at_pt': [F.pcen[k].round(1).tolist() for k in vines], 'plate_faces_deleted': n_plate}
    delete_faces_and_islands(F.o, face_mask)
    F.load()
    log('fields_aqueduct', info)


def move_islands(F, T, isl, fn):
    """apply fn(world xy (n,2)) -> new xy to the vertices of the islands; z follows the original terrain difference."""
    idx = np.nonzero(np.isin(F.lab, isl))[0]
    W = F.W.copy()
    xy0 = W[idx, :2]; xy1 = fn(xy0)
    t0 = T.zs(xy0); t1 = T.zs(xy1)
    dz = np.where(np.isfinite(t0) & np.isfinite(t1), t1 - t0, 0.0)
    W[idx, :2] = xy1; W[idx, 2] += dz
    plate_v = np.isin(F.lab[idx], [k for k in isl if F.kind[k] == 'plate'])
    floor = np.where(np.isfinite(t1), t1 + 0.05, -np.inf)
    W[idx[plate_v], 2] = np.maximum(W[idx[plate_v], 2], floor[plate_v])
    set_world_verts(F.o, W)
    F.load()
    return idx


class KD2:
    """2-D nearest-distance queries (mathutils KDTree on z = 0)."""
    def __init__(self, P):
        self.kd = KDTree(max(1, len(P)))
        for i, p in enumerate(P):
            self.kd.insert((float(p[0]), float(p[1]), 0.0), i)
        self.kd.balance()
        self.n = len(P)

    def dmin(self, Q):
        if self.n == 0 or len(Q) == 0:
            return float('inf')
        return min(self.kd.find((float(q[0]), float(q[1]), 0.0))[2] for q in Q)

    def dists(self, Q):
        return np.array([self.kd.find((float(q[0]), float(q[1]), 0.0))[2] for q in Q]) if self.n else np.full(len(Q), np.inf)


def screen_gap(P_a, P_b):
    """min distance between two projected point clouds (pt)."""
    if isinstance(P_b, KD2):
        return P_b.dmin(P_a)
    return KD2(P_b).dmin(P_a)


def tri_samples(T2, step):
    """points covering 2-D triangles T2 (m,3,2) with <= step spacing (vectorised)."""
    if len(T2) == 0:
        return np.zeros((0, 2))
    L = np.max(np.linalg.norm(T2 - np.roll(T2, 1, axis=1), axis=2), axis=1)
    n = np.clip(np.ceil(L / step).astype(int), 1, 200)
    out = []
    for k in np.unique(n):
        sel = T2[n == k]
        ij = np.array([(i, j) for i in range(k + 1) for j in range(k + 1 - i)], float) / k
        w = np.c_[1 - ij.sum(1), ij]
        out.append(np.einsum('wk,tkd->twd', w, sel).reshape(-1, 2))
    return np.concatenate(out)


def face_samples_pt(_unused, S, faces_vs, step=0.4):
    """projected sample points covering faces given as a list of world vertex arrays."""
    tris = []
    for Wf in faces_vs:
        for k in range(1, len(Wf) - 1):
            tris.append(Wf[[0, k, k + 1]])
    if not tris:
        return np.zeros((0, 2))
    T3 = np.array(tris)
    P = S.project(T3.reshape(-1, 3)).reshape(-1, 3, 2)
    return tri_samples(P, step)


def object_face_samples(o, S, step=0.4):
    W = world_verts(o)
    return face_samples_pt(None, S, [W[list(p.vertices)] for p in o.data.polygons], step)


def fields_w_heat(F, T, S):
    """fields_w NEW-01 (blocker) + OP09: the two-plate strip under the d2 heat hook is shortened along its long
    axis (world Y) with its -Y (screen west) end fixed, until its screen gap to the D2_heat marks is >= 4.3 pt."""
    isl = F.islands_in((20.0, 95.0, 890.0, 935.0))
    isl = [k for k in isl if F.kind[k] == 'plate']
    if len(isl) == 0:
        log('fields_w_heat', 'plates not found'); return
    heat = [bpy.data.objects[n] for n in ('D2_heat0', 'D2_heat1', 'D2_heat2') if bpy.data.objects.get(n)]
    Hs = KD2(np.vstack([object_face_samples(h, S) for h in heat]))
    idx = np.nonzero(np.isin(F.lab, isl))[0]
    fidx = np.nonzero(np.isin(F.flab, isl))[0]
    W0 = F.W.copy()
    y0 = W0[idx, 1].min()
    faces = [F.lv[F.ls[f]:F.ls[f] + F.lt[f]] for f in fidx]

    def gap_for(s):
        W = W0.copy(); W[idx, 1] = y0 + (W0[idx, 1] - y0) * s
        Ps = np.vstack([island_outline(F, list(isl), S, 0.4, W), face_samples_pt(None, S, [W[v] for v in faces], 2.0)])
        return screen_gap(Ps, Hs)
    g0 = gap_for(1.0)
    best = None
    for s in np.arange(1.0, 0.59, -0.01):
        g = gap_for(s)
        if g >= 4.3:
            best = (round(float(s), 2), g); break
    if best is None:
        log('fields_w_heat', {'gap_before': g0, 'result': 'no scale >= 0.6 reaches 4.3 pt'}); return
    s = best[0]
    props = F.props_on(isl)
    move_islands(F, T, list(isl), lambda xy: np.c_[xy[:, 0], y0 + (xy[:, 1] - y0) * s])
    if props:   # props keep their shape: move by their centroid's scaled offset
        for k in props:
            c = F.cen[k]
            dy = (y0 + (c[1] - y0) * s) - c[1]
            move_islands(F, T, [k], lambda xy, dy=dy: np.c_[xy[:, 0], xy[:, 1] + dy])
    log('fields_w_heat', {'plates': [int(k) for k in isl], 'gap_before_pt': round(g0, 2), 'scale_y': s,
                          'gap_after_pt': round(best[1], 2), 'props_moved': len(props)})


def water_mask_points(S, box, step=0.75):
    """screen sample points (pt) inside box whose first hit is water (L02_tiber / L10_sea)."""
    sc = bpy.context.scene; dg = bpy.context.evaluated_depsgraph_get()
    x0, x1, y0, y1 = box
    pts = []
    for y in np.arange(y0, y1, step):
        for x in np.arange(x0, x1, step):
            o, d = S.ray((x, y))
            r = sc.ray_cast(dg, o, d)
            if r[0] and r[4].name in ('L02_tiber', 'L10_sea'):
                pts.append((x, y))
    return np.array(pts)


def island_samples(F, isl, S, step=0.5):
    fidx = np.nonzero(np.isin(F.flab, isl))[0]
    return face_samples_pt(None, S, [F.W[F.lv[F.ls[f]:F.ls[f] + F.lt[f]]] for f in fidx], step)



def island_outline(F, isl, S, step=0.5, W=None):
    """screen points along the outer (one-face) edges of the given islands, every <= step pt."""
    W = F.W if W is None else W
    me = F.o.data
    if not hasattr(F, '_bedges') or F._bedges_n != len(me.edges):
        le = np.empty(len(me.loops), np.int32); me.loops.foreach_get('edge_index', le)
        cnt = np.bincount(le, minlength=len(me.edges))
        E = np.empty(len(me.edges) * 2, np.int32); me.edges.foreach_get('vertices', E); E = E.reshape(-1, 2)
        F._bedges = E[cnt == 1]; F._bedges_n = len(me.edges)
    Eb = F._bedges[np.isin(F.lab[F._bedges[:, 0]], isl)]
    if len(Eb) == 0:
        return np.zeros((0, 2))
    A = S.project(W[Eb[:, 0]]); B = S.project(W[Eb[:, 1]])
    L = np.linalg.norm(B - A, axis=1); n = np.clip(np.ceil(L / step).astype(int), 1, 400)
    out = []
    for k in np.unique(n):
        a, b = A[n == k], B[n == k]
        for t in range(k + 1):
            out.append(a + (b - a) * (t / k))
    return np.vstack(out)


def fields_sw_bank(F, T, S):
    """fields_sw OP03 (major) / COLOR-24 / FORM-15: the L-shaped meadow + stubble plates on the Tiber bank and their
    straw piles move away from the river by world (-0.6, -0.6) (more if the water gap is still < 4 pt)."""
    plates = [k for k in F.islands_in((178.0, 238.0, 1070.0, 1118.0)) if F.kind[k] == 'plate']
    straws = [k for k in F.islands_in((178.0, 238.0, 1068.0, 1118.0), ('straw',))]
    if not plates:
        log('fields_sw_bank', 'plates not found'); return
    box = (150.0, 290.0, 1040.0, 1140.0)
    Wt = KD2(water_mask_points(S, box))
    g0 = screen_gap(island_samples(F, plates, S), Wt) if Wt.n else None
    shift = 0.6
    move_islands(F, T, plates + straws, lambda xy: xy - shift)
    g1 = screen_gap(island_samples(F, plates, S), Wt) if Wt.n else None
    extra = 0.0
    while g1 is not None and g1 < 4.5 and extra < 0.6:
        move_islands(F, T, plates + straws, lambda xy: xy - 0.1); extra += 0.1
        g1 = screen_gap(island_samples(F, plates, S), Wt)
    log('fields_sw_bank', {'plates': [int(k) for k in plates], 'straws': [int(k) for k in straws], 'shift_world': -(shift + extra),
                           'water_gap_before_pt': g0 and round(g0, 2), 'water_gap_after_pt': g1 and round(g1, 2)})


def fields_nw_river(F, T, S):
    """fields_nw OP11: the plate whose edge comes within 2.55 pt of the Tiber at (277.9, 628.3) moves +X 0.4."""
    target = np.array((277.9, 628.3))
    best = None
    for k in range(F.n):
        if F.kind[k] != 'plate':
            continue
        m = F.lab == k
        d = np.linalg.norm(F.P[m] - target, axis=1).min()
        if best is None or d < best[0]:
            best = (d, k)
    if best is None or best[0] > 8.0:
        log('fields_nw_river', {'result': 'plate not found', 'nearest': best and round(best[0], 2)}); return
    k = best[1]
    box = (230.0, 330.0, 590.0, 670.0)
    Wt = KD2(water_mask_points(S, box))
    g0 = screen_gap(island_samples(F, [k], S), Wt)
    props = F.props_on([k])
    dx = 0.4
    move_islands(F, T, [k] + props, lambda xy: np.c_[xy[:, 0] + dx, xy[:, 1]])
    g1 = screen_gap(island_samples(F, [k], S), Wt)
    while g1 < 4.3 and dx < 0.8:
        move_islands(F, T, [k] + props, lambda xy: np.c_[xy[:, 0] + 0.1, xy[:, 1]]); dx += 0.1
        g1 = screen_gap(island_samples(F, [k], S), Wt)
    log('fields_nw_river', {'plate': int(k), 'props': len(props), 'dx': round(dx, 2), 'water_gap_before_pt': round(g0, 2), 'water_gap_after_pt': round(g1, 2)})


def fields_e_block(F, T, S):
    """fields_e HIER-06: the closed 8-plate block at the SE end (screen 1017-1140 x 501-563) sits 2.9-3.0 pt from the
    plate groups on both sides (moving it 2 pt down, as suggested, closes the east gap to 1.1 pt). It shrinks about its
    own centre (largest scale <= 0.995 that opens every neighbour gap to >= 4 pt), so it no longer merges with them."""
    cand = [k for k in F.islands_in((1010.0, 1145.0, 498.0, 566.0)) if F.kind[k] == 'plate']
    blk = [k for k in cand if F.W[F.lab == k, 0].min() > -8.5 and F.W[F.lab == k, 0].max() < 1.7 and F.W[F.lab == k, 1].min() > 75.5]
    if len(blk) == 0:
        log('fields_e_block', 'block not found'); return
    bx0, by0 = F.P[np.isin(F.lab, blk)].min(0) - 12; bx1, by1 = F.P[np.isin(F.lab, blk)].max(0) + 12
    others = []
    for k in range(F.n):
        if F.kind[k] != 'plate' or k in blk:
            continue
        pk = F.P[F.lab == k]
        if pk[:, 0].max() > bx0 and pk[:, 0].min() < bx1 and pk[:, 1].max() > by0 and pk[:, 1].min() < by1:
            others.append(k)

    other_kd = [(KD2(island_outline(F, [k], S, 0.5)), int(k)) for k in others]

    def gaps(Wb=None):
        A = island_outline(F, blk, S, 0.5, Wb)
        return sorted((kd.dmin(A), k) for kd, k in other_kd if kd.n)[:4]

    g0 = gaps()
    idx = np.nonzero(np.isin(F.lab, blk))[0]
    c = F.W[idx, :2].mean(0)
    props = F.props_on(blk)
    W0 = F.W.copy()
    s_ok = None
    for s_ in np.arange(0.995, 0.899, -0.005):
        Wt = W0.copy(); Wt[idx, :2] = c + (W0[idx, :2] - c) * s_
        if min(g for g, k in gaps(Wt)) >= 4.0:
            s_ok = round(float(s_), 3); break
    if s_ok is None:
        log('fields_e_block', {'result': 'no scale >= 0.9 opens all gaps to 4 pt', 'gaps_before': g0}); return
    move_islands(F, T, blk, lambda xy: c + (xy - c) * s_ok)
    for k in props:   # props keep their shape, follow their centroid
        ck = F.cen[k][:2]; d_ = c + (ck - c) * s_ok - ck
        move_islands(F, T, [k], lambda xy, d_=d_: xy + d_)
    log('fields_e_block', {'plates': [int(k) for k in blk], 'props': len(props), 'scale_about_centre': s_ok,
                           'nearest_gaps_before': [[round(g, 2), k] for g, k in g0],
                           'nearest_gaps_after': [[round(g, 2), k] for g, k in gaps()]})


def straw_fix(F, T, S):
    """fields_* FORM-19 / FORM-22: straw piles shorter than 0.49 grow (uniform, about their bottom tip) to 0.49; every
    pile then drops so its lower side ring sits 0.02 above the plate (or the ground) under it."""
    plate_faces = np.nonzero(F.kind[F.flab] == 'plate')[0]
    pf = set(plate_faces.tolist())
    sup = bvh_from([F.o], lambda o, me: [p.index in pf for p in me.polygons])
    land_bvh = bvh_from([need('T_land')])
    W = F.W.copy()
    grown = 0; drops = []
    for k in np.nonzero(F.kind == 'straw')[0]:
        idx = np.nonzero(F.lab == k)[0]
        w = W[idx]
        zmin = w[:, 2].min(); h = np.ptp(w[:, 2])
        tip = w[np.argmin(w[:, 2])].copy()
        if h < STRAW_MIN - 1e-4:
            s = STRAW_MIN / h
            w = tip + (w - tip) * s; grown += 1
        levels = np.unique(np.round(w[:, 2], 4))
        ring_z = levels[1] if len(levels) > 1 else levels[0]
        ring = w[np.abs(w[:, 2] - ring_z) < 1e-3]
        best = -np.inf
        for x, y, _ in ring:
            for b in (sup, land_bvh):
                hit = b.ray_cast(Vector((x, y, ring_z + 0.6)), Vector((0, 0, -1)))[0]
                if hit is not None:
                    best = max(best, hit.z); break
        if not np.isfinite(best):
            continue
        dz = best + 0.02 - ring_z
        w[:, 2] += dz; drops.append(dz)
        W[idx] = w
    set_world_verts(F.o, W)
    F.load()
    hs = np.array([np.ptp(F.W[F.lab == k, 2]) for k in np.nonzero(F.kind == 'straw')[0]])
    log('straw_fix', {'piles': int((F.kind == 'straw').sum()), 'grown_to_min': grown, 'min_height': STRAW_MIN,
                      'drop_min_med_max': np.round(np.percentile(drops, [0, 50, 100]), 3).tolist() if drops else None,
                      'height_min_max_ratio': [round(float(hs.min()), 3), round(float(hs.max()), 3), round(float(hs.max() / hs.min()), 3)]})


def straw_colour():
    """fields_e HIER-15: field_straw #D5BB82 -> #D0BC8F (Oklch C 0.080 -> 0.064, same L and hue)."""
    m = bpy.data.materials.get('RC.v12_13.field_straw')
    if m is None:
        log('straw_colour', 'material missing'); return
    users = [o.name for o in bpy.data.objects if any(s.material == m for s in o.material_slots)]
    if any(u != 'F_centuriatio' for u in users):
        raise RuntimeError(f'WE step: RC.v12_13.field_straw is shared with {users}')
    lin = hex_lin('#D0BC8F')
    m.diffuse_color = (*lin, 1.0)
    if m.node_tree:
        for n in m.node_tree.nodes:
            if n.type == 'BSDF_PRINCIPLED':
                n.inputs['Base Color'].default_value = (*lin, 1.0)
    log('straw_colour', {'material': m.name, 'hex': '#D0BC8F', 'users': users})


def hex_lin(h):
    def s2l(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(s2l(int(h[i:i + 2], 16) / 255) for i in (1, 3, 5))


# ------------------------------------------------------------------ roads: paving parts, landing ends, paving bed
CELL = 0.10        # world units, raster for the paving bed / carving caps
BED_D = float(os.environ.get('WE_BED_D', '0.03'))      # bed top below the lowest paver top around it
BED_HEX = os.environ.get('WE_BED_HEX', '')             # '' = paving material RC.road.selce_basalt
BED_MAT = 'RC.road.joint_bed'


def road_parts(o):
    lab, flab, ls, lt, lv = islands(o)
    n = int(lab.max()) + 1 if len(lab) else 0
    nf = np.bincount(flab, minlength=n)
    return lab, flab, ls, lt, lv, nf


def delete_islands(o, kill):
    lab, flab, ls, lt, lv, nf = road_parts(o)
    return delete_faces_and_islands(o, np.isin(flab, list(kill)))


def landing_kill(road, c, r, under_margin, t_min):
    """paving parts (< 40 faces) of road: centre within r + under_margin of the disc centre c (under the disc), and
    parts outside the disc whose centre lies past the disc centre towards the dead end (t > t_min along the road)."""
    lab, flab, ls, lt, lv, nf = road_parts(road)
    W = world_verts(road)
    cen = np.array([W[lab == k, :2].mean(0) for k in range(len(nf))])
    pav = nf < KERB_MIN_FACES
    d = np.linalg.norm(cen - c, axis=1)
    ring = pav & (d > 1.5) & (d < 5.0) & (d > r + 0.3)
    ax = c - cen[ring].mean(0); ax /= np.linalg.norm(ax)
    t = (cen - c) @ ax
    under = [int(k) for k in np.nonzero(pav & (d < r + under_margin))[0]] if under_margin > -1 else []
    beyond = [int(k) for k in np.nonzero(pav & (d >= r + max(under_margin, -0.05)) & (d < r + 1.2) & (t > t_min))[0]]
    return under, beyond


def road_landing1(S):
    """road_core_nw FORM-18: the paving parts of R_core_road whose centre lies under the landing disc
    R1_road_landing1 (radius + 0.09) are removed, and so are the small paving fragments that stick out past its rim
    (parts whose centre is within rim + 0.6 and that lie outside the road's kerb lines, i.e. beyond the road end)."""
    road = need('R_core_road'); l1 = need('R1_road_landing1')
    Wl = world_verts(l1); c = Wl[:, :2].mean(0); r = float(np.linalg.norm(Wl[:, :2] - c, axis=1).max())
    lab, flab, ls, lt, lv, nf = road_parts(road)
    W = world_verts(road)
    kill, beyond = landing_kill(road, c, r, 0.09, 0.3)
    n = delete_islands(road, kill + beyond)
    log('road_landing1', {'centre': c.round(3).tolist(), 'radius': round(r, 3), 'paving_parts_under_disc': len(kill),
                          'paving_parts_beyond_rim': len(beyond), 'faces': n})


def road_landing5(S):
    """road_core_se FORM-19: paving bits beyond the landing disc R1_road_landing5 (screen 936-949 x 865-869) and the
    kerb-less 1-4-face paving strip east of the east kerb (screen x > 953.9, y 866-892) are removed."""
    road = need('R_core_road'); l5 = need('R1_road_landing5')
    Wl = world_verts(l5); c = Wl[:, :2].mean(0); r = float(np.linalg.norm(Wl[:, :2] - c, axis=1).max())
    _, beyond = landing_kill(road, c, r, -1.0, 0.8)
    lab, flab, ls, lt, lv, nf = road_parts(road)
    W = world_verts(road); P = S.project(W)
    strip = []
    for k in range(len(nf)):
        if nf[k] >= KERB_MIN_FACES or k in beyond:
            continue
        p = P[lab == k].mean(0)
        if p[0] > 953.9 and 866.0 <= p[1] <= 892.0:
            strip.append(k)
    n = delete_islands(road, beyond + strip)
    log('road_landing5', {'paving_parts_beyond_rim': len(beyond), 'kerbless_strip_parts': len(strip), 'faces': n})


def raster(tris, x0, y0, nx, ny, mode='max'):
    """z of triangles (m,3,3) on a CELL grid (cell centres x0 + i*CELL); max or min where several overlap; nan elsewhere."""
    fill = -np.inf if mode == 'max' else np.inf
    G = np.full((ny, nx), fill)
    for t in tris:
        a, b, c = t
        i0 = max(0, int(math.floor((t[:, 0].min() - x0) / CELL))); i1 = min(nx - 1, int(math.ceil((t[:, 0].max() - x0) / CELL)))
        j0 = max(0, int(math.floor((t[:, 1].min() - y0) / CELL))); j1 = min(ny - 1, int(math.ceil((t[:, 1].max() - y0) / CELL)))
        if i1 < i0 or j1 < j0:
            continue
        X, Y = np.meshgrid(x0 + np.arange(i0, i1 + 1) * CELL, y0 + np.arange(j0, j1 + 1) * CELL)
        v0 = b[:2] - a[:2]; v1 = c[:2] - a[:2]
        den = v0[0] * v1[1] - v1[0] * v0[1]
        if abs(den) < 1e-12:
            continue
        px = X - a[0]; py = Y - a[1]
        u = (px * v1[1] - v1[0] * py) / den; v = (v0[0] * py - px * v0[1]) / den; w = 1 - u - v
        e = 0.35 * CELL / max(1e-6, math.sqrt(abs(den)))           # half a cell of slack: thin strips still mark cells
        inside = (u >= -e) & (v >= -e) & (w >= -e)
        z = w * a[2] + u * b[2] + v * c[2]
        sub = G[j0:j1 + 1, i0:i1 + 1]
        if mode == 'max':
            np.maximum(sub, np.where(inside, z, -np.inf), out=sub)
        else:
            np.minimum(sub, np.where(inside, z, np.inf), out=sub)
    G[~np.isfinite(G)] = np.nan
    return G


def shift(G, dy, dx, fill):
    H = np.full_like(G, fill)
    ny, nx = G.shape
    ys0, ys1 = max(0, dy), ny + min(0, dy); xs0, xs1 = max(0, dx), nx + min(0, dx)
    H[ys0:ys1, xs0:xs1] = G[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
    return H


def disk(r):
    R = int(math.ceil(r))
    return [(dy, dx) for dy in range(-R, R + 1) for dx in range(-R, R + 1) if dx * dx + dy * dy <= r * r + 1e-9]


def dilate(M, r):
    out = np.zeros_like(M)
    for dy, dx in disk(r):
        out |= shift(M, dy, dx, False)
    return out


def erode(M, r):
    return ~dilate(~M, r)


def nan_min_filter(G, r):
    out = np.full_like(G, np.nan)
    with np.errstate(invalid='ignore'):
        for dy, dx in disk(r):
            H = shift(G, dy, dx, np.nan)
            out = np.fmin(out, H)
    return out


def face_tris(o, faces):
    W = world_verts(o); me = o.data
    tris = []
    for f in faces:
        v = list(me.polygons[f].vertices)
        for k in range(1, len(v) - 1):
            tris.append(W[[v[0], v[k], v[k + 1]]])
    return np.array(tris).reshape(-1, 3, 3)


def world_normals_z(o):
    me = o.data
    fn = np.empty(len(me.polygons) * 3); me.polygons.foreach_get('normal', fn)
    fn = fn.reshape(-1, 3) @ np.array(o.matrix_world.to_3x3()).T
    return fn[:, 2] / np.maximum(np.linalg.norm(fn, axis=1), 1e-12)


class BedGrid:
    def __init__(self, x0, y0, nx, ny, Z, M):
        self.x0, self.y0, self.nx, self.ny, self.Z, self.M = x0, y0, nx, ny, Z, M

    def at(self, xy, grow=1):
        """bed z under each point (min over a (2*grow+1)^2 neighbourhood of bed cells), nan if no bed."""
        i = np.rint((xy[:, 0] - self.x0) / CELL).astype(int); j = np.rint((xy[:, 1] - self.y0) / CELL).astype(int)
        out = np.full(len(xy), np.nan)
        Zm = np.where(self.M, self.Z, np.nan)
        for dj in range(-grow, grow + 1):
            for di in range(-grow, grow + 1):
                ii = i + di; jj = j + dj
                ok = (ii >= 0) & (ii < self.nx) & (jj >= 0) & (jj < self.ny)
                v = np.full(len(xy), np.nan); v[ok] = Zm[jj[ok], ii[ok]]
                out = np.fmin(out, v)
        return out


def build_bed(S):
    """road_core_* PLACE-03 / HIER-09 / OV-RSW-23, road_appia HIER-09: a thin paving bed under the joints of the
    core road and the Via Appia. Footprint = paving tops + kerb tops, closed by 0.3 (joints, kerb notches, the wedge
    at the south bridge's east ramp), shrunk one cell so it stays inside the outer kerb edges and off the bridge decks
    and landing discs. Its top lies BED_D below the lowest paver top within 0.4, so the joints show a shallow floor in
    paving colour instead of a deep shadow or the paper-coloured ground."""
    grids = []
    verts_all, faces_all = [], []
    block = []
    for bn in ('B_pons1', 'B_pons2', 'R1_road_landing1', 'R1_road_landing5', 'R4_bridge_west_bed'):
        b = need(bn); Wb = world_verts(b)
        block.append((bn, convex_hull(Wb[:, :2]), float(Wb[:, 2].min())))
    info = {}
    for name in ('R_core_road', 'R_via_appia'):
        o = need(name)
        lab, flab, ls, lt, lv, nf = road_parts(o)
        nz = world_normals_z(o)
        pav = nf[flab] < KERB_MIN_FACES
        tops = np.nonzero(pav & (nz > 0.7))[0]
        kerb = np.nonzero(~pav & (np.abs(nz) > 0.7))[0]
        Tt = face_tris(o, tops); Tk = face_tris(o, kerb)
        W = world_verts(o)
        x0, y0 = W[:, 0].min() - 1.0, W[:, 1].min() - 1.0
        nx = int(math.ceil((W[:, 0].max() + 1.0 - x0) / CELL)) + 1; ny = int(math.ceil((W[:, 1].max() + 1.0 - y0) / CELL)) + 1
        Zt = raster(Tt, x0, y0, nx, ny, 'max')
        Zk = raster(Tk, x0, y0, nx, ny, 'max')
        M0 = np.isfinite(Zt) | np.isfinite(Zk)
        Mc = erode(dilate(M0, 3), 3) | M0
        Mb = erode(Mc, 1)
        X, Y = np.meshgrid(x0 + np.arange(nx) * CELL, y0 + np.arange(ny) * CELL)
        cells = np.c_[X.ravel(), Y.ravel()]
        for bn, H, zbot in block:
            if bn.startswith('B_pons') or bn == 'R4_bridge_west_bed':
                d = dist_to_hulls(cells, [H]).reshape(ny, nx)
                Mb &= ~(d < 0.05)
        Zmin = nan_min_filter(Zt, 4)
        Zb = Zmin - BED_D
        for bn, H, zbot in block:                      # stay under the landing discs
            if bn.startswith('R1_road_landing'):
                d = dist_to_hulls(cells, [H]).reshape(ny, nx)
                near = d < 0.15
                Zb = np.where(near & np.isfinite(Zb), np.minimum(Zb, zbot - 0.012), Zb)
        Mb &= np.isfinite(Zb)
        grids.append(BedGrid(x0, y0, nx, ny, Zb, Mb))
        # mesh: one quad per bed cell, corner z = mean of the bed cells around it
        js, is_ = np.nonzero(Mb)
        Zc = np.where(Mb, Zb, 0.0); Mc_ = Mb.astype(float)
        Zp = np.pad(Zc, 1); Mp = np.pad(Mc_, 1)
        cs = Zp[:-1, :-1] + Zp[1:, :-1] + Zp[:-1, 1:] + Zp[1:, 1:]
        cn = Mp[:-1, :-1] + Mp[1:, :-1] + Mp[:-1, 1:] + Mp[1:, 1:]
        cz = np.where(cn > 0, cs / np.maximum(cn, 1), 0.0)               # (ny+1, nx+1) corners
        used = np.zeros((ny + 1, nx + 1), bool)
        for dj, di in ((0, 0), (0, 1), (1, 0), (1, 1)):
            used[js + dj, is_ + di] = True
        vid = -np.ones((ny + 1, nx + 1), np.int64)
        vj, vi = np.nonzero(used)
        base = sum(len(v) for v in verts_all)
        vid[vj, vi] = base + np.arange(len(vj))
        verts_all.append(np.c_[x0 + (vi - 0.5) * CELL, y0 + (vj - 0.5) * CELL, cz[vj, vi]])
        faces_all.append(np.c_[vid[js, is_], vid[js, is_ + 1], vid[js + 1, is_ + 1], vid[js + 1, is_]])
        info[name] = {'bed_cells': int(Mb.sum()), 'paving_top_faces': int(len(tops)), 'kerb_top_faces': int(len(kerb)),
                      'closing_added_cells': int((Mc & ~M0).sum())}
    V = np.vstack(verts_all); Fc = np.vstack(faces_all)
    me = bpy.data.meshes.get(BED_NAME)
    if me is None:
        me = bpy.data.meshes.new(BED_NAME)
    else:
        me.clear_geometry()
    me.from_pydata(V.tolist(), [], Fc.tolist())
    me.update()
    ob = bpy.data.objects.get(BED_NAME)
    if ob is None:
        ob = bpy.data.objects.new(BED_NAME, me)
        for col in need('R_core_road').users_collection:
            col.objects.link(ob)
    elif ob.data != me:
        ob.data = me
    ob.matrix_world = Matrix.Identity(4)
    pave = bpy.data.materials.get('RC.road.selce_basalt')
    if BED_HEX:
        m = bpy.data.materials.get(BED_MAT) or pave.copy()
        m.name = BED_MAT
        lin = hex_lin(BED_HEX); m.diffuse_color = (*lin, 1.0)
        if m.node_tree:
            for n in m.node_tree.nodes:
                if n.type == 'BSDF_PRINCIPLED':
                    n.inputs['Base Color'].default_value = (*lin, 1.0)
        pave = m
    me.materials.clear(); me.materials.append(pave)
    ob.hide_render = False; ob.hide_viewport = False
    info['faces'] = len(me.polygons); info['material'] = pave.name; info['depth_below_min_top'] = BED_D
    log('paving_bed', info)
    return grids


def lower_road5_bed(grids):
    """road_core_se COLOR-25 / FORM-19: R1_road5_bed sank into / covered the pavers; it drops 0.12 and in any case
    0.03 under the new paving bed, so the pavers and the bed show and nothing z-fights."""
    o = need('R1_road5_bed'); W = world_verts(o)
    z = W[:, 2] - 0.12
    for g in grids:
        b = g.at(W[:, :2], grow=2)
        z = np.where(np.isfinite(b), np.minimum(z, b - 0.03), z)
    d = W[:, 2] - z
    W[:, 2] = z
    set_world_verts(o, W)
    log('road5_bed', {'lowered_by': np.round(d, 3).tolist()})


# ------------------------------------------------------------------ terrain
def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def eval_world_verts(o):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = o.evaluated_get(dg); me = ev.to_mesh()
    co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    ev.to_mesh_clear()
    return (np.c_[co, np.ones(len(co))] @ np.array(o.matrix_world).T)[:, :3]


def ground_contacts(T, box, exclude, band=(-0.6, 0.45), cap=25000, near=None, near_r=2.0, overlay=True):
    """xy of the vertices of other render-visible objects (map + overlay) that lie near the ground in box."""
    x0, x1, y0, y1 = box
    pts, names = [], {}
    seen = set()
    near_keys = None
    if near is not None:
        ci = np.floor(near[:, 0] / near_r).astype(np.int64); cj = np.floor(near[:, 1] / near_r).astype(np.int64)
        near_keys = np.unique(np.concatenate([(ci + di) * 100003 + (cj + dj) for di in (-1, 0, 1) for dj in (-1, 0, 1)]))
    for o in map_visible_objects() + (overlay_objects() if overlay else []):
        if o.name in seen or o.name in exclude or o.name in NOT_GROUND or o.name == BED_NAME:
            continue
        seen.add(o.name)
        Wv = eval_world_verts(o)
        if not len(Wv):
            continue
        m = (Wv[:, 0] > x0) & (Wv[:, 0] < x1) & (Wv[:, 1] > y0) & (Wv[:, 1] < y1)
        if near is not None and m.any():
            key = (np.floor(Wv[:, 0] / near_r).astype(np.int64) * 100003 + np.floor(Wv[:, 1] / near_r).astype(np.int64))
            m &= np.isin(key, near_keys)
        if not m.any():
            continue
        sub = Wv[m]
        if len(sub) > cap:
            sub = sub[::len(sub) // cap + 1]
        tz = T.zs(sub[:, :2])
        dz = sub[:, 2] - tz
        k = np.isfinite(tz) & (dz > band[0]) & (dz < band[1])
        if k.any():
            pts.append(sub[k, :2]); names[o.name] = int(k.sum())
    return (np.vstack(pts) if pts else np.zeros((0, 2))), names


class TerrainEdit:
    """all T_land height edits are collected on a copy of the original z and written once."""
    def __init__(self):
        self.o = need('T_land')
        self.W0 = world_verts(self.o)
        self.xy = self.W0[:, :2].copy()
        self.z0 = self.W0[:, 2].copy()
        self.z = self.z0.copy()
        ls, lt, lv, E = mesh_topo(self.o)
        self.ls, self.lt, self.lv, self.E = ls, lt, lv, E
        me = self.o.data
        fn = np.empty(len(me.polygons) * 3); me.polygons.foreach_get('normal', fn)
        self.fnz = np.abs(fn.reshape(-1, 3)[:, 2])
        fidx = np.repeat(np.arange(len(ls)), lt)
        self.steep = np.zeros(len(self.z0), bool)
        self.steep[lv[(self.fnz < 0.7)[fidx]]] = True
        self.notes = {}

    def box(self, x0, x1, y0, y1):
        return np.nonzero((self.xy[:, 0] >= x0) & (self.xy[:, 0] <= x1) & (self.xy[:, 1] >= y0) & (self.xy[:, 1] <= y1))[0]

    def pin_limit(self, idx, pins, r0=0.35, fade=0.5):
        """largest |dz| allowed at idx given ground-contact points of other objects."""
        if len(pins) == 0:
            return np.full(len(idx), np.inf)
        d = KD2(pins).dists(self.xy[idx])
        return np.maximum(0.0, d - r0) * fade

    def pin_weight(self, idx, pins, r0=0.35, rf=1.8):
        """0 at the ground contacts of other objects (within r0), smoothly 1 beyond r0 + rf."""
        if len(pins) == 0:
            return np.ones(len(idx))
        d = KD2(pins).dists(self.xy[idx])
        return smoothstep(r0, r0 + rf, d)

    def blend_to(self, idx, target, w, lim=None):
        dz = w * (target - self.z[idx])
        if lim is not None:
            dz = np.clip(dz, -lim, lim)
        self.z[idx] += dz
        return dz

    def cap(self, idx, cap, lim=None):
        dz = np.minimum(0.0, cap - self.z[idx])
        dz = np.where(np.isfinite(dz), dz, 0.0)
        if lim is not None:
            dz = np.maximum(dz, -lim)
        self.z[idx] += dz
        return dz

    def write(self):
        W = self.W0.copy(); W[:, :2] = self.xy; W[:, 2] = self.z
        set_world_verts(self.o, W)
        ch = np.abs(self.z - self.z0) > 1e-6
        return int(ch.sum()), round(float(np.abs(self.z - self.z0).max()), 3)


def op_hill(TE, T0, S):
    """ground_land OBJ_COLOR-07 (④ window) + support_ruin_observers RO-2: the crescent hill around the ruin scene
    (C5_researchers) and the ④ cube pits keeps its shape but its relief above the plain (z 0.9) is scaled x0.4 (soft
    knee), fading out towards the pine grove on its north-east crest and pinned under every object that stands on it.
    Around the ruin scene the ground is levelled to the scene's own base height for 2.6 units (25 pt) and blended
    into the lowered hill over the next 2.6 units, so no slope runs along its outline."""
    box = (38.0, 80.0, -42.0, -2.0)
    idx = TE.box(*box)
    z = TE.z[idx]; xy = TE.xy[idx]
    c, alpha, d0 = 0.9, 0.4, 0.25
    d = z - c
    f = np.where(d > 0, alpha * d + (1 - alpha) * d0 * (1 - np.exp(-np.maximum(d, 0) / d0)), d)
    zt = c + f
    fx = smoothstep(box[0], box[0] + 3, xy[:, 0]) * smoothstep(box[1], box[1] - 3, xy[:, 0])
    fy = smoothstep(box[2], box[2] + 3, xy[:, 1]) * smoothstep(box[3], box[3] - 3, xy[:, 1])
    grove = np.array((70.0, -12.0))
    fg = smoothstep(6.0, 14.0, np.linalg.norm(xy - grove, axis=1))
    w = fx * fy * fg
    target = z + w * (zt - z)
    # ruin scene: footprint raster + base height along its outline
    c5 = bpy.data.objects.get('C5_researchers')
    ring_info = None
    if c5 is not None:
        Wc = eval_world_verts(c5)
        tz = T0.zs(Wc[::3, :2]); sub = Wc[::3]
        cont = np.isfinite(tz) & (sub[:, 2] - tz > -0.6) & (sub[:, 2] - tz < 0.45)
        base = sub[cont]
        # footprint = cells covered by the projected (top-down) faces of the scene
        me = c5.data
        tri = []
        for p in me.polygons:
            v = list(p.vertices)
            for k in range(1, len(v) - 1):
                tri.append([v[0], v[k], v[k + 1]])
        tri = np.array(tri)
        Wl = world_verts(c5)
        fx0, fy0 = Wl[:, 0].min() - 0.2, Wl[:, 1].min() - 0.2
        nx = int((Wl[:, 0].max() + 0.2 - fx0) / CELL) + 2; ny = int((Wl[:, 1].max() + 0.2 - fy0) / CELL) + 2
        G = raster(Wl[tri], fx0, fy0, nx, ny, 'max')
        foot = np.isfinite(G)
        fj, fi = np.nonzero(foot)
        fcells = np.c_[fx0 + fi * CELL, fy0 + fj * CELL]
        edge = foot & ~erode(foot, 1)
        ej, ei = np.nonzero(edge)
        ecells = np.c_[fx0 + ei * CELL, fy0 + ej * CELL]
        rho = KD2(fcells).dists(xy)
        inside = np.zeros(len(xy), bool)
        ii = np.rint((xy[:, 0] - fx0) / CELL).astype(int); jj = np.rint((xy[:, 1] - fy0) / CELL).astype(int)
        ok = (ii >= 0) & (ii < nx) & (jj >= 0) & (jj < ny)
        inside[ok] = foot[jj[ok], ii[ok]]
        # base height at the outline: mean z of the base-contact vertices near each outline cell
        kb = KD2(base[:, :2])
        hz = np.empty(len(ecells))
        for n_, q in enumerate(ecells):
            res = kb.kd.find_n((q[0], q[1], 0.0), 6)
            hz[n_] = np.mean([base[i_, 2] for _, i_, _ in res])
        ke = KD2(ecells)
        near_e = np.array([ke.kd.find_n((p[0], p[1], 0.0), 4) for p in xy[rho < 6.0]], dtype=object)
        h_edge = np.full(len(xy), np.nan)
        h_edge[rho < 6.0] = [np.mean([hz[i_] for _, i_, _ in r]) for r in near_e]
        R1, R2 = 2.6, 5.2
        wr = 1.0 - smoothstep(R1, R2, rho)                 # 1 near the scene, 0 beyond R2
        ring = (~inside) & np.isfinite(h_edge) & (rho < R2)
        target[ring] = wr[ring] * (h_edge[ring] - 0.03) + (1 - wr[ring]) * target[ring]
        target[inside] = z[inside]
        ring_info = {'base_contact_vertices': int(len(base)), 'footprint_cells': int(foot.sum()),
                     'outline_base_z_min_med_max': np.round(np.percentile(hz, [0, 50, 100]), 3).tolist()}
    pins, names = ground_contacts(T0, box, exclude={'C5_researchers'}, overlay=False)
    dz = TE.blend_to(idx, target, TE.pin_weight(idx, pins))
    log('hill', {'vertices': int(len(idx)), 'lowered_max': round(float(-dz.min()), 3), 'raised_max': round(float(dz.max()), 3),
                 'pinned_objects': names, 'ruin_scene': ring_info})


def op_bench(TE, T0):
    """support_core5_lab OP-core5-01: the ground under the lab bench footprint (+0.4) is levelled to the bench's
    bottom (z_b - 0.01) and blended back over 1.6 units, so the bench no longer floats over the tilted ground."""
    b = need('R1_lab_bench'); Wb = world_verts(b); zb = float(Wb[:, 2].min())
    H = convex_hull(Wb[:, :2])
    lo = H.min(0) - 3; hi = H.max(0) + 3
    idx = TE.box(lo[0], hi[0], lo[1], hi[1])
    rho = poly_dist(TE.xy[idx], H)
    w = 1.0 - smoothstep(0.4, 2.0, rho)
    pins, names = ground_contacts(T0, (lo[0], hi[0], lo[1], hi[1]), exclude={'R1_lab_bench'}, overlay=False)
    dz = TE.blend_to(idx, np.full(len(idx), zb - 0.01), w * TE.pin_weight(idx, pins))
    log('bench', {'bench_bottom_z': round(zb, 3), 'vertices': int((np.abs(dz) > 1e-6).sum()), 'raised_max': round(float(dz.max()), 3),
                  'lowered_max': round(float(-dz.min()), 3), 'pinned_objects': names})


def cone_cap_points(TE, idx, src_xy, src_cap, shoulder, slope, radius):
    """cap(p) = min over sources s of src_cap(s) + slope * max(0, |p - s| - shoulder), sources within radius."""
    kd = KDTree(len(src_xy))
    for i, p in enumerate(src_xy):
        kd.insert((p[0], p[1], 0.0), i)
    kd.balance()
    cap = np.full(len(idx), np.inf)
    for n_, vi in enumerate(idx):
        x, y = TE.xy[vi]
        for co, i_, d in kd.find_range((x, y, 0.0), radius):
            v = src_cap[i_] + slope * max(0.0, d - shoulder)
            if v < cap[n_]:
                cap[n_] = v
    return cap


def op_bed_cap(TE, grids):
    """the ground stays 0.025 under the paving bed (joints show bed, not ground)."""
    tot = 0; mx = 0.0
    for g in grids:
        x1 = g.x0 + g.nx * CELL; y1 = g.y0 + g.ny * CELL
        idx = TE.box(g.x0, x1, g.y0, y1)
        b = g.at(TE.xy[idx], grow=2)
        ok = np.isfinite(b)
        dz = TE.cap(idx[ok], b[ok] - 0.025)
        tot += int((dz < -1e-6).sum()); mx = max(mx, float(-dz.min()) if len(dz) else 0.0)
    log('bed_cap', {'vertices_lowered': tot, 'max_drop': round(mx, 3)})


def plate_lift(F, T):
    """fields_* OP03 / FORM-15 / COLOR-24: wherever the ground comes within 0.03 of a field plate (or pokes through
    it), the plate's vertices around that spot are lifted until the plate clears the ground by 0.03 (dense samples
    on every face; two passes so shared vertices settle). The ground itself is not touched."""
    W = F.W.copy()
    fids = np.nonzero(F.kind[F.flab] == 'plate')[0]
    ij = np.array([(i, j) for i in range(5) for j in range(5 - i)], float) / 4.0
    bw = np.c_[1 - ij.sum(1), ij]
    lifted_total = np.zeros(len(W))
    for _ in range(2):
        need_up = np.zeros(len(W))
        for f in fids:
            v = F.lv[F.ls[f]:F.ls[f] + F.lt[f]]
            for k in range(1, len(v) - 1):
                tri = W[[v[0], v[k], v[k + 1]]]
                P = bw @ tri
                g = T.zs(P[:, :2])
                d = np.nanmax(g + 0.03 - P[:, 2]) if np.isfinite(g).any() else -1
                if d > 0:
                    for vi in (v[0], v[k], v[k + 1]):
                        need_up[vi] = max(need_up[vi], d)
        if not need_up.any():
            break
        W[:, 2] += need_up; lifted_total += need_up
    set_world_verts(F.o, W)
    F.load()
    lv_ = np.nonzero(lifted_total > 1e-6)[0]
    log('plate_lift', {'vertices_lifted': int(len(lv_)), 'max_lift': round(float(lifted_total.max()), 3),
                       'at_pt': F.S.project(F.W[lv_[np.argsort(-lifted_total[lv_])[:6]]]).round(1).tolist() if len(lv_) else []})


WATER_Z = -0.40
BRIDGE_PARTS = {'B_pons1', 'B_pons2', 'B_pons1_parapet0', 'B_pons1_parapet1', 'B_pons2_parapet0', 'B_pons2_parapet1'}


def op_bank_shift(TE, T0):
    """road_core_w OBJ_PLACE-11: south-east of the north bridge's south end the road's outer kerb hangs over the
    Tiber. The river bank there (all T_land vertices, so bank top, wall and hole edge move together) is pushed under
    the road by a smooth horizontal displacement towards the river, just far enough that the ground runs >= 0.5 past
    every road vertex (about 4.5 pt), fading to zero 2.4 units away and next to the bridge masonry."""
    road = need('R_core_road'); Wr = world_verts(road)
    br = need('B_pons1'); Wb = world_verts(br)
    Hb = convex_hull(Wb[Wb[:, 2] < 0.6, :2])
    box = (-45.5, -38.0, -11.5, -5.0)
    m = (Wr[:, 0] > box[0]) & (Wr[:, 0] < box[1]) & (Wr[:, 1] > box[2]) & (Wr[:, 1] < box[3])
    R = Wr[m]
    R = R[dist_to_hulls(R[:, :2], [Hb]) > 0.6]
    ang = np.linspace(0, 2 * np.pi, 12, endpoint=False)
    A = []
    for x, y, z in R:
        bad = not np.isfinite(T0.z(x, y))
        if not bad:
            for rr in (0.25, 0.5):
                if any(not np.isfinite(T0.z(x + rr * math.cos(a), y + rr * math.sin(a))) for a in ang):
                    bad = True; break
        if bad:
            A.append((x, y))
    if not A:
        log('bank_shift', {'road_vertices_near_water': 0}); return None
    A = np.unique(np.round(np.array(A), 4), axis=0)
    riv = world_verts(need('L02_tiber'))
    ca = A.mean(0)
    near = riv[np.linalg.norm(riv[:, :2] - ca, axis=1) < 3.0, :2]
    n = near.mean(0) - ca; n /= np.linalg.norm(n)
    D = None
    for D_ in np.arange(0.3, 2.01, 0.05):
        if all(np.isfinite(T0.z(*(a + (0.5 - D_) * n))) for a in A):
            D = round(float(D_), 2); break
    if D is None:
        log('bank_shift', {'result': 'no displacement <= 2.0 found', 'vertices': len(A)}); return None
    lo = A.min(0) - 3; hi = A.max(0) + 3
    idx = TE.box(lo[0], hi[0], lo[1], hi[1])
    dA = KD2(A).dists(TE.xy[idx])
    w = (1.0 - smoothstep(0.6, 2.4, dA)) * smoothstep(0.3, 1.2, dist_to_hulls(TE.xy[idx], [Hb]))
    TE.xy[idx] += (D * w)[:, None] * n[None, :]
    log('bank_shift', {'road_vertices_near_water': int(len(A)), 'direction': n.round(3).tolist(), 'displacement': D,
                       'terrain_vertices_moved': int((w > 1e-4).sum())})
    return (A, n)


def op_bank_fill(TE, grids, shifted):
    """... and under the road there the ground is raised to 0.05 under the paving bed (0.5 slope beyond it)."""
    if shifted is None:
        return
    A, n = shifted
    lo = A.min(0) - 2.5; hi = A.max(0) + 2.5
    idx = TE.box(lo[0], hi[0], lo[1], hi[1])
    best = np.full(len(idx), -np.inf)
    for g in grids:
        b = g.at(TE.xy[idx], grow=1)
        ok = np.isfinite(b)
        best[ok] = np.maximum(best[ok], b[ok] - 0.05)
    src = np.isfinite(best)
    if not src.any():
        return
    kd = KD2(TE.xy[idx][src]); bz = best[src]
    tgt = np.full(len(idx), -np.inf)
    for i_, p in enumerate(TE.xy[idx]):
        for co, j_, d in kd.kd.find_range((p[0], p[1], 0.0), 1.2):
            tgt[i_] = max(tgt[i_], bz[j_] - 0.5 * d)
    dA = KD2(A).dists(TE.xy[idx])
    wf = 1.0 - smoothstep(1.2, 2.6, dA)
    sel = (wf > 0) & np.isfinite(tgt) & (tgt > TE.z[idx]) & (TE.z[idx] > WATER_Z + 0.05)
    dz = np.where(sel, wf * (tgt - TE.z[idx]), 0.0)
    TE.z[idx] += dz
    log('bank_fill', {'vertices_raised': int(sel.sum()), 'max_raise': round(float(dz.max()), 3)})


def bridge_clamp(T):
    """bridge_* OBJ_PLACE-02: the abutments and end arches are seated on the bank instead of buried in it: every
    masonry vertex (arch spans and piers, not the deck) that lies more than 0.05 under the ground (over land) is
    lifted to ground - 0.05. Vertical pier edges collapse to zero height there; nothing above the ground moves."""
    res = {}
    for bn in ('B_pons1', 'B_pons2'):
        o = need(bn); W = world_verts(o)
        lab, flab, ls, lt, lv = islands(o)
        mas = np.isin(lab, [k for k in range(int(lab.max()) + 1) if W[lab == k, 2].min() < -0.5])
        g = T.zs(W[:, :2])
        want = np.where(mas & np.isfinite(g), g - 0.05, -np.inf)
        newz = np.maximum(W[:, 2], want)
        res[bn] = {'vertices_raised': int((newz > W[:, 2] + 1e-6).sum()), 'max_raise': round(float((newz - W[:, 2]).max()), 3)}
        W[:, 2] = newz
        set_world_verts(o, W)
    log('bridge_clamp', res)


def cliff_creases(TE):
    """ground_land OBJ_FORM-20: the edges between near-vertical faces (cliffs, quay and bank walls, the diorama
    skirt) and the gently sloping ground above are marked sharp, so the cliff faces no longer take the top
    surface's fan normals (vertical seams)."""
    me = TE.o.data
    fnz = np.empty(len(me.polygons) * 3); me.polygons.foreach_get('normal', fnz); fnz = np.abs(fnz.reshape(-1, 3)[:, 2])
    bm = bmesh.new(); bm.from_mesh(me)
    sharp = np.zeros(len(me.edges), bool)
    bm.edges.ensure_lookup_table()
    for e in bm.edges:
        fs = e.link_faces
        if len(fs) == 2:
            a, b = fnz[fs[0].index], fnz[fs[1].index]
            if min(a, b) < 0.35 and max(a, b) > 0.75:
                sharp[e.index] = True
    bm.free()
    a = me.attributes.get('sharp_edge')
    if a is None:
        a = me.attributes.new('sharp_edge', 'BOOLEAN', 'EDGE')
    cur = np.zeros(len(me.edges), bool); a.data.foreach_get('value', cur)
    a.data.foreach_set('value', cur | sharp)
    me.update()
    log('cliff_creases', {'edges_marked': int(sharp.sum())})


# ------------------------------------------------------------------ water
def tiber_mouth():
    """water_tiber FORM-18: the river-mouth part of L02_tiber that lies over the sea (L10_sea, z -0.70) drops to
    z -0.73, so the two water sheets no longer z-fight."""
    riv = need('L02_tiber'); sea = need('L10_sea')
    W = world_verts(riv)
    sb = bvh_from([sea])
    over = np.zeros(len(W), bool)
    for i, (x, y, z) in enumerate(W):
        if z > -0.66:
            continue
        hit = sb.ray_cast(Vector((x, y, 5.0)), Vector((0, 0, -1)))[0]
        if hit is not None and abs(hit.z - z) < 0.05:
            over[i] = True
    W[over, 2] = np.minimum(W[over, 2], -0.73)
    set_world_verts(riv, W)
    log('tiber_mouth', {'vertices_lowered': int(over.sum())})



def river_marks(S):
    """water_tiber OBJ_INFO-14a: the river's wave marks (straight lenses, deviation/length 0.05) take the sea marks'
    short-arc profile: each river island is lengthened x1.12 along its long axis and bent by a parabolic sag of
    0.20 x length, bowing the same way as most sea arcs (same K5m shape class)."""
    o = need('W_water_marks'); W = world_verts(o)
    lab, flab, ls, lt, lv = islands(o)
    rb = bvh_from([need('L02_tiber')]); sb = bvh_from([need('L10_sea')])
    n = int(lab.max()) + 1
    info = {'river': 0, 'sea': 0}
    geo = []
    for k in range(n):
        idx = np.nonzero(lab == k)[0]
        w = W[idx]; c = w.mean(0)
        hr = rb.ray_cast(Vector((c[0], c[1], c[2] + 1.0)), Vector((0, 0, -1)))[0]
        hs = sb.ray_cast(Vector((c[0], c[1], c[2] + 1.0)), Vector((0, 0, -1)))[0]
        body = 'river' if (hr is not None and (hs is None or hr.z >= hs.z - 1e-4)) else ('sea' if hs is not None else None)
        if body is None:
            continue
        q = w[:, :2] - c[:2]
        U, sv, Vt = np.linalg.svd(q, full_matrices=False)
        a = Vt[0]
        if a @ np.array((1.0, 1.0)) < 0:
            a = -a
        b = np.array((-a[1], a[0]))
        t = q @ a; u = q @ b
        L = float(np.ptp(t))
        mid = np.abs(t) < 0.2 * L
        sag = float(np.mean(u[mid]) - np.mean(u[~mid])) if mid.any() and (~mid).any() else 0.0
        geo.append((k, body, idx, c, a, b, t, u, L, sag))
    sea_sign = np.sign(np.median([g[9] for g in geo if g[1] == 'sea'])) if any(g[1] == 'sea' for g in geo) else 1.0
    if sea_sign == 0:
        sea_sign = 1.0
    for k, body, idx, c, a, b, t, u, L, sag in geo:
        info[body] += 1
        if body != 'river' or L <= 1e-6:
            continue
        t2 = t * 1.12; L2 = L * 1.12
        du = sea_sign * 0.20 * L2 * (1.0 - (2.0 * t2 / L2) ** 2)
        xy = c[:2] + np.outer(t2, a) + np.outer(u + du, b)
        W[idx, :2] = xy
    set_world_verts(o, W)
    # check the result on screen: deviation of the mid-line from the chord / chord length
    ratios = []
    W2 = world_verts(o)
    for k, body, idx, c, a, b, t, u, L, sag in geo:
        if body != 'river':
            continue
        P = S.project(W2[idx]); tt = (W2[idx, :2] - c[:2]) @ a
        e0 = P[np.argmin(tt)]; e1 = P[np.argmax(tt)]; ch = np.linalg.norm(e1 - e0)
        if ch < 1e-6:
            continue
        nrm = np.array((-(e1 - e0)[1], (e1 - e0)[0])) / ch
        dev = np.abs((P - e0) @ nrm).max()
        ratios.append(dev / ch)
    info['sea_bow_sign'] = float(sea_sign)
    info['river_dev_over_len_screen_p10_p50'] = np.round(np.percentile(ratios, [10, 50]), 3).tolist() if ratios else None
    log('river_marks', info)


# ------------------------------------------------------------------ main
def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    if not argv:
        raise SystemExit('usage: blender -b in.blend --factory-startup --python step.py -- out.blend [render_prefix]')
    out = Path(argv[0]).resolve(); src = Path(bpy.data.filepath).resolve()
    published = out.parent == OUT_DIR.resolve() and (out.exists() or re.fullmatch(r'roman_concrete_narrative_v\d+.*\.blend', out.name))
    if out == src or out.suffix != '.blend' or published:
        raise SystemExit(f'WE step: refusing to write {out}')
    t0 = time.time()
    for n in OWNED:
        need(n)
    skip = set(OWNED) | set(CREATED)
    fp0 = fingerprint(skip)
    S = Screen()
    modes = {n: restore_or_snapshot(need(n)) for n in OWNED}
    bpy.context.view_layer.update()
    log('restore', modes)
    T0 = terrain()                       # the original ground (restored)
    F = Fields(S)
    if on('fields'):
        fields_aqueduct(F, T0)
        fields_w_heat(F, T0, S)
        fields_sw_bank(F, T0, S)
        fields_nw_river(F, T0, S)
        fields_e_block(F, T0, S)
    grids = []
    if on('roads'):
        road_landing1(S)
        road_landing5(S)
        grids = build_bed(S)
        lower_road5_bed(grids)
    bpy.context.view_layer.update()
    if on('terrain'):
        TE = TerrainEdit()
        cliff_creases(TE)                # from the original ground: only the existing cliffs / walls get creases
        shifted = op_bank_shift(TE, T0) if on('roads') else None
        op_hill(TE, T0, S)
        op_bench(TE, T0)
        op_bank_fill(TE, grids, shifted)
        op_bed_cap(TE, grids)
        log('terrain_write', TE.write())
    bpy.context.view_layer.update()
    T1 = terrain()                       # the final ground
    if on('terrain'):
        bridge_clamp(T1)
    if on('fields'):
        plate_lift(F, T1)
    if on('water'):
        tiber_mouth()
        river_marks(S)
    if on('fields'):
        straw_fix(F, T1, S)
        straw_colour()
    bpy.context.view_layer.update()
    fp1 = fingerprint(skip)
    changed = sorted(n for n in fp0 if fp1.get(n) != fp0[n]) + sorted(set(fp1) - set(fp0) - skip)
    if changed:
        raise RuntimeError(f'WE step: objects outside WE ownership changed: {changed[:20]}')
    bpy.context.scene[MARK] = json.dumps({'ops': OPS})
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(out), copy=True)
    REP['input'] = str(src); REP['output'] = str(out); REP['seconds'] = round(time.time() - t0, 1)
    if len(argv) > 1:
        prefix = Path(argv[1]).resolve()
        H = runpy.run_path(str(NB / 'scripts/integrate_assets.py'), run_name='helpers')
        REP['render'] = H['render_two_pass'](prefix.with_suffix('.png'))
    rp = out.with_suffix('.we.json')
    rp.write_text(json.dumps(REP, ensure_ascii=False, indent=1, default=lambda x: x.tolist() if hasattr(x, 'tolist') else str(x)))
    print('WE_STEP done', REP['seconds'], 's')


if __name__ == '__main__':
    main()
