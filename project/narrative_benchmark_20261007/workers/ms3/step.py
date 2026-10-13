"""MS3 step v8_13b (MS3 worker): move the ③④→⑤ milestone MS3_core34_to_5 along the edge of R_core_road so that
it no longer stands in front of the Colosseum podium SE edge on screen (v8_13: 397.8 pt² overlap).

Only the OBJECT TRANSFORM of MS3_core34_to_5 changes (location + rotation about z, scale kept). Its mesh is shared
with MS2_core2_to_34 and is not touched. No other object, mesh, material or setting is changed.

Placement model (all world units on the ground plane unless noted):
 * Road centreline of the ③④→⑤ stretch of R_core_road: guide polyline (screen points of v8_13, cast to T_land),
   re-centred on the paver boxes (islands < 40 faces) as (max lateral + min lateral)/2, smoothed. s = arc length
   toward ⑤, l = lateral offset (+ = left of travel, i.e. Colosseum side).
 * A candidate is (s, l) of the COLUMN AXIS. Rotation follows the road: theta = theta0 + (phi(s) - phi(s0)), where
   phi is the centreline heading, so the arrow keeps the same angle to the road it has now (it points toward ⑤).
 * Height: plinth bottom = lowest T_land height under the plinth footprint - EMBED, so no edge floats; the uphill
   burial (highest ground - bottom) is reported and limited (BURY_MAX).
 * Feasible when, on screen (pt, 1191 x 1684 frame, Screen class of workers/layout/common.py):
     - MS3 silhouette >= 4pt from COL_ruined / R3_colosseum_podium / R4_arena_skin,
     - >= 4pt from every other map object that is not road (fields, trees, buildings ...) and from the overlay pass
       shapes (core badges ③④/⑤, underlines) and from every Figma text box (review_loop/text_spec_r10.json),
     - road vertices hidden by MS3 (camera ray hits MS3 before the vertex) <= the count at the original place,
     - the column stands at the road edge like now: column axis outside the paved lane (|l| >= paving half width)
       and the plinth still reaching the kerb (|l| - plinth half size <= kerb outer edge),
     - burial <= BURY_MAX, the arrow still points toward ⑤ on screen.
   Silhouette distances: MS3 triangles sampled (<= 0.2pt) into a 0.25pt grid; boundary cells vs KD trees of the
   obstacle triangles sampled at 0.3pt; conservative gap = distance - 0.4pt.
 * Candidates are visited in order of increasing move distance of the column axis; the first feasible one wins
   (coarse 0.25 grid, then refined at 0.05 around it).

Run: Blender -b <in.blend> --factory-startup --python step.py -- <out.blend> [render_prefix]
Refuses to write onto the input file or onto an existing file in nb_work/out/. Writes no .blend1.
Idempotent: the scene marker keeps MS3's original matrix; a rerun on its own output restores it and recomputes,
which gives the same pose (deterministic). If MS3 was moved by something else after this step, it stops.
"""
import bpy, json, sys, runpy, math, hashlib, os, time
from pathlib import Path
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

NB_WORK = Path('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work')
sys.path.insert(0, str(NB_WORK / 'workers' / 'layout'))
from common import Screen, need, world_verts, bvh_of, Terrain, map_visible_objects, overlay_objects, sample_tris  # noqa: E402

MS_NAME = 'MS3_core34_to_5'
MARK = 'rc_ms3_v8_13b'
TEXT_SPEC = NB_WORK / 'review_loop' / 'text_spec_r10.json'
OUT_DIR = (NB_WORK / 'out').resolve()
CLEAR_PT = 4.0          # required screen gap
GRID = 0.25             # pt, occupancy grid
OBST_SPACING = 0.3      # pt, obstacle triangle sampling
MS_SPACING = 0.2        # pt, MS3 triangle sampling (at the original pose)
GAP_SLACK = 0.4         # pt, sampling/grid error subtracted from measured distances
EMBED = 0.04            # world, plinth bottom below the lowest ground under it
BURY_MAX = 0.30         # world, max ground height above the plinth bottom (plinth is 0.86 high)
ARROW_TO_5_MAX_DEG = 60.0
S_RANGE = 30.0          # world, search range along the road each way
# guide polyline of the ③④→⑤ stretch (screen pt, v8_13): from the ③④ side, past MS3, up the branch to landing ⑤
GUIDE_PT = [(560, 1010), (640, 1003), (700, 994), (760, 989), (800, 983), (835, 972), (860, 955), (880, 932),
            (900, 908), (920, 888), (936, 876)]
ROAD_PREFIX = ('R_', 'R1_', 'R4_bridge', 'B_pons')
COLG = ('COL_ruined', 'R3_colosseum_podium', 'R4_arena_skin')
T0 = time.time()

# ---------------------------------------------------------------- arguments / output protection
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
if not argv:
    raise SystemExit('usage: blender -b <in.blend> --factory-startup --python step.py -- <out.blend> [render_prefix]')
SRC = Path(bpy.data.filepath).resolve()
OUT = Path(argv[0]).resolve()
PREFIX = Path(argv[1]).resolve() if len(argv) > 1 else None
PROBE = os.environ.get('MS3_PROBE')      # debug: write the candidate table there and do not save
if OUT.suffix != '.blend' or OUT == SRC or (OUT.parent == OUT_DIR and OUT.exists()) or \
        (OUT.parent == OUT_DIR and OUT.name.startswith('roman_concrete_narrative_v') and
         any(p.name == OUT.name for p in OUT_DIR.glob('*.blend*'))):
    raise SystemExit(f'refusing to write {OUT} (input file, existing out/ version file, or not .blend)')
if 'Mobile Documents' in str(OUT) or str(OUT).startswith(str(Path.home() / 'Documents')):
    raise SystemExit(f'refusing to write into the iCloud Documents tree: {OUT}')
bpy.context.preferences.filepaths.save_version = 0

sc = bpy.context.scene
O = bpy.data.objects
report = {'step': 'ms3_v8_13b', 'input': str(SRC), 'output': str(OUT)}


def r_(v, n=3):
    return [round(float(x), n) for x in v] if hasattr(v, '__len__') else round(float(v), n)


# ---------------------------------------------------------------- fingerprints (prove nothing else changed)
def mesh_fp(me):
    h = hashlib.sha256()
    for label, coll, field, width, dt in (('v', me.vertices, 'co', 3, np.float32), ('e', me.edges, 'vertices', 2, np.int32),
                                          ('l', me.loops, 'vertex_index', 1, np.int32),
                                          ('ps', me.polygons, 'loop_start', 1, np.int32),
                                          ('pm', me.polygons, 'material_index', 1, np.int32)):
        a = np.empty(len(coll) * width, dt); coll.foreach_get(field, a)
        h.update(label.encode()); h.update(str(len(coll)).encode()); h.update(a.tobytes())
    return h.hexdigest()[:16]


def object_fp(o):
    h = hashlib.sha256()
    h.update(np.array(o.matrix_world, np.float64).round(6).tobytes())
    h.update(json.dumps([o.hide_render, o.hide_viewport, [c.name for c in o.users_collection],
                         [s.material.name if s.material else None for s in o.material_slots],
                         o.data.name if o.data else None]).encode())
    if o.type == 'MESH':
        h.update(mesh_fp(o.data).encode())
    return h.hexdigest()[:16]


def scene_fp():
    return {o.name: object_fp(o) for o in sorted(O, key=lambda x: x.name)}


# ---------------------------------------------------------------- idempotency: restore the original pose first
MS = need(MS_NAME)
if MS.parent is not None or MS.constraints or MS.rotation_mode != 'XYZ' or abs(MS.rotation_euler.x) > 1e-6 or abs(MS.rotation_euler.y) > 1e-6:
    raise RuntimeError(f'{MS_NAME}: expected an unparented object rotated about z only')
prev = json.loads(sc[MARK]) if sc.get(MARK) else None
if prev is not None:
    cur = np.array(MS.matrix_world).ravel()
    if np.abs(cur - np.array(prev['new_matrix'])).max() > 1e-4:
        raise RuntimeError(f'{MS_NAME} was moved after this step ran (matrix differs from the marker); refusing to guess')
    MS.matrix_world = Matrix(np.array(prev['orig_matrix']).reshape(4, 4).tolist())
    bpy.context.view_layer.update()
    report['rerun'] = 'marker found: original MS3 pose restored, pose recomputed'
FP_BEFORE = scene_fp()
M0 = np.array(MS.matrix_world)
LOC0 = np.array(MS.matrix_world.translation)
TH0 = float(MS.rotation_euler.z)
SCL = np.array(MS.scale)

# ---------------------------------------------------------------- screen, terrain, local MS3 geometry
S = Screen()
LAND = need('T_land'); TER = Terrain(LAND)
ROAD = need('R_core_road')
me = MS.data
LV = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', LV); LV = LV.reshape(-1, 3)
slots = [s.material.name if s.material else '' for s in MS.material_slots]
def slot_idx(sub):
    k = [i for i, n in enumerate(slots) if sub in n]
    if not k: raise RuntimeError(f'{MS_NAME}: no material slot containing {sub!r} ({slots})')
    return k[0]
K_STONE, K_PLINTH, K_ARROW = slot_idx('milestone_stone'), slot_idx('roman_plinth'), slot_idx('direction_arrow')
me.calc_loop_triangles()
TRI = np.empty(len(me.loop_triangles) * 3, np.int32); me.loop_triangles.foreach_get('vertices', TRI); TRI = TRI.reshape(-1, 3)
TMAT = np.empty(len(me.loop_triangles), np.int32); me.loop_triangles.foreach_get('material_index', TMAT)
PMAT = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', PMAT)
POLYS = [tuple(p.vertices) for p in me.polygons]
LS = LV * SCL                                   # scaled local coordinates (rotation/translation per candidate)
def vset(k):
    return np.array(sorted({v for p, m in zip(POLYS, PMAT) if m == k for v in p}))
stone_v, plinth_v, arrow_v = vset(K_STONE), vset(K_PLINTH), vset(K_ARROW)
COL_OFF = np.array(((LS[stone_v, 0].min() + LS[stone_v, 0].max()) / 2, (LS[stone_v, 1].min() + LS[stone_v, 1].max()) / 2))
pz = LS[plinth_v, 2]; bot = LS[plinth_v][pz < pz.min() + 0.01 * SCL[2]]
PL_HALF = float(max(np.abs(LS[plinth_v, 0] - COL_OFF[0]).max(), np.abs(LS[plinth_v, 1] - COL_OFF[1]).max()))
PL_H = float(pz.max() - pz.min())
if abs(pz.min()) > 1e-4:
    raise RuntimeError(f'{MS_NAME}: plinth bottom is not at local z=0 ({pz.min()})')
# plinth footprint samples (scaled local xy): bottom ring + interior grid inside its convex hull
def hull(P):
    P = np.unique(P.round(6), axis=0); P = P[np.lexsort((P[:, 1], P[:, 0]))]
    def half(Q):
        h = []
        for q in Q:
            while len(h) >= 2 and (h[-1][0] - h[-2][0]) * (q[1] - h[-2][1]) - (h[-1][1] - h[-2][1]) * (q[0] - h[-2][0]) <= 0: h.pop()
            h.append(q)
        return h
    return np.array(half(P)[:-1] + half(P[::-1])[:-1])
HULL = hull(bot[:, :2])
gx, gy = np.meshgrid(np.linspace(HULL[:, 0].min(), HULL[:, 0].max(), 13), np.linspace(HULL[:, 1].min(), HULL[:, 1].max(), 13))
G = np.c_[gx.ravel(), gy.ravel()]
inside = np.ones(len(G), bool)
for i in range(len(HULL)):
    a, b = HULL[i], HULL[(i + 1) % len(HULL)]
    inside &= (b[0] - a[0]) * (G[:, 1] - a[1]) - (b[1] - a[1]) * (G[:, 0] - a[0]) >= -1e-9
FOOT = np.r_[HULL, G[inside]]


def rotz(t):
    c, s_ = math.cos(t), math.sin(t); return np.array(((c, -s_), (s_, c)))


def world_of(P3, th, loc):
    R = np.eye(3); R[:2, :2] = rotz(th)
    return P3 @ R.T + loc


# MS3 triangle samples in scaled-local 3D, dense enough for <= MS_SPACING pt gaps at the original pose
P0 = S.project(world_of(LS, TH0, LOC0))
tri0 = P0[TRI]
Lmax = np.max(np.linalg.norm(tri0 - np.roll(tri0, 1, axis=1), axis=2), axis=1)
kk = np.clip(np.ceil(Lmax / MS_SPACING).astype(int), 1, 200)
SAMP, SAMP_ARROW = [], []
for k in np.unique(kk):
    sel = kk == k
    ij = np.array([(i, j) for i in range(k + 1) for j in range(k + 1 - i)], float) / k
    w = np.c_[1 - ij.sum(1), ij]
    pts = np.einsum('wk,tkd->twd', w, LS[TRI[sel]])
    SAMP.append(pts.reshape(-1, 3)); SAMP_ARROW.append(np.repeat(TMAT[sel] == K_ARROW, len(w)))
SAMP = np.concatenate(SAMP); SAMP_ARROW = np.concatenate(SAMP_ARROW)
# arrow axis (scaled local): tail -> tip along the plate's long horizontal axis; tip = narrowing end
A = LS[arrow_v]; ac = A[:, :2].mean(0); _, _, Vt = np.linalg.svd(A[:, :2] - ac); ax = Vt[0]
t_ = (A[:, :2] - ac) @ ax
def zext(m): return A[m, 2].max() - A[m, 2].min()
span = t_.max() - t_.min()
if zext(t_ > t_.max() - 0.06 * span) > zext(t_ < t_.min() + 0.06 * span): ax = -ax
ARROW_AX = ax                                   # local unit vector, tail -> tip
ARROW_C = np.r_[ac, A[:, 2].mean()]
report['ms3_model'] = {'scale': r_(SCL, 4), 'column_axis_local_scaled': r_(COL_OFF), 'plinth_half_size': round(PL_HALF, 3),
                       'plinth_height': round(PL_H, 3), 'arrow_axis_local': r_(ARROW_AX, 4), 'samples': int(len(SAMP))}

# ---------------------------------------------------------------- road centreline (③④ -> ⑤ stretch)
def ground_pt(pt):
    o, d = S.ray(np.array(pt, float)); h = TER.bvh.ray_cast(o, d)[0]
    if h is None: raise RuntimeError(f'guide point {pt} misses T_land')
    return np.array((h.x, h.y))


def densify(P, n):
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1); s_ = np.r_[0, np.cumsum(seg)]; u = np.linspace(0, s_[-1], n)
    return np.stack([np.interp(u, s_, P[:, 0]), np.interp(u, s_, P[:, 1])], 1)


def tangents(C):
    T = np.gradient(C, axis=0); T /= np.linalg.norm(T, axis=1)[:, None]; return T, np.stack([-T[:, 1], T[:, 0]], 1)


def islands(o):
    import bmesh
    bm = bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
    seen = set(); out = []
    for f in bm.faces:
        if f.index in seen: continue
        st = [f]; seen.add(f.index); vs = set(); nf = 0
        while st:
            a = st.pop(); nf += 1; vs.update(v.index for v in a.verts)
            for e in a.edges:
                for g in e.link_faces:
                    if g.index not in seen: seen.add(g.index); st.append(g)
        out.append((np.array(sorted(vs)), nf))
    bm.free(); return out


C = densify(np.array([ground_pt(p) for p in GUIDE_PT]), 900)
Tg, Ng = tangents(C)
RW = world_verts(ROAD)
ISL = islands(ROAD)
PAV = [vs for vs, nf in ISL if nf < 40]; KERB = [vs for vs, nf in ISL if nf >= 40]
PC = np.array([RW[vs, :2].mean(0) for vs in PAV])


def nearest_param(P, C_, step=1):
    Cs = C_[::step]
    out_i = np.empty(len(P), int)
    for a in range(0, len(P), 2000):
        d = np.linalg.norm(P[a:a + 2000, None, :] - Cs[None], axis=2); out_i[a:a + 2000] = d.argmin(1) * step
    return out_i


box = (PC[:, 0] > C[:, 0].min() - 6) & (PC[:, 0] < C[:, 0].max() + 6) & (PC[:, 1] > C[:, 1].min() - 6) & (PC[:, 1] < C[:, 1].max() + 6)
PCb = PC[box]; ib = nearest_param(PCb, C); lb = np.einsum('ij,ij->i', PCb - C[ib], Ng[ib])
okb = np.abs(lb) < 3.5
off = np.full(len(C), np.nan)
for k in range(len(C)):
    m = okb & (np.abs(ib - k) <= 6)
    if m.sum() >= 5: off[k] = (lb[m].max() + lb[m].min()) / 2
gd = ~np.isnan(off)
if gd.mean() < 0.9:
    raise RuntimeError(f'R_core_road pavers do not follow the ③④→⑤ guide line ({gd.mean():.2f} covered) - road changed?')
xk = np.arange(len(C)); off = np.interp(xk, xk[gd], off[gd])
Kg = np.exp(-0.5 * (np.arange(-30, 31) / 10.0) ** 2); Kg /= Kg.sum(); off = np.convolve(np.pad(off, 30, mode='edge'), Kg, 'valid')
if np.abs(off).max() > 1.6:
    raise RuntimeError(f'R_core_road centre is {np.abs(off).max():.2f} off the guide line - road changed?')
CL = densify(C + Ng * off[:, None], 900)
TL, NL = tangents(CL)
SL = np.r_[0, np.cumsum(np.linalg.norm(np.diff(CL, axis=0), axis=1))]
PHI = np.unwrap(np.arctan2(TL[:, 1], TL[:, 0]))
# paving half width / kerb edges from the meshes along this stretch
pv_all = np.concatenate([RW[vs, :2] for vs, b_ in zip(PAV, box) if b_])
ip = nearest_param(pv_all, CL, 3); lp = np.einsum('ij,ij->i', pv_all - CL[ip], NL[ip])
lp = lp[(np.abs(lp) < 3.0) & (ip > 10) & (ip < len(CL) - 10)]
kv = np.concatenate([RW[vs, :2] for vs in KERB])
kv = kv[(kv[:, 0] > CL[:, 0].min() - 4) & (kv[:, 0] < CL[:, 0].max() + 4) & (kv[:, 1] > CL[:, 1].min() - 4) & (kv[:, 1] < CL[:, 1].max() + 4)]
ik = nearest_param(kv, CL, 3); lk = np.einsum('ij,ij->i', kv - CL[ik], NL[ik])
dk_ = np.linalg.norm(kv - CL[ik], axis=1)
lk = lk[(np.abs(lk) < 3.0) & (ik > 10) & (ik < len(CL) - 10) & (dk_ < 3.0)]
PAVE_HALF = float(np.percentile(np.abs(lp), 99))
KERB_OUT = float(np.percentile(np.abs(lk), 99))
report['road'] = {'centreline_length': round(float(SL[-1]), 3), 'guide_offset_max': round(float(np.abs(off).max()), 3),
                  'paving_half_width_p99': round(PAVE_HALF, 3), 'kerb_outer_p99': round(KERB_OUT, 3),
                  'kerb_inner_p1': round(float(np.percentile(np.abs(lk), 1)), 3)}


def at_s(s_):
    s_ = float(np.clip(s_, 0, SL[-1])); j = int(np.clip(np.searchsorted(SL, s_), 1, len(SL) - 1))
    f = (s_ - SL[j - 1]) / max(SL[j] - SL[j - 1], 1e-9)
    c = CL[j - 1] + f * (CL[j] - CL[j - 1]); n = NL[j - 1] + f * (NL[j] - NL[j - 1]); n /= np.linalg.norm(n)
    return c, n, PHI[j - 1] + f * (PHI[j] - PHI[j - 1])


def s_l_of(p):
    i = int(np.linalg.norm(CL - p, axis=1).argmin())
    s_ = SL[i] + (p - CL[i]) @ TL[i]
    c, n, _ = at_s(s_); return float(s_), float((p - c) @ n)


COLC0 = LOC0[:2] + rotz(TH0) @ COL_OFF
S0, L0 = s_l_of(COLC0)
_, _, PHI0 = at_s(S0)
report['original'] = {'location': r_(LOC0, 4), 'rot_z_deg': round(math.degrees(TH0), 3), 'column_axis_xy': r_(COLC0, 3),
                      's': round(S0, 3), 'l': round(L0, 3), 'road_heading_deg': round(math.degrees(PHI0), 2),
                      'arrow_heading_deg': round(math.degrees(TH0 + math.atan2(ARROW_AX[1], ARROW_AX[0])), 2)}


def pose(s_, l_):
    c, n, ph = at_s(s_)
    th = TH0 + (ph - PHI0)
    colc = c + n * l_
    xy = colc - rotz(th) @ COL_OFF
    F = FOOT @ rotz(th).T + xy
    tz = np.array([TER.z(x, y) for x, y in F])
    zb = float(tz.min() - EMBED)
    return {'s': float(s_), 'l': float(l_), 'th': th, 'loc': np.array((xy[0], xy[1], zb)), 'colc': colc,
            'bury_max': float(tz.max() - zb), 'bury_min': float(tz.min() - zb), 'ground_range': float(tz.max() - tz.min())}


# ---------------------------------------------------------------- obstacles on screen
ROI_PAD = 140.0
b0 = (P0[:, 0].min() - ROI_PAD, P0[:, 0].max() + ROI_PAD, P0[:, 1].min() - ROI_PAD, P0[:, 1].max() + ROI_PAD)
ROI = (max(b0[0], 0.0), min(b0[1], 1191.0), max(b0[2], 0.0), min(b0[3], 1684.0))
NX, NY = int(math.ceil((ROI[1] - ROI[0]) / GRID)) + 1, int(math.ceil((ROI[3] - ROI[2]) / GRID)) + 1


def cells(P):
    ix = np.floor((P[:, 0] - ROI[0]) / GRID).astype(np.int64); iy = np.floor((P[:, 1] - ROI[2]) / GRID).astype(np.int64)
    ok = (ix >= 0) & (ix < NX) & (iy >= 0) & (iy < NY)
    return ix[ok], iy[ok], ok


def is_road(n):
    return n.startswith(ROAD_PREFIX) and n not in COLG


mapobj = [o for o in map_visible_objects() if o.name not in (MS_NAME, LAND.name)]
groups = {'colosseum': [o for o in mapobj if o.name in COLG],
          'objects': [o for o in mapobj if o.name not in COLG and not is_road(o.name)],
          'overlay': overlay_objects()}
missing = [n for n in COLG if n not in {o.name for o in groups['colosseum']}]
if missing:
    raise RuntimeError(f'Colosseum group objects not rendered: {missing}')
OBST = {}
for g, objs in groups.items():
    pts, own = [], []
    for o in objs:
        dg = bpy.context.evaluated_depsgraph_get(); ev = o.evaluated_get(dg); m_ = ev.to_mesh(); m_.calc_loop_triangles()
        co = np.empty(len(m_.vertices) * 3); m_.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
        tri = np.empty(len(m_.loop_triangles) * 3, np.int32); m_.loop_triangles.foreach_get('vertices', tri)
        ev.to_mesh_clear()
        if len(tri) == 0: continue
        Wo = (np.c_[co, np.ones(len(co))] @ np.array(o.matrix_world).T)[:, :3]
        sp = sample_tris(S.project(Wo), tri.reshape(-1, 3), ROI, OBST_SPACING)
        if len(sp): pts.append(sp); own += [o.name] * len(sp)
    if not pts:
        OBST[g] = None; continue
    pts = np.concatenate(pts); own = np.array(own)
    kd = KDTree(len(pts))
    for i, p in enumerate(pts): kd.insert((p[0], p[1], 0.0), i)
    kd.balance()
    grid = np.zeros((NY, NX), bool); ix, iy, ok = cells(pts); grid[iy, ix] = True
    OBST[g] = {'kd': kd, 'grid': grid, 'own': own[ok], 'own_all': own, 'n': len(pts), 'ix': ix, 'iy': iy}
spec = json.loads(TEXT_SPEC.read_text())
TEXTS = [(t[0], t[1]) for t in spec['texts']]
TXT = np.array([b for _, b in TEXTS], float)            # x, y, w, h
report['obstacles'] = {g: (None if v is None else {'objects': sorted(set(v['own_all'].tolist())), 'samples': v['n']}) for g, v in OBST.items()}
report['obstacles']['texts'] = len(TEXTS)

# ---------------------------------------------------------------- road vertices for the hidden-vertex count
ROADOBJS = [o for o in map_visible_objects() if is_road(o.name)]
RV = np.concatenate([world_verts(o) for o in ROADOBJS]); RV_OWN = np.concatenate([[o.name] * len(o.data.vertices) for o in ROADOBJS])
RP = S.project(RV)
ORIGIN = np.array(S.origin)


def ms_bvh(th, loc):
    Wm = world_of(LS, th, loc)
    return BVHTree.FromPolygons([Vector(p) for p in Wm], POLYS), Wm


def hidden_count(th, loc, Wp):
    B, _ = ms_bvh(th, loc)
    x0, x1, y0, y1 = Wp[:, 0].min() - 1, Wp[:, 0].max() + 1, Wp[:, 1].min() - 1, Wp[:, 1].max() + 1
    cand = np.nonzero((RP[:, 0] > x0) & (RP[:, 0] < x1) & (RP[:, 1] > y0) & (RP[:, 1] < y1))[0]
    per = {}
    for i in cand:
        d = Vector(RV[i] - ORIGIN); L = d.length; d /= L
        if B.ray_cast(Vector(ORIGIN), d, L - 0.05)[0] is not None:
            per[RV_OWN[i]] = per.get(RV_OWN[i], 0) + 1
    return sum(per.values()), per


# ---------------------------------------------------------------- evaluate one pose on screen
def rect_dist(P):
    """min distance from points P to the text boxes (0 inside), and the box index."""
    best, bi = np.inf, -1
    for k, (x, y, w, h) in enumerate(TXT):
        dx = np.maximum(np.maximum(x - P[:, 0], P[:, 0] - (x + w)), 0); dy = np.maximum(np.maximum(y - P[:, 1], P[:, 1] - (y + h)), 0)
        d = float(np.sqrt(dx * dx + dy * dy).min())
        if d < best: best, bi = d, k
    return best, bi


def screen_eval(ps, full=False):
    Wsm = world_of(SAMP, ps['th'], ps['loc'])
    Psm = S.project(Wsm)
    ix, iy, ok = cells(Psm)
    if not ok.all():
        return {'inside_roi': False}
    x0, y0 = ix.min() - 1, iy.min() - 1
    occ = np.zeros((iy.max() - y0 + 2, ix.max() - x0 + 2), bool); occ[iy - y0, ix - x0] = True
    inner = occ.copy()
    inner[1:-1, 1:-1] = occ[1:-1, 1:-1] & occ[:-2, 1:-1] & occ[2:, 1:-1] & occ[1:-1, :-2] & occ[1:-1, 2:]
    inner[0, :] = inner[-1, :] = False; inner[:, 0] = inner[:, -1] = False
    by, bx = np.nonzero(occ & ~inner)
    BP = np.c_[ROI[0] + (bx + x0 + 0.5) * GRID, ROI[2] + (by + y0 + 0.5) * GRID]
    res = {'inside_roi': True, 'area_pt2': float(occ.sum() * GRID * GRID)}
    for g, ob in OBST.items():
        if ob is None:
            res[g] = {'gap': 99.0}; continue
        sub = ob['grid'][y0:y0 + occ.shape[0], x0:x0 + occ.shape[1]]
        ov = occ[:sub.shape[0], :sub.shape[1]] & sub
        if ov.any():
            res[g] = {'gap': 0.0, 'overlap_pt2': float(ov.sum() * GRID * GRID)}
            if full:
                sel = (ob['ix'] - x0 >= 0) & (ob['iy'] - y0 >= 0) & (ob['ix'] - x0 < occ.shape[1]) & (ob['iy'] - y0 < occ.shape[0])
                hit = sel.copy(); hit[sel] = occ[ob['iy'][sel] - y0, ob['ix'][sel] - x0]
                res[g]['with'] = sorted(set(ob['own'][hit].tolist()))
            continue
        best, who = np.inf, -1
        for p in BP:
            _, i, d = ob['kd'].find((p[0], p[1], 0.0))
            if d < best: best, who = d, i
        res[g] = {'gap': max(0.0, best - GAP_SLACK)}
        if full: res[g]['nearest'] = str(ob['own_all'][who])
    dt, bi = rect_dist(BP)
    inside_txt = any(((Psm[:, 0] >= x) & (Psm[:, 0] <= x + w) & (Psm[:, 1] >= y) & (Psm[:, 1] <= y + h)).any() for x, y, w, h in TXT
                     if x < Psm[:, 0].max() and x + w > Psm[:, 0].min() and y < Psm[:, 1].max() and y + h > Psm[:, 1].min())
    res['texts'] = {'gap': 0.0 if inside_txt else max(0.0, dt - GAP_SLACK), 'nearest': TEXTS[bi][0]}
    # arrow: screen direction tail->tip, visible plate area
    Ah = world_of(np.array([ARROW_C - np.r_[ARROW_AX, 0] * 2.0 / SCL[0] * SCL[0], ARROW_C + np.r_[ARROW_AX, 0] * 2.0]), ps['th'], ps['loc'])
    Ap = S.project(Ah); dv = Ap[1] - Ap[0]
    res['arrow_dir_pt'] = (dv / np.linalg.norm(dv)).tolist()
    res['arrow_tip_pt'] = Ap[1].tolist()
    am = SAMP_ARROW[ok]
    acc = np.zeros_like(occ); acc[iy[am] - y0, ix[am] - x0] = True
    res['arrow_area_pt2'] = float(acc.sum() * GRID * GRID)
    res['box'] = [float(Psm[:, 0].min()), float(Psm[:, 0].max()), float(Psm[:, 1].min()), float(Psm[:, 1].max())]
    return res


# target for "points toward ⑤": the ⑤ landing plate centre (R1_road_landing5) on screen
L5 = need('R1_road_landing5'); L5P = S.project(world_verts(L5)).mean(0)


def arrow_angle_to_5(res):
    d = np.array(res['arrow_dir_pt']); tgt = L5P - np.array(res['arrow_tip_pt'])
    return math.degrees(math.acos(float(np.clip(d @ tgt / np.linalg.norm(tgt), -1, 1))))


# ---------------------------------------------------------------- baseline (original pose)
base_pose = {'s': S0, 'l': L0, 'th': TH0, 'loc': LOC0.copy(), 'colc': COLC0}
F0 = FOOT @ rotz(TH0).T + LOC0[:2]; tz0 = np.array([TER.z(x, y) for x, y in F0])
base_pose.update({'bury_max': float(tz0.max() - LOC0[2]), 'bury_min': float(tz0.min() - LOC0[2]), 'ground_range': float(tz0.max() - tz0.min())})
base_scr = screen_eval(base_pose, full=True)
print(f'[ms3] baseline screen {time.time() - T0:.1f}s', flush=True)
HID0, HID0_PER = hidden_count(TH0, LOC0, S.project(world_of(SAMP, TH0, LOC0)))
base_scr['arrow_angle_to_5_deg'] = arrow_angle_to_5(base_scr)
report['original'].update({'screen': base_scr, 'hidden_road_vertices': HID0, 'hidden_per_object': HID0_PER,
                           'plinth_bottom_minus_ground': [round(-base_pose['bury_max'], 3), round(-base_pose['bury_min'], 3)]})
ARROW_AREA0 = base_scr['arrow_area_pt2']

L_MIN = PAVE_HALF                    # column axis outside the paved lane (on the kerb or beyond)
L_MAX = KERB_OUT + PL_HALF           # plinth still reaches the kerb outer edge
side0 = 1.0 if L0 > 0 else -1.0
report['constraints'] = {'clear_pt': CLEAR_PT, 'column_axis_abs_l': [round(L_MIN, 3), round(L_MAX, 3)],
                         'bury_max_world': BURY_MAX, 'embed_world': EMBED, 'arrow_to_5_max_deg': ARROW_TO_5_MAX_DEG,
                         'hidden_road_vertices_max': HID0, 'search_s_range': S_RANGE}

table = []


def evaluate(s_, l_, need_hidden=True):
    if not (L_MIN <= abs(l_) <= L_MAX) or s_ < 0 or s_ > SL[-1]:
        return None
    ps = pose(s_, l_)
    rec = {'s': round(s_, 3), 'l': round(l_, 3), 'move': float(np.linalg.norm(ps['colc'] - COLC0)),
           'bury_max': round(ps['bury_max'], 3), 'dtheta_deg': round(math.degrees(ps['th'] - TH0), 2)}
    fail = []
    if ps['bury_max'] > BURY_MAX: fail.append('bury')
    scr = screen_eval(ps)
    if not scr['inside_roi']:
        fail.append('roi'); rec['fail'] = fail; table.append(rec); return rec
    for g in ('colosseum', 'objects', 'overlay', 'texts'):
        rec[g] = round(scr[g]['gap'], 2)
        if scr[g]['gap'] < CLEAR_PT: fail.append(g)
    ang = arrow_angle_to_5(scr); rec['arrow_to_5'] = round(ang, 1)
    if ang > ARROW_TO_5_MAX_DEG: fail.append('arrow_dir')
    rec['arrow_area_ratio'] = round(scr['arrow_area_pt2'] / ARROW_AREA0, 3)
    if not fail and need_hidden:
        h, per = hidden_count(ps['th'], ps['loc'], None if False else S.project(world_of(SAMP, ps['th'], ps['loc'])))
        rec['hidden'] = h
        if h > HID0: fail.append('hidden')
    rec['fail'] = fail; table.append(rec)
    rec['_pose'] = ps
    if len(table) % 50 == 0:
        print(f'[ms3] evaluated {len(table)}  {time.time() - T0:.1f}s  last s={s_:.2f} l={l_:.2f} fail={fail}', flush=True)
    return rec


def search(s_vals, l_vals):
    C_ = sorted(((float(np.linalg.norm(pose_xy(s_, l_) - COLC0)), s_, l_) for s_ in s_vals for l_ in l_vals
                 if L_MIN <= abs(l_) <= L_MAX), key=lambda t: (round(t[0], 6), t[1], t[2]))
    for d, s_, l_ in C_:
        rec = evaluate(s_, l_)
        if rec is not None and not rec['fail']:
            return rec
    return None


def pose_xy(s_, l_):
    c, n, _ = at_s(s_); return c + n * l_


# coarse: both sides of the road, along +-S_RANGE; visit by move distance
coarse_s = np.round(np.arange(max(0.0, S0 - S_RANGE), min(SL[-1], S0 + S_RANGE) + 1e-9, 0.25), 4)
coarse_l = np.round(np.r_[np.arange(-L_MAX, -L_MIN + 1e-9, 0.25), np.arange(L_MIN, L_MAX + 1e-9, 0.25), L0], 4)
FORCE = os.environ.get('MS3_FORCE')      # debug: "ds,l" relative to the original place, skips the search
if FORCE:
    _ds, _l = [float(v) for v in FORCE.split(',')]
    best = evaluate(S0 + _ds, _l); best['forced'] = FORCE
else:
    best = search(coarse_s, coarse_l)
if best is None:
    raise RuntimeError('no feasible MS3 place along R_core_road within the search range')
coarse_best = {k: v for k, v in best.items() if k != '_pose'}
# refine around it: everything within the coarse step that is closer to the original place
fs = np.round(np.arange(best['s'] - 0.3, best['s'] + 0.3 + 1e-9, 0.05), 4)
fl = np.round(np.arange(best['l'] - 0.3, best['l'] + 0.3 + 1e-9, 0.05), 4)
fine = None if FORCE else search(fs, fl)
if fine is not None and fine['move'] < best['move']:
    best = fine
report['search'] = {'coarse_best': coarse_best, 'evaluated': len(table), 'seconds': round(time.time() - T0, 1)}
if PROBE:
    Path(PROBE).write_text(json.dumps({'report': report, 'table': [{k: v for k, v in t.items() if k != '_pose'} for t in table]},
                                      ensure_ascii=False, indent=1, default=float))
    print('PROBE written', PROBE); raise SystemExit(0)

# ---------------------------------------------------------------- apply
ps = best['_pose']
R3 = Matrix.Rotation(ps['th'], 4, 'Z')
MS.matrix_world = Matrix.Translation(Vector(ps['loc'])) @ R3 @ Matrix.Diagonal(Vector((*SCL, 1.0)))
bpy.context.view_layer.update()
if abs(MS.rotation_euler.z - ps['th']) > 1e-5 and abs((MS.rotation_euler.z - ps['th']) % (2 * math.pi)) > 1e-5:
    raise RuntimeError('rotation not applied as expected')

# ---------------------------------------------------------------- checks on the applied pose
fin_scr = screen_eval(ps, full=True)
fin_scr['arrow_angle_to_5_deg'] = arrow_angle_to_5(fin_scr)
HID1, HID1_PER = hidden_count(ps['th'], ps['loc'], S.project(world_of(SAMP, ps['th'], ps['loc'])))
Wf = world_verts(MS)
pl_w = Wf[plinth_v]; botw = pl_w[pl_w[:, 2] < pl_w[:, 2].min() + 0.01]
rel = np.array([p[2] - TER.z(p[0], p[1]) for p in botw])
report['result'] = {
    'location': r_(ps['loc'], 4), 'rot_z_deg': round(math.degrees(ps['th']), 3), 'dtheta_deg': round(math.degrees(ps['th'] - TH0), 3),
    'road_heading_deg': round(math.degrees(at_s(ps['s'])[2]), 2), 's': round(ps['s'], 3), 'l': round(ps['l'], 3),
    'move_column_axis_world': round(best['move'], 3),
    'move_column_axis_pt': r_(S.to_pt(Vector((*ps['colc'], ps['loc'][2]))) - S.to_pt(Vector((*COLC0, LOC0[2]))), 2),
    'move_screen_box_pt': r_(np.array(fin_scr['box']) - np.array(base_scr['box']), 2),
    'screen': fin_scr, 'hidden_road_vertices': HID1, 'hidden_per_object': HID1_PER,
    'footing': {'plinth_bottom_z': round(float(ps['loc'][2]), 4), 'bottom_ring_minus_ground_min_med_max':
                [round(float(rel.min()), 3), round(float(np.median(rel)), 3), round(float(rel.max()), 3)],
                'ground_range_under_plinth': round(ps['ground_range'], 3), 'max_burial': round(ps['bury_max'], 3),
                'plinth_height': round(PL_H, 3), 'max_burial_fraction': round(ps['bury_max'] / PL_H, 3)},
    'arrow_area_ratio': round(fin_scr['arrow_area_pt2'] / ARROW_AREA0, 3),
}
FP_AFTER = scene_fp()
changed = sorted(n for n in FP_AFTER if FP_BEFORE.get(n) != FP_AFTER[n])
added = sorted(set(FP_AFTER) - set(FP_BEFORE)); removed = sorted(set(FP_BEFORE) - set(FP_AFTER))
if changed != [MS_NAME] or added or removed or mesh_fp(MS.data) != mesh_fp(need('MS2_core2_to_34').data):
    raise RuntimeError(f'unexpected changes: changed={changed} added={added} removed={removed}')
KEEP = ['R_core_road', 'R_via_appia', 'R_via_ostiensis', 'T_land', 'COL_ruined', 'R3_colosseum_podium', 'R4_arena_skin',
        'R1_road_landing5', 'R1_road5_bed', 'MS2_core2_to_34', 'MS1_core1_to_2', 'F_centuriatio']
report['invariance'] = {'objects_compared': len(FP_AFTER), 'changed_objects': changed,
                        'ms3_mesh_sha': mesh_fp(MS.data), 'unchanged_hashes': {n: FP_AFTER[n] for n in KEEP if n in FP_AFTER}}
sc[MARK] = json.dumps({'orig_matrix': np.array(M0).ravel().tolist(), 'new_matrix': np.array(MS.matrix_world).ravel().tolist(),
                       'clear_pt': CLEAR_PT, 's': round(ps['s'], 4), 'l': round(ps['l'], 4)})
report['seconds'] = round(time.time() - T0, 1)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT), copy=True)
report['saved'] = str(OUT)
if PREFIX is not None:
    H = runpy.run_path(str(NB_WORK / 'scripts' / 'integrate_assets.py'), run_name='helpers')
    report['render'] = H['render_two_pass'](PREFIX.with_suffix('.png'))
    PREFIX.with_name(PREFIX.name + '_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=1, default=float))
print('REPORT ' + json.dumps(report, ensure_ascii=False, default=float))
