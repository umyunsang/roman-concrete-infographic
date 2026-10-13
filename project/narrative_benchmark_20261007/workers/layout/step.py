"""Layout step v8_13a (layout worker) - user request: "콜로세움이랑 도로랑 너무 가까워서 콜로세움을 위쪽으로 조금 이동",
keeping the earlier request: no road around the Colosseum may be hidden.

Only geometry/placement changes, no colour or material change (colouring is another worker's step):
 0. Colosseum group (COL_ruined, R3_colosseum_podium, R4_arena_skin) 14pt up the screen. The terrain pit the
    building stands in (T_land: flat floor 1 unit deep inside a flat ring) slides with it. Moving the building and
    podium over a fixed pit (scripts/user_v8_13.py) left the SE wall base and its buried scan debris floating over
    the pit and sank the podium into it; sliding the pit keeps every wall foot exactly where it was relative to the
    ground. Only flat ring vertices (z unchanged) are stretched, so the visible ground does not change.
 1. Pantheon (R8_pantheon) 34pt left / 30pt up the screen; its sloping new site is levelled (T_land terrace pad) so
    the plinth neither floats nor lets the ground show inside the portico.
 2. CORE 1 -> 2 north-west road (R_core_road): old stretch removed as in user_v8_13 s.2, re-paved along a smooth spline
    (ground radius >= 6) from the B_pons1 deck to the R1_road_landing1 plate, between the Pantheon and the raised wall
    top: 0.45-pitch / 0.49-wide paver boxes in running bond with 0.25-wide curbs.
 3. Podium outer edge pulled in per angle so its SCREEN silhouette stays >= 4pt from every other map object except the
    milestones (roads, fields, river, trees ...). user_v8_13 measured 4pt along the ground, which foreshortens to
    ~2.3pt on screen for the south road.
 4. Checks: road vertices hidden from the camera (ray test against every map object), Pantheon/road gap.

Run: Blender -b <in.blend> --factory-startup --python step.py -- <out.blend> [render_prefix]
Objects are found by name (clear error if missing). Deterministic; a scene marker makes a second run on its own
output a no-op. Never overwrites the input file and writes no .blend1 backup.
"""
import bpy, bmesh, math, json, sys, runpy
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
from bpy_extras.object_utils import world_to_camera_view

NB_WORK = Path('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work')
PROTECTED = {(NB_WORK / 'out' / f'roman_concrete_narrative_v8_{v}.blend').resolve() for v in ('10', '11', '12')}
MARK = 'rc_layout_v8_13a'
COL_UP_PT = 14.0                 # Colosseum group, screen points up
PAN_SHIFT_PT = (-34.0, -30.0)    # Pantheon, screen points (x right, y down)
PODIUM_CLEAR_PT = 4.0            # podium silhouette to any other object, on screen
SAMPLE_PT = 0.5                  # obstacle sampling (max error ~0.35pt) -> test against CLEAR + 0.45
W_PT, H_PT = 1191, 1684
OVERLAY = {'80_SHAPES', '81_NOSHADOW', '85_HEADER'}

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
if not argv:
    raise SystemExit('usage: blender -b <in.blend> --factory-startup --python step.py -- <out.blend> [render_prefix]')
SRC = Path(bpy.data.filepath).resolve()
OUT = Path(argv[0]).resolve()
PREFIX = Path(argv[1]).resolve() if len(argv) > 1 else None
if OUT == SRC or OUT in PROTECTED or OUT.suffix != '.blend':
    raise SystemExit(f'refusing to write {OUT} (input or protected file, or not .blend)')
bpy.context.preferences.filepaths.save_version = 0       # no .blend1 next to the output

sc = bpy.context.scene; O = bpy.data.objects
report = {'input': str(SRC), 'output': str(OUT)}


def need(name):
    o = O.get(name)
    if o is None:
        raise RuntimeError(f'layout step: object {name!r} not found in {SRC.name}')
    if o.type != 'MESH':
        raise RuntimeError(f'layout step: {name!r} is {o.type}, expected MESH')
    return o


# ---------------------------------------------------------------- screen / terrain helpers (as user_v8_13.py)
cam = sc.camera
frame = [cam.matrix_world @ v for v in cam.data.view_frame(scene=sc)]
origin = cam.matrix_world.translation.copy()
_dg = bpy.context.evaluated_depsgraph_get()
_P = cam.calc_matrix_camera(_dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
                            scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
_M = np.array(_P @ cam.matrix_world.inverted())


def to_pt(p):
    v = world_to_camera_view(sc, cam, p); return np.array((v.x * W_PT, (1 - v.y) * H_PT))


def project(W):
    W = np.asarray(W, float); H = np.c_[W, np.ones(len(W))] @ _M.T; n = H[:, :2] / H[:, 3:4]
    return np.c_[(n[:, 0] + 1) / 2 * W_PT, (1 - (n[:, 1] + 1) / 2) * H_PT]


_t = [Vector(p) for p in ((0, 0, 0), (-30, 40, 1), (25, -20, 0))]
assert np.abs(np.array([to_pt(p) for p in _t]) - project([p[:] for p in _t])).max() < 1e-3


def ray(pt):
    u, v = pt[0] / W_PT, 1 - pt[1] / H_PT
    tr, br, bl, tl = frame
    return origin, ((bl + (br - bl) * u + (tl - bl) * v) - origin).normalized()


def bvh_of(objs, owners=False):
    dg = bpy.context.evaluated_depsgraph_get(); verts, polys, own = [], [], []
    for o in objs:
        ev = o.evaluated_get(dg); me = ev.to_mesh(); mw = o.matrix_world; b = len(verts)
        verts += [mw @ v.co for v in me.vertices]; polys += [[b + i for i in p.vertices] for p in me.polygons]
        own += [o.name] * len(me.polygons); ev.to_mesh_clear()
    t = BVHTree.FromPolygons(verts, polys)
    return (t, own) if owners else t


def world_per_pt(p):
    r = cam.matrix_world.col[0].xyz.normalized()
    return 1.0 / np.linalg.norm(to_pt(p + r) - to_pt(p))


def wverts(o):
    co = np.empty(len(o.data.vertices) * 3); o.data.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    return (np.c_[co, np.ones(len(co))] @ np.array(o.matrix_world).T)[:, :3]


def set_wverts(o, W):
    co = (np.c_[W, np.ones(len(W))] @ np.array(o.matrix_world.inverted()).T)[:, :3]
    o.data.vertices.foreach_set('co', co.ravel()); o.data.update()


def screen_box(o, step=1):
    P = project(wverts(o)[::step])
    return [round(float(v), 1) for v in (P[:, 0].min(), P[:, 0].max(), P[:, 1].min(), P[:, 1].max())]


def inside_poly(poly, P):
    x, y = P[:, 0], P[:, 1]; res = np.zeros(len(P), bool); n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if y1 == y2: continue
        res ^= ((y1 > y) != (y2 > y)) & (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1)
    return res


def map_visible(include_overlay=False):
    vis = set()
    def walk(lc, hidden):
        c = lc.collection; h = hidden or lc.exclude or c.hide_render or (not include_overlay and c.name in OVERLAY)
        for o in c.objects:
            if not h and not o.hide_render and o.type == 'MESH': vis.add(o.name)
        for ch in lc.children: walk(ch, h)
    walk(bpy.context.view_layer.layer_collection, False)
    return [O[n] for n in sorted(vis)]


def sample_tris(o, roi, spacing=SAMPLE_PT):
    """screen points covering o's projected triangles (vertices, edges, interior), gaps <= spacing, inside roi."""
    dg = bpy.context.evaluated_depsgraph_get(); ev = o.evaluated_get(dg); me = ev.to_mesh(); me.calc_loop_triangles()
    co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    T = np.empty(len(me.loop_triangles) * 3, np.int32); me.loop_triangles.foreach_get('vertices', T)
    W = (np.c_[co, np.ones(len(co))] @ np.array(o.matrix_world).T)[:, :3]; ev.to_mesh_clear()
    if len(T) == 0: return np.zeros((0, 2))
    tri = project(W)[T.reshape(-1, 3)]; x0, x1, y0, y1 = roi
    tri = tri[(tri[:, :, 0].max(1) >= x0) & (tri[:, :, 0].min(1) <= x1) & (tri[:, :, 1].max(1) >= y0) & (tri[:, :, 1].min(1) <= y1)]
    if len(tri) == 0: return np.zeros((0, 2))
    n = np.clip(np.ceil(np.max(np.linalg.norm(tri - np.roll(tri, 1, axis=1), axis=2), axis=1) / spacing).astype(int), 1, 600)
    out = []
    for k in np.unique(n):
        ij = np.array([(i, j) for i in range(k + 1) for j in range(k + 1 - i)], float) / k
        out.append(np.einsum('wk,tkd->twd', np.c_[1 - ij.sum(1), ij], tri[n == k]).reshape(-1, 2))
    return np.concatenate(out)


def save_and_render():
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT), copy=True)
    report['saved'] = str(OUT)
    if PREFIX is not None:
        H = runpy.run_path(str(NB_WORK / 'scripts/integrate_assets.py'), run_name='helpers')
        report['render'] = H['render_two_pass'](PREFIX.with_suffix('.png'))
    print('REPORT ' + json.dumps(report, ensure_ascii=False))


# ---------------------------------------------------------------- idempotency
if sc.get(MARK):
    report['already_applied'] = json.loads(sc[MARK]); report['changed'] = False
    save_and_render(); raise SystemExit(0)

COL, POD, ARENA, LAND = need('COL_ruined'), need('R3_colosseum_podium'), need('R4_arena_skin'), need('T_land')
PAN, ROAD = need('R8_pantheon'), need('R_core_road')
ROADS = [ROAD, need('R_via_appia'), need('R_via_ostiensis')]
for o in (COL, POD, ARENA, LAND, PAN, ROAD):
    if o.data.users > 1: o.data = o.data.copy()
if len(POD.data.vertices) % 3:
    raise RuntimeError('R3_colosseum_podium: expected 3 vertices per angle (inner, outer top, outer lip)')

# ---------------------------------------------------------------- 0. Colosseum group up the screen, pit slides along
TER0 = bvh_of([LAND])
def tz0(x, y):
    h = TER0.ray_cast(Vector((x, y, 500)), Vector((0, 0, -1)))[0]; return h.z if h else 0.0
cw = wverts(COL)[::25]
cx, cy = (cw[:, 0].min() + cw[:, 0].max()) / 2, (cw[:, 1].min() + cw[:, 1].max()) / 2
cbase = Vector((cx, cy, tz0(cx, cy)))
o_, d_ = ray(to_pt(cbase) + np.array((0.0, -COL_UP_PT))); cnew = o_ + d_ * ((cbase.z - o_.z) / d_.z)
D = Vector((cnew.x - cbase.x, cnew.y - cbase.y, 0.0))
col_box0, pod_box0 = screen_box(COL, 25), screen_box(POD)
# screen shift where it matters: the label 802:78 next to the NE wall, and the south wall foot
CW_all = wverts(COL); CP = project(CW_all)
lab_c = np.array((730.5 + 51.1 / 2, 633.2 + 29.5 / 2))
i_lab = int(np.argmin(np.linalg.norm(CP - lab_c, axis=1)))
i_south = int(np.argmax(CP[:, 1]))
def shift_at(i):
    p = Vector(CW_all[i]); return [round(float(v), 2) for v in (to_pt(p + D) - to_pt(p))]
report['colosseum'] = {'D_world': [round(D.x, 4), round(D.y, 4), 0.0], 'D_len': round(D.length, 3),
                       'screen_shift_at_label_wall': shift_at(i_lab), 'label_wall_point_pt': [round(float(v), 1) for v in CP[i_lab]],
                       'screen_shift_at_south_foot': shift_at(i_south)}

# terrain pit: verts inside the podium's outer lip ring that lie below the flat ring around them
PW = wverts(POD); N = len(PW) // 3
LW = wverts(LAND)
lip0 = PW[2::3, :2]
bb = (LW[:, 0] > lip0[:, 0].min() - 10) & (LW[:, 0] < lip0[:, 0].max() + 10) & (LW[:, 1] > lip0[:, 1].min() - 10) & (LW[:, 1] < lip0[:, 1].max() + 10)
cand = np.nonzero(bb)[0]
in_lip = np.zeros(len(LW), bool); in_lip[cand] = inside_poly(lip0, LW[cand, :2])
ring_z = float(np.median(LW[in_lip, 2][LW[in_lip, 2] > cbase.z + 0.5]))
pit = in_lip & (LW[:, 2] < ring_z - 0.05)
if pit.sum() < 100:
    raise RuntimeError(f'T_land: expected a pit under the Colosseum, found {int(pit.sum())} vertices')
kd = KDTree(int(pit.sum()))
for i, p in enumerate(LW[pit]): kd.insert(Vector((p[0], p[1], 0.0)), i)
kd.balance()
dp = np.full(len(LW), np.inf)
for i in cand: dp[i] = kd.find(Vector((LW[i, 0], LW[i, 1], 0.0)))[2]
A_IN, B_OUT, FLAT_CHECK = 0.8, 5.5, 6.5     # w=1 up to 0.8 (covers every pit-edge triangle), 0 from 5.5
band = (~pit) & (dp < FLAT_CHECK)
nonflat = int((np.abs(LW[band, 2] - ring_z) > 1e-4).sum())
if nonflat:
    raise RuntimeError(f'T_land: ring around the Colosseum pit is not flat ({nonflat} vertices) - slide would show')
u = np.clip((B_OUT - dp) / (B_OUT - A_IN), 0, 1); w = u * u * (3 - 2 * u); w[pit] = 1.0
if 1.5 * D.length / (B_OUT - A_IN) >= 1:
    raise RuntimeError('Colosseum move too long for the flat ring (triangles would fold)')
LW2 = LW.copy(); LW2[:, 0] += w * D.x; LW2[:, 1] += w * D.y
# fold check on every triangle touching a moved vertex
LAND.data.calc_loop_triangles()
TT = np.empty(len(LAND.data.loop_triangles) * 3, np.int32); LAND.data.loop_triangles.foreach_get('vertices', TT); TT = TT.reshape(-1, 3)
mov = w > 0
tsel = TT[mov[TT].any(1)]
def sarea(X): a, b, c = X[tsel, :2].transpose(1, 0, 2); return (b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (b[:, 1] - a[:, 1]) * (c[:, 0] - a[:, 0])
ratio = sarea(LW2) / np.where(np.abs(sarea(LW)) < 1e-12, 1e-12, sarea(LW))
if ratio.min() <= 0.05:
    raise RuntimeError(f'T_land slide folds triangles (min area ratio {ratio.min():.3f})')
set_wverts(LAND, LW2)
report['terrain_pit'] = {'pit_verts': int(pit.sum()), 'ring_z': round(ring_z, 4), 'pit_floor_z': round(float(LW[pit, 2].min()), 4),
                         'band_verts_moved': int(((w > 0) & (w < 1)).sum()), 'flat_ring_checked_to': FLAT_CHECK,
                         'tri_area_ratio_min': round(float(ratio.min()), 3), 'tri_area_ratio_max': round(float(ratio.max()), 3)}
bpy.context.view_layer.update()
TER1 = bvh_of([LAND])
def tz(x, y):
    h = TER1.ray_cast(Vector((x, y, 500)), Vector((0, 0, -1)))[0]; return h.z if h else 0.0
def ground(pt):
    h = TER1.ray_cast(*ray(pt))[0]; assert h is not None, pt; return h

m = COL.matrix_world.copy(); m.translation += D; COL.matrix_world = m
for ob in (POD, ARENA):          # rigid over the moved pit, terrain-following on the outer ring
    Wo = wverts(ob); Wn = Wo.copy()
    for k, (x, y, z) in enumerate(Wo):
        nx, ny = x + D.x, y + D.y; Wn[k] = (nx, ny, tz(nx, ny) + (z - tz0(x, y)))
    set_wverts(ob, Wn)
bpy.context.view_layer.update()
dzs = []
for ob in (POD, ARENA):
    pass
report['colosseum'].update({'box_before': col_box0, 'box_after': screen_box(COL, 25),
                            'podium_box_before': pod_box0, 'podium_box_after': screen_box(POD)})

# ---------------------------------------------------------------- 1. Pantheon 34pt left / 30pt up
before_box = screen_box(PAN, 7)
pw = wverts(PAN)[::7]
base = Vector(((pw[:, 0].min() + pw[:, 0].max()) / 2, (pw[:, 1].min() + pw[:, 1].max()) / 2, pw[:, 2].min()))
o_, d_ = ray(to_pt(base) + np.array(PAN_SHIFT_PT)); nb = o_ + d_ * ((base.z - o_.z) / d_.z)
delta = nb - base; delta.z = tz(nb.x, nb.y) - tz(base.x, base.y)
m = PAN.matrix_world.copy(); m.translation += delta; PAN.matrix_world = m
bpy.context.view_layer.update()
report['pantheon'] = {'box_before': before_box, 'box_after': screen_box(PAN, 7),
                      'delta_world': [round(v, 4) for v in delta]}

# ---------------------------------------------------------------- 2. NW road re-laid (user_v8_13.py section 2)
road = ROAD
mw = road.matrix_world; inv = mw.inverted()
OLD = np.array([(300, 658), (320, 652), (340, 642.5), (360, 635), (380, 627), (400, 619), (420, 610), (440, 599.5),
                (460, 583), (480, 565), (500, 544), (520, 527.5), (540, 516.5)], float)
NEW = np.array([(300, 658), (320, 649), (340, 622), (360, 590), (380, 560), (390, 548), (400, 542), (410, 539),
                (420, 535), (430, 533), (440, 534), (460, 532), (480, 527), (500, 522), (520, 519), (540, 516.5)], float)
def densify(P, n=400):
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1); s = np.concatenate([[0], np.cumsum(seg)])
    u_ = np.linspace(0, s[-1], n); return np.stack([np.interp(u_, s, P[:, 0]), np.interp(u_, s, P[:, 1])], 1), u_
def smooth(P, it=3):
    for _ in range(it):   # Chaikin, ends fixed
        Q = [P[0]]
        for a, b in zip(P[:-1], P[1:]): Q += [0.75 * a + 0.25 * b, 0.25 * a + 0.75 * b]
        Q.append(P[-1]); P = np.array(Q)
    return P
def to_xy(P): return np.array([(lambda g: (g.x, g.y))(ground(p)) for p in P])
Cr, _ = densify(smooth(to_xy(OLD)), 600); Nr, _ = densify(smooth(to_xy(NEW)), 600)
bm = bmesh.new(); bm.from_mesh(road.data); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
seen = set(); islands = []
for f in bm.faces:
    if f.index in seen: continue
    st = [f]; seen.add(f.index); vs = set()
    while st:
        a_ = st.pop(); vs.update(v.index for v in a_.verts)
        for e in a_.edges:
            for g in e.link_faces:
                if g.index not in seen: seen.add(g.index); st.append(g)
    islands.append(sorted(vs))
bm.free()
WV = wverts(road)
def in_box(p):
    q = to_pt(Vector(p)); return 295 < q[0] < 545 and 480 < q[1] < 700
def nearest(C, p):
    return int(np.argmin(np.linalg.norm(C - p, axis=1)))
def tangents(C):
    T = np.gradient(C, axis=0); T /= np.linalg.norm(T, axis=1)[:, None]; return T, np.stack([-T[:, 1], T[:, 0]], 1)
Tr, Nrm = tangents(Cr)
pav = [isl for isl in islands if len(isl) <= 40 and in_box(WV[isl].mean(0))]
PC = np.array([WV[isl, :2].mean(0) for isl in pav])
idx = np.array([nearest(Cr, p) for p in PC]); lat = np.einsum('ij,ij->i', PC - Cr[idx], Nrm[idx])
off = np.full(len(Cr), np.nan)
for k in range(0, len(Cr), 5):
    mk = np.abs(idx - k) <= 8
    if mk.sum() >= 6: off[k] = (lat[mk].max() + lat[mk].min()) / 2
ok = ~np.isnan(off); xk = np.arange(len(Cr)); off = np.interp(xk, xk[ok], off[ok])
Kg = np.exp(-0.5 * (np.arange(-40, 41) / 15.0) ** 2); Kg /= Kg.sum(); off = np.convolve(np.pad(off, 40, mode='edge'), Kg, 'valid')
uu = xk / (len(Cr) - 1); taper = np.clip(np.minimum(uu, 1 - uu) / 0.08, 0, 1); taper = taper * taper * (3 - 2 * taper)
Co = Cr + Nrm * (off * taper)[:, None]
Cn = Co + (Nr - Cr)
To, No = tangents(Co); Tn, Nn = tangents(Cn)
so = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(Co, axis=0), axis=1))])
sn = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(Cn, axis=0), axis=1))])
ramp = lambda x: np.clip((x - 0.15) / 0.7, 0, 1) ** 2 * (3 - 2 * np.clip((x - 0.15) / 0.7, 0, 1))
report['nw_road'] = {'length_ratio': round(float(sn[-1] / so[-1]), 3), 'true_centre_offset_max': round(float(np.abs(off * taper).max()), 2)}
disp = np.linalg.norm(Nr - Cr, axis=1); mv = np.nonzero(disp > 0.04)[0]
i0, i1 = max(int(mv[0]) - 6, 1), min(int(mv[-1]) + 6, len(Co) - 2)
s0, s1 = so[i0], so[i1]
S0 = s0 + (sn[-1] - so[-1]) * ramp(s0 / so[-1]); S1 = s1 + (sn[-1] - so[-1]) * ramp(s1 / so[-1])
def old_s(p):
    i = nearest(Co, p); return so[i] + (p - Co[i]) @ To[i]
bm = bmesh.new(); bm.from_mesh(road.data); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
kill = set()
for isl in islands:
    c = WV[isl].mean(0)
    if len(isl) <= 40 and in_box(c) and s0 <= old_s(c[:2]) <= s1: kill.update(isl)
dead_f = [f for f in bm.faces if all(v.index in kill for v in f.verts)]
CURBV = {vi for isl in islands if len(isl) > 40 for vi in isl}
for f in bm.faces:
    if f.verts[0].index not in CURBV: continue
    wc = mw @ f.calc_center_median()
    if in_box(wc) and s0 <= old_s(np.array((wc.x, wc.y))) <= s1: dead_f.append(f)
report['nw_road']['old_faces_removed'] = len(dead_f)
bmesh.ops.delete(bm, geom=dead_f, context='FACES')
bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
def at(s_, l_):
    s_ = float(np.clip(s_, 0, sn[-1])); j = int(np.clip(np.searchsorted(sn, s_), 1, len(sn) - 1))
    f = (s_ - sn[j - 1]) / max(sn[j] - sn[j - 1], 1e-9)
    b_ = Cn[j - 1] + f * (Cn[j] - Cn[j - 1]); n = Nn[j - 1] + f * (Nn[j] - Nn[j - 1]); n /= np.linalg.norm(n)
    return b_ + n * l_
def V3(xy, dz):
    return bm.verts.new(inv @ Vector((xy[0], xy[1], tz(xy[0], xy[1]) + dz)))
def quad(vs, want):
    f = bm.faces.new(vs); f.normal_update()
    if f.normal.dot(want) < 0: f.normal_flip()
    return f
UP = (inv.to_3x3() @ Vector((0, 0, 1))).normalized()
rng = np.random.default_rng(1207)
PITCH = (S1 - S0) / max(1, round((S1 - S0) / 0.45)); UNIT, HALF = 0.49, 1.72
rows = int(round((S1 - S0) / PITCH)); n_pav = 0
for r in range(rows):
    sc_ = S0 + (r + 0.5) * PITCH; offs = (r % 2) * UNIT / 2
    for k in range(-6, 7):
        l0 = k * UNIT + offs - (UNIT - 0.035) / 2; l1 = l0 + UNIT - 0.035
        l0, l1 = max(l0, -HALF), min(l1, HALF)
        if l1 - l0 < 0.12: continue
        js, jl = rng.normal(0, 0.012, 2); top = 0.094 + rng.normal(0, 0.006)
        a_, b_ = sc_ - (PITCH - 0.035) / 2 + js, sc_ + (PITCH - 0.035) / 2 + js
        cs = [at(a_, l0 + jl), at(b_, l0 + jl), at(b_, l1 + jl), at(a_, l1 + jl)]
        T_ = [V3(c, top) for c in cs]; B_ = [V3(c, top - 0.068) for c in cs]
        quad(T_, UP)
        cen = sum((v.co for v in T_), Vector()) / 4
        for mm in range(4):
            o2 = (mm + 1) % 4; side = [T_[mm], T_[o2], B_[o2], B_[mm]]
            mid = (T_[mm].co + T_[o2].co) / 2; quad(side, (mid - cen).normalized())
        n_pav += 1
n_curb = 0
for sgn in (1, -1):
    steps = max(2, int((S1 - S0) / 0.15)); prevT = prevO = prevBI = prevBO = None
    for q_ in range(steps + 1):
        s_ = S0 + (S1 - S0) * q_ / steps
        pi, po = at(s_, sgn * HALF), at(s_, sgn * (HALF + 0.25))
        TI, TO = V3(pi, 0.13), V3(po, 0.13); BI, BO = V3(pi, 0.02), V3(po, -0.04)
        if prevT is not None:
            outward = Vector((*(po - pi), 0)); outward = (inv.to_3x3() @ outward).normalized()
            quad([prevT, TI, TO, prevO], UP)
            quad([prevT, TI, BI, prevBI], -outward)
            quad([prevO, TO, BO, prevBO], outward)
            n_curb += 3
        prevT, prevO, prevBI, prevBO = TI, TO, BI, BO
report['nw_road']['repaved'] = {'pavers': n_pav, 'rows': rows, 'pitch': round(float(PITCH), 3), 'curb_faces': n_curb,
                                'old_s': [round(float(s0), 2), round(float(s1), 2)], 'new_s': [round(float(S0), 2), round(float(S1), 2)]}
bm.to_mesh(road.data); bm.free()
road.data.update(); bpy.context.view_layer.update()

# ---------------------------------------------------------------- 3. podium edge >= 4pt (screen) from other objects
pm = POD.matrix_world
PW = wverts(POD)
ri, ro, rl = PW[0::3], PW[1::3], PW[2::3]
hgt_o = np.array([p[2] - tz(p[0], p[1]) for p in ro]); hgt_l = np.array([p[2] - tz(p[0], p[1]) for p in rl])
pb = screen_box(POD); roi = (pb[0] - 15, pb[1] + 15, pb[2] - 15, pb[3] + 15)
skip = {COL.name, POD.name, ARENA.name, LAND.name}
obst = [o for o in map_visible() if o.name not in skip]
pts, owner = [], []
for o in obst:
    s_ = sample_tris(o, roi)
    if len(s_): pts.append(s_); owner += [o.name] * len(s_)
pts = np.concatenate(pts)
KD = KDTree(len(pts))
for i, p in enumerate(pts): KD.insert(Vector((p[0], p[1], 0.0)), i)
KD.balance()
LIM = PODIUM_CLEAR_PT + 0.45
def edge_pts(k, t):
    """world points of the outer top and outer lip at angle k pulled in to fraction t."""
    a = ri[k, :2]
    xo, yo = a + t * (ro[k, :2] - a); xl, yl = a + t * (rl[k, :2] - a)
    return np.array(((xo, yo, tz(xo, yo) + hgt_o[k]), (xl, yl, tz(xl, yl) + hgt_l[k])))
def clearance(P3):
    return min(KD.find(Vector((q[0], q[1], 0.0)))[2] for q in project(P3))
T = np.ones(N); blockers = {}
for k in range(N):
    for t in np.linspace(1.0, 0.45, 111):
        if clearance(edge_pts(k, t)) >= LIM: T[k] = t; break
    else:
        T[k] = 0.45
    if T[k] < 1:
        q = project(edge_pts(k, 1.0)); nm = owner[KD.find(Vector((q[1][0], q[1][1], 0.0)))[1]]
        blockers[nm] = blockers.get(nm, 0) + 1
def smooth_env(T):
    Ts = T.copy(); K = np.exp(-0.5 * (np.arange(-6, 7) / 2.5) ** 2); K /= K.sum()
    for _ in range(6): Ts = np.minimum(T, np.convolve(np.concatenate([Ts[-6:], Ts, Ts[:6]]), K, 'valid'))
    return Ts
Ts = smooth_env(T)
for it in range(80):                      # straight edges between angles must clear too
    bad = set()
    E = [edge_pts(k, Ts[k]) for k in range(N)]
    for k in range(N):
        k2 = (k + 1) % N
        if Ts[k] > 0.999 and Ts[k2] > 0.999 and T[k] > 0.999 and T[k2] > 0.999 and clearance(E[k]) >= LIM + 3: continue
        for f in (0.25, 0.5, 0.75):
            if clearance(E[k] * (1 - f) + E[k2] * f) < LIM: bad.update((k, k2)); break
    if not bad: break
    for k in bad: T[k] = max(0.45, min(T[k], Ts[k]) - 0.01)
    Ts = smooth_env(T)
report['podium'] = {'angles': N, 'angles_clipped': int((Ts < 0.999).sum()), 't_min': round(float(Ts.min()), 3),
                    'edge_fix_iterations': it, 'clipped_because_of': blockers, 'obstacle_samples': len(pts)}
PWn = PW.copy()
for k in range(N):
    if Ts[k] > 0.999: continue
    e = edge_pts(k, Ts[k]); PWn[3 * k + 1] = e[0]; PWn[3 * k + 2] = e[1]
set_wverts(POD, PWn); bpy.context.view_layer.update()
q_ = project(np.array([edge_pts(k, Ts[k])[j] for k in range(N) for j in (0, 1)]))
report['podium']['screen_clearance_min_at_vertices'] = round(float(min(KD.find(Vector((p[0], p[1], 0)))[2] for p in q_)), 2)

# ---------------------------------------------------------------- 4. checks
blk = [o for o in map_visible() if o.name not in {r.name for r in ROADS} | {LAND.name}]
B, own = bvh_of(blk, owners=True)
BT = TER1
hidden = {}
for r in ROADS:
    W = wverts(r); per = {}; terr = 0
    for p in W:
        d = Vector(p) - origin; L = d.length; dn = d / L
        h = B.ray_cast(origin, dn, L - 0.05)
        if h[0] is not None: per[own[h[2]]] = per.get(own[h[2]], 0) + 1
        elif BT.ray_cast(origin, dn, L - 0.05)[0] is not None: terr += 1
    hidden[r.name] = {'by_objects': per, 'by_terrain_only': terr, 'vertices': len(W)}
report['roads_hidden'] = hidden
P = project(wverts(road))
PP = project(wverts(PAN)[::3])
gaps = []
for x0 in np.arange(PP[:, 0].min(), PP[:, 0].max(), 4.0):
    a_ = PP[(PP[:, 0] >= x0) & (PP[:, 0] < x0 + 4)]; r_ = P[(P[:, 0] >= x0) & (P[:, 0] < x0 + 4) & (P[:, 1] > 480) & (P[:, 1] < 700)]
    if len(a_) and len(r_): gaps.append(float(r_[:, 1].min() - a_[:, 1].max()))
report['pantheon']['road_min_column_gap_pt'] = round(min(gaps), 1) if gaps else None
# Pantheon footing: lowest ring of the model against the terrain under it
PWp = wverts(PAN); zmin = PWp[:, 2].min(); foot = PWp[PWp[:, 2] < zmin + 0.05]
rel = np.array([p[2] - tz(p[0], p[1]) for p in foot[::max(1, len(foot) // 400)]])
report['pantheon']['foot_minus_terrain'] = [round(float(rel.min()), 3), round(float(np.median(rel)), 3), round(float(rel.max()), 3)]

sc[MARK] = json.dumps({'col_up_pt': COL_UP_PT, 'pantheon_shift_pt': PAN_SHIFT_PT, 'podium_clear_pt': PODIUM_CLEAR_PT,
                       'D_world': report['colosseum']['D_world']})
report['changed'] = True
save_and_render()
