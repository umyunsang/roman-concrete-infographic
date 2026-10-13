"""v8.13: user requests — Colosseum 14pt up (more room to the south road), fields/furrows and roads coloured; the
v8.12 road work (no road hidden by the Colosseum, podium clear of roads) is redone for the new Colosseum position.

v8.12 notes (kept):

- South road: the travertine podium's outer lip lay over the road's upper half (x 550-775pt). Its outer edge is pulled
  in per angle so it stays 4pt clear of the road.
- North-west road (CORE 1 -> 2): about 85pt of it ran behind the Colosseum's tall north-west wall. It is re-laid
  between the Pantheon and the wall top. The Pantheon moves 30pt left and 14pt up to open that corridor (its label
  moves in Figma).
Run: blender -b out/roman_concrete_narrative_v8_11.blend --factory-startup --python scripts/user_v8_13.py -- <test|final> [test_prefix]
"""
import bpy, bmesh, math, json, sys, runpy
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'out/roman_concrete_narrative_v8_11.blend'
OUT = ROOT / 'out/roman_concrete_narrative_v8_13.blend'
argv = sys.argv[sys.argv.index('--') + 1:]
MODE = argv[0]
assert Path(bpy.data.filepath).resolve() == SRC.resolve()
W_PT, H_PT = 1191, 1684
sc = bpy.context.scene; cam = sc.camera; O = bpy.data.objects
report = {}

def to_pt(p):
    v = world_to_camera_view(sc, cam, p); return np.array((v.x * W_PT, (1 - v.y) * H_PT))
frame = [cam.matrix_world @ v for v in cam.data.view_frame(scene=sc)]
origin = cam.matrix_world.translation
def ray(pt):
    u, v = pt[0] / W_PT, 1 - pt[1] / H_PT
    tr, br, bl, tl = frame
    return origin, ((bl + (br - bl) * u + (tl - bl) * v) - origin).normalized()
dg = bpy.context.evaluated_depsgraph_get()
def bvh_of(objs):
    verts, polys = [], []
    for o in objs:
        ev = o.evaluated_get(dg); me = ev.to_mesh(); mw = o.matrix_world; b = len(verts)
        verts += [mw @ v.co for v in me.vertices]; polys += [[b + i for i in p.vertices] for p in me.polygons]
        ev.to_mesh_clear()
    return BVHTree.FromPolygons(verts, polys)
TERRAIN = bvh_of([O['T_land']])
def tz(x, y):
    h = TERRAIN.ray_cast(Vector((x, y, 500)), Vector((0, 0, -1)))[0]; return h.z if h else 0.0
def ground(pt):
    h = TERRAIN.ray_cast(*ray(pt))[0]; assert h is not None, pt; return h
def world_per_pt(p):
    r = cam.matrix_world.col[0].xyz.normalized()
    return 1.0 / np.linalg.norm(to_pt(p + r) - to_pt(p))
def screen_box(o, step=1):
    mw = o.matrix_world; P = np.array([to_pt(mw @ o.data.vertices[i].co) for i in range(0, len(o.data.vertices), step)])
    return [round(float(v), 1) for v in (P[:, 0].min(), P[:, 0].max(), P[:, 1].min(), P[:, 1].max())]
def occluded(road, blockers):
    """road vertices whose camera ray hits a blocker first, as screen points."""
    B = bvh_of(blockers); mw = road.matrix_world; hidden = []
    for v in road.data.vertices:
        p = mw @ v.co; d = p - origin; L = d.length
        if B.ray_cast(origin, d.normalized(), L - 0.05)[0] is not None: hidden.append(to_pt(p))
    return np.array(hidden)

# 0. Colosseum group 14pt up the screen (user: it sat too close to the south road). Rigid move for the building,
#    terrain-following move for the podium ring and the arena skin.
COLG = [O['COL_ruined'], O['R3_colosseum_podium'], O['R4_arena_skin']]
cw = np.array([O['COL_ruined'].matrix_world @ O['COL_ruined'].data.vertices[i].co for i in range(0, len(O['COL_ruined'].data.vertices), 25)])
cbase = Vector(((cw[:, 0].min() + cw[:, 0].max()) / 2, (cw[:, 1].min() + cw[:, 1].max()) / 2, tz((cw[:, 0].min() + cw[:, 0].max()) / 2, (cw[:, 1].min() + cw[:, 1].max()) / 2)))
o_, d_ = ray(to_pt(cbase) + np.array((0.0, -14.0))); t = (cbase.z - o_.z) / d_.z; cnew = o_ + d_ * t
CD = cnew - cbase; CD.z = 0.0
col_box0 = screen_box(O['COL_ruined'], 25)
m = O['COL_ruined'].matrix_world.copy(); m.translation += Vector((CD.x, CD.y, tz(cnew.x, cnew.y) - cbase.z)); O['COL_ruined'].matrix_world = m
for ob in COLG[1:]:
    if ob.data.users > 1: ob.data = ob.data.copy()
    mwo = ob.matrix_world; iv = mwo.inverted()
    for v in ob.data.vertices:
        w = mwo @ v.co; nx, ny = w.x + CD.x, w.y + CD.y
        v.co = iv @ Vector((nx, ny, tz(nx, ny) + (w.z - tz(w.x, w.y))))
    ob.data.update()
bpy.context.view_layer.update()
report['colosseum_box'] = [col_box0, screen_box(O['COL_ruined'], 25)]

# 1. Pantheon 34pt left / 30pt up (keeps 7pt+ from the CORE 1 milestone, opens a corridor above the raised wall)
pan = O['R8_pantheon']
before_box = screen_box(pan, 7)
pw = np.array([pan.matrix_world @ pan.data.vertices[i].co for i in range(0, len(pan.data.vertices), 7)])
base = Vector(((pw[:, 0].min() + pw[:, 0].max()) / 2, (pw[:, 1].min() + pw[:, 1].max()) / 2, pw[:, 2].min()))
o_, d_ = ray(to_pt(base) + np.array((-34.0, -30.0))); t = (base.z - o_.z) / d_.z; nb = o_ + d_ * t
delta = nb - base; delta.z = tz(nb.x, nb.y) - tz(base.x, base.y)
m = pan.matrix_world.copy(); m.translation += delta; pan.matrix_world = m
bpy.context.view_layer.update()
report['pantheon_box'] = [before_box, screen_box(pan, 7)]

# 2. NW road re-laid along a new screen centreline (vertices keep arc position and lateral offset)
road = O['R_core_road']
if road.data.users > 1: road.data = road.data.copy()
mw = road.matrix_world; inv = mw.inverted()
OLD = np.array([(300, 658), (320, 652), (340, 642.5), (360, 635), (380, 627), (400, 619), (420, 610), (440, 599.5),
                (460, 583), (480, 565), (500, 544), (520, 527.5), (540, 516.5)], float)
NEW = np.array([(300, 658), (320, 649), (340, 622), (360, 590), (380, 560), (390, 548), (400, 542), (410, 539),
                (420, 535), (430, 533), (440, 534), (460, 532), (480, 527), (500, 522), (520, 519), (540, 516.5)], float)
def frame_at(C, i):
    a, b = C[max(i - 1, 0)], C[min(i + 1, len(C) - 1)]; t = (b - a) / np.linalg.norm(b - a); return t, np.array((-t[1], t[0]))
def densify(P, n=400):
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1); s = np.concatenate([[0], np.cumsum(seg)])
    u = np.linspace(0, s[-1], n); return np.stack([np.interp(u, s, P[:, 0]), np.interp(u, s, P[:, 1])], 1), u
def smooth(P, it=3):
    for _ in range(it):   # Chaikin, ends fixed
        Q = [P[0]]
        for a, b in zip(P[:-1], P[1:]): Q += [0.75 * a + 0.25 * b, 0.25 * a + 0.75 * b]
        Q.append(P[-1]); P = np.array(Q)
    return P
# Ground-plane remap (a screen-space rotation of a foreshortened plane would shear the pavers). The road is 626
# separate paver boxes + 2 bed strips: pavers move rigidly (translate + turn), bed vertices follow the same map.
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
WV = np.array([(mw @ v.co)[:] for v in road.data.vertices])
def in_box(p):
    q = to_pt(Vector(p)); return 295 < q[0] < 545 and 480 < q[1] < 700
def nearest(C, p):
    return int(np.argmin(np.linalg.norm(C - p, axis=1)))
def tangents(C):
    T = np.gradient(C, axis=0); T /= np.linalg.norm(T, axis=1)[:, None]; return T, np.stack([-T[:, 1], T[:, 0]], 1)
# true middle of the paving: centre of the paver spread across the rough line, tapered to 0 at both ends
Tr, Nrm = tangents(Cr)
pav = [isl for isl in islands if len(isl) <= 40 and in_box(WV[isl].mean(0))]
PC = np.array([WV[isl, :2].mean(0) for isl in pav])
idx = np.array([nearest(Cr, p) for p in PC]); lat = np.einsum('ij,ij->i', PC - Cr[idx], Nrm[idx])
off = np.full(len(Cr), np.nan)
for k in range(0, len(Cr), 5):
    m = np.abs(idx - k) <= 8
    if m.sum() >= 6: off[k] = (lat[m].max() + lat[m].min()) / 2
ok = ~np.isnan(off); xk = np.arange(len(Cr)); off = np.interp(xk, xk[ok], off[ok])
Kg = np.exp(-0.5 * (np.arange(-40, 41) / 15.0) ** 2); Kg /= Kg.sum(); off = np.convolve(np.pad(off, 40, mode='edge'), Kg, 'valid')
u = xk / (len(Cr) - 1); taper = np.clip(np.minimum(u, 1 - u) / 0.08, 0, 1); taper = taper * taper * (3 - 2 * taper)
Co = Cr + Nrm * (off * taper)[:, None]
Cn = Co + (Nr - Cr)                                   # same designed displacement (zero at both ends)
To, No = tangents(Co); Tn, Nn = tangents(Cn)
so = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(Co, axis=0), axis=1))])
sn = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(Cn, axis=0), axis=1))])
ramp = lambda x: np.clip((x - 0.15) / 0.7, 0, 1) ** 2 * (3 - 2 * np.clip((x - 0.15) / 0.7, 0, 1))
def remap(p):
    """old ground point -> (new ground point, turn angle). Arc length is stretched only in the middle so both ends stay put."""
    i = nearest(Co, p); d = p - Co[i]; la, lo = d @ No[i], d @ To[i]
    s_old = so[i] + lo; s_new = s_old + (sn[-1] - so[-1]) * ramp(s_old / so[-1])
    j = int(np.clip(np.searchsorted(sn, s_new), 1, len(sn) - 1)); f = (s_new - sn[j - 1]) / max(sn[j] - sn[j - 1], 1e-9)
    base = Cn[j - 1] + f * (Cn[j] - Cn[j - 1]); t = Tn[j]; n = Nn[j]
    ang = math.atan2(t[1], t[0]) - math.atan2(To[i][1], To[i][0])
    return base + n * la, ang
report['nw_road_length_ratio'] = round(float(sn[-1] / so[-1]), 3); report['nw_true_centre_offset_max'] = round(float(np.abs(off * taper).max()), 2)
# Where the line moves, the old pavers (laid in a fan at the old sharp bend) cannot be re-used without wedge gaps, so
# that stretch is re-paved: rows of 0.42 x 0.455 pavers (measured from the straight part of this road: pitch 0.45,
# width 0.49, top 0.094 above ground, 0.068 thick) in running bond, with 0.25-wide curbs on both sides.
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
    if len(isl) <= 40:
        if in_box(c) and s0 <= old_s(c[:2]) <= s1: kill.update(isl)
dead_f = [f for f in bm.faces if all(v.index in kill for v in f.verts)]
CURBV = {vi for isl in islands if len(isl) > 40 for vi in isl}
for f in bm.faces:                                     # curb faces inside the stretch
    if f.verts[0].index not in CURBV: continue
    w = mw @ f.calc_center_median()
    if in_box(w) and s0 <= old_s(np.array((w.x, w.y))) <= s1: dead_f.append(f)
report['nw_old_faces_removed'] = len(dead_f)
bmesh.ops.delete(bm, geom=dead_f, context='FACES')
bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
def at(s_, l_):
    s_ = float(np.clip(s_, 0, sn[-1])); j = int(np.clip(np.searchsorted(sn, s_), 1, len(sn) - 1))
    f = (s_ - sn[j - 1]) / max(sn[j] - sn[j - 1], 1e-9)
    base = Cn[j - 1] + f * (Cn[j] - Cn[j - 1]); n = Nn[j - 1] + f * (Nn[j] - Nn[j - 1]); n /= np.linalg.norm(n)
    return base + n * l_
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
        for m in range(4):
            o2 = (m + 1) % 4; side = [T_[m], T_[o2], B_[o2], B_[m]]
            mid = (T_[m].co + T_[o2].co) / 2; quad(side, (mid - cen).normalized())
        n_pav += 1
n_curb = 0
for sgn in (1, -1):
    steps = max(2, int((S1 - S0) / 0.15)); prevT = prevI = prevO = prevBI = prevBO = None
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
report['nw_repaved'] = {'pavers': n_pav, 'rows': rows, 'pitch': round(float(PITCH), 3), 'curb_faces': n_curb,
                        'old_s': [round(float(s0), 2), round(float(s1), 2)], 'new_s': [round(float(S0), 2), round(float(S1), 2)]}
bm.to_mesh(road.data); bm.free()
road.data.update(); bpy.context.view_layer.update()

# 3. podium outer lip pulled in per angle, 4pt clear of the roads (vertex order per angle: inner, outer top, outer lip)
pod = O['R3_colosseum_podium']
if pod.data.users > 1: pod.data = pod.data.copy()
pm = pod.matrix_world; pinv = pm.inverted()
ROADS = bvh_of([road, O['R_via_appia']])
V = pod.data.vertices; N = len(V) // 3
ri = np.array([(pm @ V[3 * k].co)[:] for k in range(N)]); ro = np.array([(pm @ V[3 * k + 1].co)[:] for k in range(N)])
rl = np.array([(pm @ V[3 * k + 2].co)[:] for k in range(N)])
def clear(x, y):
    p = Vector((x, y, tz(x, y) + 0.05)); hit = ROADS.find_nearest(p)[0]
    if hit is None: return True
    return math.hypot(hit.x - x, hit.y - y) > 4 * world_per_pt(p)
T = np.ones(N)
for k in range(N):
    for t in np.linspace(1.0, 0.45, 56):
        x, y = ri[k, :2] + t * (rl[k, :2] - ri[k, :2])
        if clear(x, y): T[k] = t; break
    else: T[k] = 0.45
Ts = T.copy()
for _ in range(6):   # smooth envelope that never pushes the lip back over a road
    K = np.exp(-0.5 * (np.arange(-6, 7) / 2.5) ** 2); K /= K.sum()
    Ts = np.minimum(T, np.convolve(np.concatenate([Ts[-6:], Ts, Ts[:6]]), K, 'valid'))
for k in range(N):
    if Ts[k] > 0.999: continue
    for idx, src in ((3 * k + 1, ro[k]), (3 * k + 2, rl[k])):
        x, y = ri[k, :2] + Ts[k] * (src[:2] - ri[k, :2])
        hgt = src[2] - tz(src[0], src[1])
        V[idx].co = pinv @ Vector((x, y, tz(x, y) + hgt))
pod.data.update(); bpy.context.view_layer.update()
report['podium_angles_clipped'] = int((Ts < 0.999).sum()); report['podium_t_min'] = round(float(Ts.min()), 3)

# 4. check: no road vertex hidden by the Colosseum, its podium or the Pantheon
hid = occluded(road, [O['COL_ruined'], pod, pan])
report['road_vertices_hidden'] = len(hid)
if len(hid): report['hidden_box'] = [round(float(v)) for v in (hid[:, 0].min(), hid[:, 0].max(), hid[:, 1].min(), hid[:, 1].max())]
P = np.array([to_pt(mw @ v.co) for v in road.data.vertices])
for x0 in range(340, 560, 20):
    s = (P[:, 0] >= x0) & (P[:, 0] < x0 + 20) & (P[:, 1] < 700) & (P[:, 1] > 480)
    if s.sum(): report[f'nw_band_x{x0}'] = [round(float(P[s, 1].min())), round(float(P[s, 1].max()))]

# 4b. screen gap between the re-laid road and the Pantheon (per 4pt column, road top vs model bottom)
PP = np.array([to_pt(pan.matrix_world @ pan.data.vertices[i].co) for i in range(0, len(pan.data.vertices), 3)])
gaps = []
for x0 in np.arange(PP[:, 0].min(), PP[:, 0].max(), 4.0):
    a_ = PP[(PP[:, 0] >= x0) & (PP[:, 0] < x0 + 4)]; r_ = P[(P[:, 0] >= x0) & (P[:, 0] < x0 + 4) & (P[:, 1] > 480) & (P[:, 1] < 700)]
    if len(a_) and len(r_): gaps.append(float(r_[:, 1].min() - a_[:, 1].max()))
report['pantheon_road_min_gap_pt'] = round(min(gaps), 1) if gaps else None

# 5. colour (user request): roads = basalt pavers between light travertine curbs (as on the Via Appia); fields =
#    soil furrows + crop ridges by field, green vine stakes, straw bales
def mat(name, hexv, like='RC.v12.base_field'):
    m_ = bpy.data.materials.get(name) or bpy.data.materials[like].copy(); m_.name = name
    m_.diffuse_color = (*(((int(hexv[i:i + 2], 16) / 255 + 0.055) / 1.055) ** 2.4 for i in (1, 3, 5)), 1); return m_
def islands_of(me_):
    bm_ = bmesh.new(); bm_.from_mesh(me_); bm_.faces.ensure_lookup_table(); seen_ = set(); out_ = []
    for f in bm_.faces:
        if f.index in seen_: continue
        st = [f]; seen_.add(f.index); fs = []
        while st:
            a_ = st.pop(); fs.append(a_.index)
            for e in a_.edges:
                for g in e.link_faces:
                    if g.index not in seen_: seen_.add(g.index); st.append(g)
        out_.append(fs)
    bm_.free(); return out_
basalt = mat('RC.v12_13.road_basalt', '#9F998E', 'RC.v12.base_road_foundation')
n_pav = 0
for rn in ('R_core_road', 'R_via_appia', 'R_via_ostiensis'):
    ro_ = O[rn]
    if ro_.data.users > 1: ro_.data = ro_.data.copy()
    me_ = ro_.data
    if basalt.name not in [m_.name for m_ in me_.materials if m_]: me_.materials.append(basalt)
    bi = [m_.name for m_ in me_.materials].index(basalt.name)
    for fs in islands_of(me_):
        if len(fs) <= 40:
            for fi in fs: me_.polygons[fi].material_index = bi
            n_pav += 1
for rn in ('R1_road_landing1', 'R1_road_landing5'):
    for sl in O[rn].material_slots: sl.material = basalt
report['road_pavers_basalt'] = n_pav
FT = [('green', '#B39C79', '#A2AA7B'), ('wheat', '#BCA57F', '#CDB877'), ('young', '#B8A07C', '#B6BB8B'), ('fallow', '#A58E6F', '#B19B79')]
SOIL = [mat(f'RC.v12_13.field_soil_{k}', s_) for k, s_, c_ in FT]; CROP = [mat(f'RC.v12_13.field_crop_{k}', c_) for k, s_, c_ in FT]
MEADOW = [mat('RC.v12_13.field_meadow', '#B9BD90'), mat('RC.v12_13.field_stubble', '#C9B98B')]
VINE = mat('RC.v12_13.field_vine', '#879564'); STRAW = mat('RC.v12_13.field_straw', '#D0B97F')
fo = O['F_centuriatio']
if fo.data.users > 1: fo.data = fo.data.copy()
fme = fo.data; fmw = fo.matrix_world; fme.materials.clear()
ALL = SOIL + CROP + MEADOW + [VINE, STRAW]
for m_ in ALL: fme.materials.append(m_)
idx_of = {m_.name: i for i, m_ in enumerate(ALL)}
rng = np.random.default_rng(1307); counts = {'plates': 0, 'ridged': 0, 'stakes': 0, 'bales': 0}
mi = [0] * len(fme.polygons)
for fs in islands_of(fme):
    P_ = np.array([(fmw @ fme.vertices[v].co)[:] for fi in fs for v in fme.polygons[fi].vertices])
    ext = P_.max(0) - P_.min(0); major = max(ext[0], ext[1])
    if len(fs) == 12 and major < 0.5:
        for fi in fs: mi[fi] = idx_of[VINE.name]
        counts['stakes'] += 1; continue
    if len(fs) == 18 and major < 1.2:
        for fi in fs: mi[fi] = idx_of[STRAW.name]
        counts['bales'] += 1; continue
    counts['plates'] += 1
    tops = [fi for fi in fs if (fmw.to_3x3() @ fme.polygons[fi].normal).normalized().z > 0.3]
    zc = {fi: (fmw @ fme.polygons[fi].center).z for fi in tops}
    zr = (max(zc.values()) - min(zc.values())) if zc else 0
    k = int(rng.integers(0, len(FT)))
    if zr <= 0.03:     # flat plate, no furrows: pasture or stubble
        mm = MEADOW[int(rng.integers(0, 2))]
        for fi in fs: mi[fi] = idx_of[mm.name]
        continue
    counts['ridged'] += 1; zmid = min(zc.values()) + zr * 0.5
    for fi in fs:
        mi[fi] = idx_of[CROP[k].name] if (fi in zc and zc[fi] > zmid) else idx_of[SOIL[k].name]
fme.polygons.foreach_set('material_index', mi); fme.update()
report['fields'] = counts

print('REPORT ' + json.dumps(report, ensure_ascii=False))
H = runpy.run_path(str(ROOT / 'scripts/integrate_assets.py'), run_name='helpers')
if MODE == 'test':
    print('RENDER ' + json.dumps(H['render_two_pass'](Path(argv[1]).with_suffix('.png'))))
else:
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT), copy=False)
    r = H['render_two_pass'](ROOT / 'renders/narrative_v8_13_user.png'); report['render'] = r
    (ROOT / 'out/v8_13-user-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print('RENDER ' + json.dumps(r))

