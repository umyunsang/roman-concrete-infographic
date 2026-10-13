"""WD1 step (wave 1, large landmarks) - object review round 11 fixes on v8_14.

Owned objects: COL_ruined, R3_colosseum_podium, R4_arena_skin, R8_pantheon, D2_lime_kiln, L05_aqua_claudia,
L01_* (8 Apennine peaks), L07_vesuvius, L08_pompeii. Nothing else is touched (fingerprint check before saving).

Run: Blender -b <in.blend> --factory-startup --python step.py -- <out.blend> [render_prefix]
Refuses to write the input file or any existing file in nb_work/out/. Idempotent: a scene marker turns a second run on
its own output into a verified no-op; every geometric decision is recomputed from the blend it runs on (terrain heights
are ray-cast at run time, objects are found by name).
"""
import bpy, bmesh, sys, json, math, os, runpy
from pathlib import Path
import numpy as np
from mathutils import Vector, Matrix

HERE = Path('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/WD1')
NB = HERE.parents[1]
sys.path.insert(0, str(HERE))
import wd1lib as L  # noqa: E402

MARK = 'rc_wd1_wave1'
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
if not argv:
    raise SystemExit('usage: Blender -b <in.blend> --factory-startup --python step.py -- <out.blend> [render_prefix]')
SRC = Path(bpy.data.filepath).resolve()
OUT = Path(argv[0]).resolve()
PREFIX = Path(argv[1]).resolve() if len(argv) > 1 else None
OUTDIR = (NB / 'out').resolve()
if OUT == SRC or OUT.suffix != '.blend' or (OUT.parent == OUTDIR and OUT.exists()) or OUT.name in {p.name for p in OUTDIR.glob('*')}:
    raise SystemExit(f'refusing to write {OUT} (input file, existing nb_work/out file, or not .blend)')
bpy.context.preferences.filepaths.save_version = 0
SECTIONS = set(os.environ.get('WD1_SECTIONS', 'mtn,col,pan,kiln,aq').split(','))

sc = bpy.context.scene
O = bpy.data.objects
L01 = sorted(o.name for o in O if o.name.startswith('L01_'))
OWNED = ['COL_ruined', 'R3_colosseum_podium', 'R4_arena_skin', 'R8_pantheon', 'D2_lime_kiln', 'L05_aqua_claudia',
         'L07_vesuvius', 'L08_pompeii'] + L01
report = {'input': str(SRC), 'output': str(OUT), 'sections': sorted(SECTIONS)}


def need(name):
    o = O.get(name)
    if o is None or o.type != 'MESH':
        raise RuntimeError(f'WD1 step: mesh object {name!r} not found in {SRC.name}')
    return o


for n in OWNED:
    need(n)
if len(L01) != 8:
    raise RuntimeError(f'WD1 step: expected 8 L01_* peaks, found {L01}')
fp_before = L.fingerprint(set(OWNED))
mat_users = {}
for o in O:
    for s in o.material_slots:
        if s.material:
            mat_users.setdefault(s.material.name, set()).add(o.name)


def own_material(name):
    """material used only by owned objects (safe to edit in place)."""
    m = bpy.data.materials.get(name)
    if m is None:
        raise RuntimeError(f'material {name!r} missing')
    others = mat_users.get(name, set()) - set(OWNED)
    if others:
        raise RuntimeError(f'material {name!r} is also used by {sorted(others)} - duplicate it instead')
    return m


def private_copy(src_name, new_name, factor=None, hexcol=None):
    """get or create an owned duplicate of a shared material; colour set absolutely (idempotent)."""
    src = bpy.data.materials[src_name]
    m = bpy.data.materials.get(new_name) or src.copy()
    m.name = new_name
    base = list(src.diffuse_color)
    if hexcol:
        lin = L.hex_to_lin(hexcol)
    else:
        lin = [min(1.0, c * factor) for c in base[:3]]
    m.diffuse_color = (*lin, base[3])
    return m


def set_hex(m, hx):
    m.diffuse_color = (*L.hex_to_lin(hx), m.diffuse_color[3])


S = L.Screen()
TERR = L.Terrain(need('T_land'))
already = bool(sc.get(MARK))
report['already_marked'] = already


# ====================================================================================== mountains (Apennines + Vesuvius)
def do_mountains():
    """AP-1 / OBJ_INFO-02 (apennines): base_mountain_volcano #CDC7AE -> #C2BCA4 (linear x0.88). Shared only by L01_* and
    L07_vesuvius (all owned), so Vesuvius darkens with the family."""
    m = own_material('RC.v12.base_mountain_volcano')
    before = L.lin_to_hex(m.diffuse_color)
    set_hex(m, '#C2BCA4')
    report['mountains'] = {'material': m.name, 'before': before, 'after': L.lin_to_hex(m.diffuse_color)}


# ====================================================================================== Colosseum
COL_RHO = (0.004, 0.349, 31.98, 24.53)        # ellipse in COL_ruined local coords (x+0.004)/a, (y-0.349)/b


def col_rho(c):
    dx, dy, a, b = COL_RHO
    return np.sqrt(((c[:, 0] + dx) / a) ** 2 + ((c[:, 1] - dy) / b) ** 2)


def col_paint():
    """OBJ_COLOR-23: colosseum_wall faces inside the outer ring (rho < 0.88) -> colosseum_interior; then wall-face
    islands whose shared edges are >= 80 % with interior faces -> interior."""
    o = need('COL_ruined'); me = o.data
    slots = [s.material.name if s.material else None for s in o.material_slots]
    iw, ii = slots.index('RC.v12.colosseum_wall'), slots.index('RC.v12.colosseum_interior')
    n = len(me.polygons)
    cen = np.empty(n * 3); me.polygons.foreach_get('center', cen); cen = cen.reshape(-1, 3)
    mi = np.empty(n, np.int32); me.polygons.foreach_get('material_index', mi)
    rho = col_rho(cen)
    sel = (mi == iw) & (rho < 0.88)
    mi[sel] = ii
    # island pass: face adjacency through shared edges
    bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
    wall = mi == iw
    comp = -np.ones(n, np.int64); ncomp = 0; changed = 0; island_stats = []
    for f0 in np.nonzero(wall)[0]:
        if comp[f0] >= 0:
            continue
        st = [int(f0)]; comp[f0] = ncomp; faces = []
        while st:
            f = st.pop(); faces.append(f)
            for e in bm.faces[f].edges:
                for g in e.link_faces:
                    gi = g.index
                    if wall[gi] and comp[gi] < 0:
                        comp[gi] = ncomp; st.append(gi)
        # boundary edges of the island with another face
        nb_int = nb_all = 0
        if len(faces) < 5000:
            fs = set(faces)
            for f in faces:
                for e in bm.faces[f].edges:
                    for g in e.link_faces:
                        if g.index not in fs:
                            nb_all += 1; nb_int += mi[g.index] == ii
        if nb_all and nb_int / nb_all >= 0.8:
            mi[faces] = ii; changed += len(faces)
            island_stats.append(len(faces))
        ncomp += 1
    bm.free()
    me.polygons.foreach_set('material_index', mi); me.update()
    report['col_paint'] = {'rho_reassigned': int(sel.sum()), 'wall_islands': ncomp, 'island_faces_reassigned': changed,
                           'islands_reassigned': len(island_stats), 'wall_faces_after': int((mi == iw).sum()),
                           'interior_faces_after': int((mi == ii).sum())}


FIN_BOXES = {'west_thread': (382, 398, 849, 860), 'east_end': (748, 766, 906, 930)}   # finding areas (+ ~2pt)
FIN_PPT = 8
FIN_MARGIN = 4          # pt of context around each box so the opening is not cut by the crop edge


def col_fins():
    """OBJ_FORM-16: scan fins. Visible-mask of COL_ruined (first hit among map objects), opening with r = 1pt; a residual
    component >= 2pt whose centroid lies in a finding box is a fin. Faces of COL_ruined reachable from the faces under
    it whose vertices ALL project into the residual (grown 0.5pt) are deleted - the fin itself, never the wall it hangs
    from (wall faces have vertices outside the residual). Repeated until no fin >= 2pt is left."""
    o = need('COL_ruined'); me = o.data
    offs = L.disk(FIN_PPT); grow = L.disk(FIN_PPT // 2)
    log = []
    for it in range(6):
        bvh, owner, fidx = L.bvh_of(L.map_visible_objects())
        Pv = S.project(L.world_verts(o))
        bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table()
        kill = set(); worst = {}; pull = {}; detached = {}
        for nm, (bx0, bx1, by0, by1) in FIN_BOXES.items():
            box = (bx0 - FIN_MARGIN, bx1 + FIN_MARGIN, by0 - FIN_MARGIN, by1 + FIN_MARGIN)
            g = L.ray_grid(S, box, FIN_PPT, bvh, owner, fidx)
            if 'COL_ruined' not in g['names']:
                continue
            m = g['hit'] == g['names'].index('COL_ruined')
            resid = m & ~L.dilate(L.erode(m, offs), offs)
            regions = []
            w = 0.0
            for ys, xs in L.label(resid):
                cx, cy = box[0] + (xs.mean() + 0.5) / FIN_PPT, box[2] + (ys.mean() + 0.5) / FIN_PPT
                if not (bx0 <= cx <= bx1 and by0 <= cy <= by1):
                    continue
                ln = L.comp_len_pt(ys, xs, FIN_PPT)
                w = max(w, ln)
                if ln >= 2.0:
                    regions.append((ys, xs))
            # detached debris: mask components other than the biggest one, centred in the finding box
            comps = sorted(L.label(m), key=lambda c: -len(c[0]))
            ndet = 0
            for ys, xs in comps[1:]:
                cx, cy = box[0] + (xs.mean() + 0.5) / FIN_PPT, box[2] + (ys.mean() + 0.5) / FIN_PPT
                if bx0 <= cx <= bx1 and by0 <= cy <= by1:
                    regions.append((ys, xs)); ndet += 1
            for ys, xs in regions:
                comp = np.zeros_like(resid); comp[ys, xs] = True
                R = L.dilate(comp, grow)

                def in_R(vi):
                    px, py = Pv[vi]
                    i, j = int((px - box[0]) * FIN_PPT), int((py - box[2]) * FIN_PPT)
                    return 0 <= j < R.shape[0] and 0 <= i < R.shape[1] and R[j, i]
                seeds = {int(f) for f in g['face'][ys, xs] if f >= 0}
                # ragged open border of the scan: a seen face with an open (boundary) edge whose centre falls in the
                # residual is trimmed; trimming a border face cannot open a hole in a closed surface
                for f in seeds:
                    F = bm.faces[f]
                    if any(e.is_boundary for e in F.edges):
                        cpt = S.project(np.array([o.matrix_world @ F.calc_center_median()]))[0]
                        i, j = int((cpt[0] - box[0]) * FIN_PPT), int((cpt[1] - box[2]) * FIN_PPT)
                        if 0 <= j < R.shape[0] and 0 <= i < R.shape[1] and R[j, i]:
                            kill.add(f)
                st = [f for f in seeds if all(in_R(v.index) for v in bm.faces[f].verts)]
                seen = set(st)
                while st:
                    f = st.pop(); kill.add(f)
                    for v in bm.faces[f].verts:
                        for h in v.link_faces:
                            if h.index not in seen:
                                seen.add(h.index)
                                if all(in_R(u.index) for u in h.verts):
                                    st.append(h.index)
                # fins rooted in the wall: pull their tip vertices (inside the residual) back onto the mean of
                # their neighbours outside it, which collapses the sliver triangles onto the wall surface
                for f in seeds:
                    for v in bm.faces[f].verts:
                        if in_R(v.index):
                            out_n = [e.other_vert(v) for e in v.link_edges if not in_R(e.other_vert(v).index)]
                            if out_n:
                                pull[v.index] = sum((u.co for u in out_n), Vector()) / len(out_n)
            detached[nm] = ndet
            worst[nm] = round(w, 2)
        log.append({'iter': it, 'worst_fin_pt': worst, 'detached_parts': detached, 'delete_faces': len(kill), 'pulled_verts': len(pull)})
        if not kill and not pull:
            bm.free()
            break
        for vi, co in pull.items():
            bm.verts[vi].co = co
        bmesh.ops.delete(bm, geom=[bm.faces[i] for i in sorted(kill)], context='FACES_ONLY')
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
        bm.to_mesh(me); bm.free(); me.update()
    report['col_fins'] = log


HOLE_BOX = (698, 720, 928, 942)


def col_hole_plug():
    """OBJ_FORM-16 (see-through gap under the broken east end): T_land pixels enclosed by COL_ruined in HOLE_BOX are
    closed by a colosseum_wall block placed just in front of the terrain points they show (inside the outer ring)."""
    o = need('COL_ruined'); me = o.data
    bvh, owner, fidx = L.bvh_of(L.map_visible_objects())
    ppt = 6
    g = L.ray_grid(S, HOLE_BOX, ppt, bvh, owner, fidx)
    names = g['names']
    if 'T_land' not in names or 'COL_ruined' not in names:
        report['col_hole'] = {'terrain_px': 0}
        return
    col = g['hit'] == names.index('COL_ruined')
    blocker = g['hit'] >= 0
    blocker &= ~(g['hit'] == names.index('T_land'))
    inside = L.fill_holes(blocker) & (g['hit'] == names.index('T_land'))
    pts = g['pts'][inside]
    rep = {'terrain_px': int(inside.sum()), 'terrain_pt2': round(inside.sum() / ppt ** 2, 2)}
    if len(pts):
        lo, hi = pts.min(0), pts.max(0)
        c = (lo + hi) / 2
        half = np.maximum((hi - lo) / 2 + 0.35, 0.45)
        z0 = TERR.z(c[0], c[1]) - 0.1
        Wv = np.array([[c[0] + sx * half[0], c[1] + sy * half[1], z0 + sz * 1.7] for sz in (0, 1) for sy in (-1, 1) for sx in (-1, 1)])
        loc = L.local_from_world(o, Wv)
        slots = [s.material.name if s.material else None for s in o.material_slots]
        bm = bmesh.new(); bm.from_mesh(me)
        vs = [bm.verts.new(p) for p in loc]
        quads = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
        for q in quads:
            f = bm.faces.new([vs[i] for i in q]); f.material_index = slots.index('RC.v12.colosseum_wall')
        bm.to_mesh(me); bm.free(); me.update()
        rep.update({'plug_center_world': np.round(c, 3).tolist(), 'plug_half_xy': np.round(half[:2], 3).tolist(), 'plug_z0': round(z0, 3)})
    report['col_hole'] = rep


PODIUM_CHAMFER = 0.6     # wu: outer top edge pulled inward -> 45 deg chamfer instead of a vertical riser


def col_podium():
    """OBJ_INFO-19-A01: the travertine podium read as a display base (dark vertical riser, light top). The outer
    footprint (D32/D34 road clearance) and the top height (0.6, D14 cover over scan debris; inner edge under the walls,
    D21) are kept; the vertical riser becomes a 45 deg chamfer by pulling each outer-top vertex inward along its top
    edge, so the edge band is lit like the top. Travertine #D2C2A2 -> #DDCDAD (top closer to the ground)."""
    p = need('R3_colosseum_podium'); me = p.data
    Wv = L.world_verts(p)
    bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    # 240 stations x (outer bottom, outer top, inner top); an outer-top vertex sits straight above an outer-bottom one
    moved = 0; runs = []
    for v in bm.verts:
        i = v.index
        nb = [e.other_vert(v).index for e in v.link_edges]
        below = [j for j in nb if Wv[j, 2] < Wv[i, 2] - 0.3 and np.hypot(*(Wv[j, :2] - Wv[i, :2])) < 0.02]
        if not below or Wv[i, 2] < 0.3:
            continue
        # inner-top neighbour: the top-edge neighbour farthest from the bottom vertex horizontally, ~level with i
        cand = [j for j in nb if j not in below and abs(Wv[j, 2] - Wv[i, 2]) < 0.7]
        if not cand:
            continue
        j = max(cand, key=lambda j: np.hypot(*(Wv[j, :2] - Wv[below[0], :2])))
        d = Wv[j, :2] - Wv[i, :2]; dist = float(np.hypot(*d))
        if dist < 0.2:
            continue
        run = min(PODIUM_CHAMFER, 0.45 * dist)
        Wv[i, :2] += d / dist * run; moved += 1; runs.append(run)
    bm.free()
    co = L.local_from_world(p, Wv)
    me.vertices.foreach_set('co', co.ravel()); me.update()
    m = own_material('RC.v12_4.piazza_travertine')
    before = L.lin_to_hex(m.diffuse_color); set_hex(m, '#DDCDAD')
    report['col_podium'] = {'outer_top_verts_chamfered': moved, 'run_min_max': [round(min(runs), 3), round(max(runs), 3)] if runs else None,
                            'travertine': [before, L.lin_to_hex(m.diffuse_color)]}


# ====================================================================================== Pantheon
PAN_STONE_K = float(os.environ.get('WD1_PAN_STONE_K', 1.18))   # pantheon-only roman_stone / roman_plinth, linear x
PAN_ROOF_K = float(os.environ.get('WD1_PAN_ROOF_K', 0.95))     # pantheon-only roman_roof, linear x (hue kept)
PAN_STEPS = 4
PAN_SEG = 160


def pan_paint():
    """OBJ_COLOR-23: roof planes painted with the wall token. Local coords of R8_pantheon: (1) portico pediment slopes
    y < -0.55, normal within 12 deg of (+-0.43, 0, 0.90), plane |n.c - 0.156| < 0.02; (2) middle-block roof: normal
    within 12 deg of +z, z = 0.271 +- 0.015, inside the XY range of that plane's roof faces (+8 %)."""
    o = need('R8_pantheon'); me = o.data
    slots = [s.material.name if s.material else None for s in o.material_slots]
    i_st = next(i for i, n in enumerate(slots) if n and n.startswith('RC.v12.roman_stone'))
    i_rf = next(i for i, n in enumerate(slots) if n and n.startswith('RC.v12.roman_roof'))
    n = len(me.polygons)
    cen = np.empty(n * 3); me.polygons.foreach_get('center', cen); cen = cen.reshape(-1, 3)
    nrm = np.empty(n * 3); me.polygons.foreach_get('normal', nrm); nrm = nrm.reshape(-1, 3)
    mi = np.empty(n, np.int32); me.polygons.foreach_get('material_index', mi)
    cos12 = math.cos(math.radians(12))
    sel1 = np.zeros(n, bool)
    for sx in (1, -1):
        t = np.array([0.43 * sx, 0, 0.90]); t /= np.linalg.norm(t)
        sel1 |= (cen[:, 1] < -0.55) & (nrm @ t > cos12) & (np.abs(cen @ t - 0.156) < 0.02)
    plane = (nrm[:, 2] > cos12) & (np.abs(cen[:, 2] - 0.271) < 0.015)
    rf = plane & (mi == i_rf)
    x0, x1 = cen[rf, 0].min(), cen[rf, 0].max(); y0, y1 = cen[rf, 1].min(), cen[rf, 1].max()
    mx, my = 0.04 * (x1 - x0), 0.04 * (y1 - y0)
    sel2 = plane & (cen[:, 0] > x0 - mx) & (cen[:, 0] < x1 + mx) & (cen[:, 1] > y0 - my) & (cen[:, 1] < y1 + my)
    a, b = int((sel1 & (mi == i_st)).sum()), int((sel2 & (mi == i_st)).sum())
    mi[(sel1 | sel2) & (mi == i_st)] = i_rf
    me.polygons.foreach_set('material_index', mi); me.update()
    report['pan_paint'] = {'portico_slope_faces': a, 'middle_roof_faces': b}


def pan_dome():
    """OV-PAN-21: the ~6 thin step rings of the dome blur at 1 m. They are replaced by 4 rings with twice the riser
    (0.045 local = 0.21 wu each) on the same footprint: faces of the old rings (roof, 0.276 < z < 0.458, r < 0.66 from
    the oculus axis) are removed and a stepped ring stack (separate riser/tread loops so the corners stay crisp) is built
    from the drum top (z 0.255, under the roof ring) to under the lower edge of the dome cap (r 0.36, z 0.455)."""
    o = need('R8_pantheon'); me = o.data
    co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    top = co[co[:, 2] > 0.5]
    cx, cy = (top[:, 0].max() + top[:, 0].min()) / 2, (top[:, 1].max() + top[:, 1].min()) / 2
    slots = [s.material.name if s.material else None for s in o.material_slots]
    i_rf = next(i for i, n in enumerate(slots) if n and n.startswith('RC.v12.roman_roof'))
    bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
    dead = []
    for f in bm.faces:
        c = f.calc_center_median()
        if f.material_index == i_rf and 0.276 < c.z < 0.458 and math.hypot(c.x - cx, c.y - cy) < 0.66:
            dead.append(f)
    nd = len(dead)
    bmesh.ops.delete(bm, geom=dead, context='FACES')
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    r_out = [0.640, 0.595, 0.550, 0.505]
    z_top = [0.320, 0.365, 0.410, 0.455]
    z_bot = [0.255] + z_top[:-1]
    r_in = r_out[1:] + [0.36]
    ang = [2 * math.pi * k / PAN_SEG for k in range(PAN_SEG)]

    def ring(r, z):
        return [bm.verts.new((cx + r * math.cos(a), cy + r * math.sin(a), z)) for a in ang]

    def band(A, B, smooth, flip=False):
        for k in range(PAN_SEG):
            q = [A[k], A[(k + 1) % PAN_SEG], B[(k + 1) % PAN_SEG], B[k]]
            f = bm.faces.new(q[::-1] if flip else q)
            f.material_index = i_rf; f.smooth = smooth
    for k in range(PAN_STEPS):
        band(ring(r_out[k], z_bot[k]), ring(r_out[k], z_top[k]), True)        # riser (outward normal)
        band(ring(r_out[k], z_top[k]), ring(r_in[k], z_top[k]), False)         # tread (up)
    bm.normal_update()
    bm.to_mesh(me); bm.free(); me.update()
    report['pan_dome'] = {'old_ring_faces_removed': nd, 'axis_local': [round(cx, 4), round(cy, 4)], 'rings': PAN_STEPS,
                          'riser_local': 0.045, 'r_out': r_out, 'z_top': z_top}


def pan_materials():
    """OV-PAN-08-13 + OBJ_COLOR-21: Pantheon-only copies of the shared tokens (the shared ones stay as they are):
    stone/plinth x PAN_STONE_K (one value lighter, like the other roman_stone buildings), roof x PAN_ROOF_K (same hue,
    darker than the lightened walls so roof/wall separate)."""
    o = need('R8_pantheon')
    out = {}
    for s in o.material_slots:
        nm = s.material.name
        base = nm.split('.pantheon')[0]
        k = PAN_ROOF_K if 'roman_roof' in base else PAN_STONE_K
        m = private_copy(base, base + '.pantheon', factor=k)
        s.material = m
        out[base] = [L.lin_to_hex(bpy.data.materials[base].diffuse_color), L.lin_to_hex(m.diffuse_color), k]
    report['pan_materials'] = out


# ====================================================================================== lime kiln
# Roman lime kiln (fornax calcaria, Cato Agr. 38: wide at the bottom, narrowed to ~3/10 at the top, round top opening,
# stoking door at the bottom). Freestanding rubble-masonry frustum: base dia 4.6 wu, top 0.41 x base, opening 0.30 x
# base, height 4.3 wu, stoking arch facing the viewer (25 deg to screen right), plinth course, soot-dark inside.
KILN = dict(R0=2.30, RT=0.95, RIN=0.69, H=4.30, PL_R=2.48, PL_H=0.28, SHAFT=1.8, N=256, DZ=0.05, COURSE=0.42,
            ARCH_W=1.20, ARCH_SPRING=0.80, ARCH_DEPTH=1.5, ARCH_TURN=25.0, BLOCK=0.78)
KILN_LABEL_GAP_PT = 6.0          # kiln silhouette left edge -> right edge of label 797:78 (x 74pt), as before
KILN_LABEL_RIGHT = 74.0          # text_spec_r11 797:78 [36, 701, 38, 11]
KILN_BASE_Y_PT = 700.0           # screen y of the base centre (label 797:78 spans y 701-712 at the kiln's foot)


def kiln_profile_r(t):
    """outer radius at height fraction t (0 base of the body, 1 top): slightly convex frustum."""
    k = KILN
    return k['R0'] - (k['R0'] - k['RT']) * t ** 1.15


def build_kiln_mesh(name):
    k = KILN
    rng = np.random.default_rng(38)            # Cato De Agri Cultura 38 - fixed seed, deterministic
    N = k['N']; z0 = k['PL_H'] - 0.02; H = k['H']
    nz = int(round((H - z0) / k['DZ']))
    zs = np.linspace(z0, H, nz + 1)
    bm = bmesh.new()
    ncourse = int(math.ceil((H - z0) / k['COURSE'])) + 1
    jitter = rng.uniform(-0.012, 0.012, size=(ncourse, 64))

    def disp(z, a):
        """masonry relief: course grooves, staggered vertical joints, per-stone bulge."""
        c = (z - z0) / k['COURSE']; ci = int(c); fc = c - ci
        d = 0.0
        if fc < 0.07 or fc > 0.93:
            d -= 0.024
        r = kiln_profile_r((z - z0) / (H - z0))
        nb = max(6, int(round(2 * math.pi * r / k['BLOCK'])))
        u = (a / (2 * math.pi) * nb + 0.5 * (ci % 2)) % 1.0
        if u < 0.035 or u > 0.965:
            d -= 0.016
        d += jitter[min(ci, ncourse - 1), int(a / (2 * math.pi) * nb + 0.5 * (ci % 2)) % 64]
        return d
    rings = []
    for z in zs:
        t = (z - z0) / (H - z0); r = kiln_profile_r(t)
        ring = []
        for i in range(N):
            a = 2 * math.pi * i / N
            rr = r + (disp(z, a) if 0.02 < t < 0.985 else 0.0)
            ring.append(bm.verts.new((rr * math.cos(a), rr * math.sin(a), z)))
        rings.append(ring)

    def band(A, B, mat, smooth=True):
        n = len(A)
        for i in range(n):
            f = bm.faces.new([A[i], A[(i + 1) % n], B[(i + 1) % n], B[i]]); f.material_index = mat; f.smooth = smooth
    for a, b in zip(rings[:-1], rings[1:]):
        band(a, b, 0)
    # rim: thick top with a small lip, then the shaft (soot) and its floor
    def ring_at(r, z):
        return [bm.verts.new((r * math.cos(2 * math.pi * i / N), r * math.sin(2 * math.pi * i / N), z)) for i in range(N)]
    lip_o = ring_at(k['RT'] - 0.04, H + 0.08)
    lip_i = ring_at(k['RIN'] + 0.06, H + 0.08)
    rim_in = ring_at(k['RIN'], H)
    band(rings[-1], lip_o, 0, False); band(lip_o, lip_i, 0, False); band(lip_i, rim_in, 0, True)
    sh_bot = ring_at(k['RIN'] * 1.08, H - k['SHAFT'])
    band(rim_in, sh_bot, 1, True)
    c = bm.verts.new((0, 0, H - k['SHAFT']))
    for i in range(N):
        f = bm.faces.new([sh_bot[i], sh_bot[(i + 1) % N], c]); f.material_index = 1
    # bottom cap of the body
    cb = bm.verts.new((0, 0, z0))
    for i in range(N):
        f = bm.faces.new([rings[0][(i + 1) % N], rings[0][i], cb]); f.material_index = 0
    bm.normal_update()
    me = bpy.data.meshes.new(name + '_body'); bm.to_mesh(me); bm.free()
    return me


def kiln_cutter_mesh(az):
    """arch prism (stoking door) along direction az (rad, ground), from outside into the body."""
    k = KILN
    w = k['ARCH_W'] / 2; zs = k['PL_H'] + 0.05; sp = k['PL_H'] + k['ARCH_SPRING']
    prof = [(-w, zs), (-w, sp)] + [(w * math.cos(math.pi - math.pi * i / 16), sp + w * math.sin(math.pi - math.pi * i / 16)) for i in range(1, 16)] + [(w, sp), (w, zs)]
    d_out, d_in = k['R0'] + 0.8, k['R0'] - k['ARCH_DEPTH']
    ux, uy = math.cos(az), math.sin(az); px, py = -uy, ux
    bm = bmesh.new()
    A = [bm.verts.new((ux * d_out + px * s, uy * d_out + py * s, z)) for s, z in prof]
    B = [bm.verts.new((ux * d_in + px * s, uy * d_in + py * s, z)) for s, z in prof]
    n = len(prof)
    for i in range(n):
        bm.faces.new([A[i], A[(i + 1) % n], B[(i + 1) % n], B[i]])
    bm.faces.new(A[::-1]); bm.faces.new(B)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new('wd1_kiln_cutter'); bm.to_mesh(me); bm.free()
    return me


def kiln_extras(bm, az, z_floor):
    """plinth course (stone), voussoir ring around the door, soot floor inside the door."""
    k = KILN; N = 128
    def ring(r, z):
        return [bm.verts.new((r * math.cos(2 * math.pi * i / N), r * math.sin(2 * math.pi * i / N), z)) for i in range(N)]
    b0, b1, t1, t0 = ring(k['PL_R'], z_floor), ring(k['PL_R'], k['PL_H'] - 0.06), ring(k['PL_R'] - 0.06, k['PL_H']), ring(k['R0'] - 0.3, k['PL_H'])
    for A, B, sm in ((b0, b1, True), (b1, t1, False), (t1, t0, False)):
        for i in range(N):
            f = bm.faces.new([A[i], A[(i + 1) % N], B[(i + 1) % N], B[i]]); f.material_index = 0; f.smooth = sm
    cb = bm.verts.new((0, 0, z_floor))
    for i in range(N):
        f = bm.faces.new([b0[(i + 1) % N], b0[i], cb]); f.material_index = 0
    # voussoirs: 9 blocks on a semicircle just proud of the wall surface
    w = k['ARCH_W'] / 2; sp = k['PL_H'] + k['ARCH_SPRING']
    ux, uy = math.cos(az), math.sin(az); px, py = -uy, ux
    z0b = k['PL_H'] - 0.02

    def rf(z):
        return kiln_profile_r(max(0.0, (z - z0b) / (k['H'] - z0b)))
    for j in range(9):
        a0, a1 = math.pi * j / 9 + 0.012, math.pi * (j + 1) / 9 - 0.012
        quad = []
        for (rr, aa) in ((w + 0.02, a0), (w + 0.30, a0), (w + 0.30, a1), (w + 0.02, a1)):
            s, z = rr * math.cos(aa), sp + rr * math.sin(aa)
            quad.append((s, z))
        front = [bm.verts.new((ux * (rf(z) + 0.07) + px * s, uy * (rf(z) + 0.07) + py * s, z)) for s, z in quad]
        back = [bm.verts.new((ux * (rf(z) - 0.35) + px * s, uy * (rf(z) - 0.35) + py * s, z)) for s, z in quad]
        f = bm.faces.new(front[::-1]); f.material_index = 0
        f = bm.faces.new(back); f.material_index = 0
        for i in range(4):
            f = bm.faces.new([front[i], front[(i + 1) % 4], back[(i + 1) % 4], back[i]]); f.material_index = 0
    # jambs (two upright stones each side of the door)
    for sgn in (-1, 1):
        s0, s1 = sgn * (w + 0.02), sgn * (w + 0.26)
        pts = [(s0, k['PL_H']), (s1, k['PL_H']), (s1, sp), (s0, sp)]
        front = [bm.verts.new((ux * (rf(z) + 0.06) + px * s, uy * (rf(z) + 0.06) + py * s, z)) for s, z in pts]
        back = [bm.verts.new((ux * (rf(z) - 0.35) + px * s, uy * (rf(z) - 0.35) + py * s, z)) for s, z in pts]
        f = bm.faces.new(front[::-1] if sgn > 0 else front); f.material_index = 0
        f = bm.faces.new(back if sgn > 0 else back[::-1]); f.material_index = 0
        for i in range(4):
            q = [front[i], front[(i + 1) % 4], back[(i + 1) % 4], back[i]]
            f = bm.faces.new(q if sgn > 0 else q[::-1]); f.material_index = 0


def do_kiln():
    """OBJ_FORM-08 (blocker, closed igloo dome, no top opening), OBJ_FORM-24 (kiln larger than Pantheon/bridges/
    lighthouse/Pompeii), OBJ_PLACE-04 (1.05 deg tilt), LK-1 (bright firebox), OBJ_COLOR-24 / LK-2 (old scan relief):
    the scan dome is replaced by a modelled Roman lime kiln about 0.55x the old screen size, upright, seated on the
    terrain at run time, placed so its left edge keeps the old 6pt gap to label 797:78."""
    o = need('D2_lime_kiln')
    nsoot = 0
    Pv = S.project(L.world_verts(o)); old_box = [round(float(Pv[:, 0].min()), 1), round(float(Pv[:, 0].max()), 1), round(float(Pv[:, 1].min()), 1), round(float(Pv[:, 1].max()), 1)]
    old_mesh = o.data
    stone = own_material('RC.v12.base_roman_support_stone')
    soot = bpy.data.materials.get('RC.v12.kiln_soot') or stone.copy()
    soot.name = 'RC.v12.kiln_soot'
    soot.diffuse_color = (*[c * 0.30 for c in stone.diffuse_color[:3]], 1.0)
    # door direction: toward the camera, turned ARCH_TURN deg to screen right
    loc0 = o.location.copy()
    cam = S.cam.matrix_world.translation
    az_cam = math.atan2(cam.y - loc0.y, cam.x - loc0.x)
    az = az_cam + math.radians(KILN['ARCH_TURN'])
    body = build_kiln_mesh('D2_lime_kiln')
    tmp = bpy.data.objects.new('wd1_tmp_kiln', body); cut = bpy.data.objects.new('wd1_tmp_cut', kiln_cutter_mesh(az))
    sc.collection.objects.link(tmp); sc.collection.objects.link(cut)
    tmp.data.materials.append(stone); tmp.data.materials.append(soot); cut.data.materials.append(soot)
    md = tmp.modifiers.new('door', 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = cut; md.solver = 'EXACT'
    md.material_mode = 'TRANSFER'
    dg = bpy.context.evaluated_depsgraph_get(); dg.update()
    me_new = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    for ob in (tmp, cut):
        m_ = ob.data; bpy.data.objects.remove(ob); bpy.data.meshes.remove(m_)
    while len(me_new.materials) < 2:
        me_new.materials.append(None)
    bm = bmesh.new(); bm.from_mesh(me_new)
    # soot: the shaft below the rim and the faces of the door recess (inside the outer masonry surface)
    k = KILN; z0b = k['PL_H'] - 0.02; nsoot = 0
    for f in bm.faces:
        c = f.calc_center_median(); r = math.hypot(c.x, c.y)
        t = max(0.0, (c.z - z0b) / (k['H'] - z0b))
        inner = (c.z > k['H'] - k['SHAFT'] - 0.02 and r < k['RIN'] * 1.12) or (c.z < 2.3 and r < kiln_profile_r(t) - 0.05)
        f.material_index = 1 if inner else 0; nsoot += int(inner)
    kiln_extras(bm, az, -0.06)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    # faces inside the door recess that came from the cutter are soot (TRANSFER); keep smooth shading on the body
    bm.to_mesh(me_new); bm.free()
    me_new.name = 'D2_lime_kiln_fornax'
    while len(me_new.materials) < 2:
        me_new.materials.append(None)
    while len(me_new.materials) > 2:
        me_new.materials.pop()
    me_new.materials[0] = stone; me_new.materials[1] = soot
    o.data = me_new
    report['kiln_slot_links_before'] = [sl.link for sl in o.material_slots]
    for sl in o.material_slots:
        sl.link = 'DATA'
    if old_mesh.users == 0:
        bpy.data.meshes.remove(old_mesh)
    o.rotation_euler = (0.0, 0.0, 0.0); o.scale = (1.0, 1.0, 1.0)
    # placement: left edge KILN_LABEL_GAP_PT right of the label, base centre at KILN_BASE_Y_PT; seat on terrain
    right = S.cam.matrix_world.col[0].xyz.copy(); right.z = 0; right.normalize()
    fwd = Vector((-right.y, right.x, 0))           # ground direction that moves the object up the screen
    for it in range(6):
        zs = [TERR.z(o.location.x + r * math.cos(a), o.location.y + r * math.sin(a)) for r in (0, 1.2, 2.5) for a in np.linspace(0, 2 * math.pi, 12, endpoint=False)]
        o.location.z = min(zs)
        bpy.context.view_layer.update()
        P = S.project(L.world_verts(o)); base = S.to_pt(o.location)
        wpp = S.wu_per_pt(o.location)
        dx = (KILN_LABEL_RIGHT + KILN_LABEL_GAP_PT) - P[:, 0].min()
        dy = KILN_BASE_Y_PT - base[1]
        if abs(dx) < 0.05 and abs(dy) < 0.05:
            break
        # screen y down = moving toward the camera on the ground; one ground unit along fwd moves the point up by
        # roughly wpp^-1 * sin(elevation); estimate numerically
        p2 = S.to_pt(o.location + fwd)
        o.location += right * (dx * wpp) + fwd * (dy / (p2[1] - base[1]))
    bpy.context.view_layer.update()
    zs = [TERR.z(o.location.x + r * math.cos(a), o.location.y + r * math.sin(a)) for r in (0, 1.2, 2.5) for a in np.linspace(0, 2 * math.pi, 24, endpoint=False)]
    o.location.z = min(zs)
    bpy.context.view_layer.update()
    P = S.project(L.world_verts(o))
    new_box = [round(float(P[:, 0].min()), 1), round(float(P[:, 0].max()), 1), round(float(P[:, 1].min()), 1), round(float(P[:, 1].max()), 1)]
    wpp = S.wu_per_pt(o.location)
    report['kiln'] = {'old_screen_box': old_box, 'new_screen_box': new_box,
                      'long_side_pt': round(max(new_box[1] - new_box[0], new_box[3] - new_box[2]), 1),
                      'long_side_over_s': round(max(new_box[1] - new_box[0], new_box[3] - new_box[2]) * wpp, 2),
                      'location': [round(v, 3) for v in o.location], 'terrain_span': [round(min(zs), 3), round(max(zs), 3)],
                      'door_azimuth_deg': round(math.degrees(az), 1), 'top_over_base': round(KILN['RT'] / KILN['R0'], 3),
                      'opening_over_base': round(KILN['RIN'] / KILN['R0'], 3), 'soot_hex': L.lin_to_hex(soot.diffuse_color),
                      'verts': len(o.data.vertices), 'faces': len(o.data.polygons), 'soot_faces': nsoot}


# ====================================================================================== aqueduct
AQ_DEPTH_K = float(os.environ.get('WD1_AQ_DEPTH', 0.6))        # cross-axis depth of everything (piers, arches, spandrels, channel)
AQ_PIER_K = float(os.environ.get('WD1_AQ_PIER', 0.7))         # along-axis width of the piers (pitch and pier centres unchanged -> wider arch openings)
AQ_BURY = 0.15          # wu the plinth may sit below the uphill terrain (~1.4pt < 1.84pt limit)
AQ_SINK = 0.05          # plinth bottom below the lowest terrain under its footprint (no float downhill)


def aq_islands(me):
    nv = len(me.vertices)
    ed = np.empty(len(me.edges) * 2, np.int64); me.edges.foreach_get('vertices', ed); ed = ed.reshape(-1, 2)
    par = np.arange(nv)

    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]; a = par[a]
        return a
    for a, b in ed:
        ra, rb = find(a), find(b)
        if ra != rb:
            par[ra] = rb
    roots = np.array([find(i) for i in range(nv)])
    u, inv = np.unique(roots, return_inverse=True)
    order = np.argsort(inv, kind='stable')
    splits = np.cumsum(np.bincount(inv))[:-1]
    return np.split(order, splits)


def do_aqueduct():
    """OBJ_FORM-07 / OBJ_INFO-02 (arches of the lower bend overlap: seen at 22-27 deg to the axis, the deep piers
    cover the 1.14 wu openings) and OBJ_PLACE-02 (plinths 0.33-0.6 wu inside T_land). The plan path, pier centres
    and pitch stay where they are (field worker WE clears its props around them). Per vertex, in the frame of the
    pier-centre polyline: cross-axis offset x AQ_DEPTH_K; within each pier zone the along-axis coordinate is
    compressed x AQ_PIER_K and the arch zone stretched to match (continuous, identity at mid-bay). Each pier column is
    lifted rigidly so its plinth bottom sits AQ_BURY under the highest terrain under its footprint, and its bottom
    face is extended down to AQ_SINK under the lowest terrain there; arches/channel follow the lift interpolated
    between piers. Terrain is ray-cast at run time."""
    o = need('L05_aqua_claudia'); me = o.data
    Wv = L.world_verts(o)
    isl = aq_islands(me)
    info = []
    for vs in isl:
        P = Wv[vs]; mn, mx = P.min(0), P.max(0)
        info.append((vs, mn, mx))
    blocks = [i for i, (vs, mn, mx) in enumerate(info) if len(vs) == 8 and max(mx[0] - mn[0], mx[1] - mn[1]) < 1.2
              and mx[2] - mn[2] < 0.6 and mx[2] < 4.2]
    cent = np.array([(info[i][1][:2] + info[i][2][:2]) / 2 for i in blocks])
    lab = -np.ones(len(blocks), int); nc = 0
    for i in range(len(blocks)):
        if lab[i] >= 0:
            continue
        d = np.linalg.norm(cent - cent[i], axis=1)
        lab[(d < 0.25) & (lab < 0)] = nc; nc += 1
    piers = []
    for c in range(nc):
        idx = np.nonzero(lab == c)[0]
        xy = np.median(cent[idx], 0)
        isl_ids = [blocks[i] for i in idx]
        bottom = min(isl_ids, key=lambda k: info[k][1][2])
        zb = info[bottom][1][2]
        bx0, by0 = info[bottom][1][:2]; bx1, by1 = info[bottom][2][:2]
        ts = [TERR.z(x, y) for x in np.linspace(bx0, bx1, 4) for y in np.linspace(by0, by1, 4)]
        if zb > max(ts) + 0.3:            # springer blocks of an arch, not a column standing on the ground
            continue
        piers.append({'xy': xy, 'isl': isl_ids, 'bottom': bottom, 'zb': zb, 'tmin': min(ts), 'tmax': max(ts)})
    # order along the aqueduct: nearest-neighbour chain from the southern end
    rest = sorted(range(len(piers)), key=lambda i: piers[i]['xy'][1])
    chain = [rest.pop(0)]
    while rest:
        last = piers[chain[-1]]['xy']
        j = min(rest, key=lambda i: np.linalg.norm(piers[i]['xy'] - last)); rest.remove(j); chain.append(j)
    piers = [piers[i] for i in chain]
    C = np.array([p['xy'] for p in piers])
    # extend both ends so vertices beyond the end piers have a frame
    C = np.vstack([C[0] - (C[1] - C[0]) / np.linalg.norm(C[1] - C[0]) * 3.0, C, C[-1] + (C[-1] - C[-2]) / np.linalg.norm(C[-1] - C[-2]) * 3.0])
    seg = C[1:] - C[:-1]; seglen = np.linalg.norm(seg, axis=1); tang = seg / seglen[:, None]
    s_node = np.r_[0, np.cumsum(seglen)]
    s_pier = s_node[1:-1]
    pitch = float(np.median(np.diff(s_pier)[np.diff(s_pier) < 2.5]))
    for p in piers:
        p['lift'] = max(0.0, p['tmax'] - AQ_BURY - p['zb'])
    lifts = np.array([p['lift'] for p in piers])
    # per vertex frame (nearest segment)
    XY = Wv[:, :2]
    best_d = np.full(len(XY), np.inf); best_k = np.zeros(len(XY), int); best_t = np.zeros(len(XY))
    for k in range(len(seg)):
        t = np.clip(((XY - C[k]) @ tang[k]), 0, seglen[k])
        d = np.linalg.norm(XY - (C[k] + t[:, None] * tang[k]), axis=1)
        m = d < best_d
        best_d[m] = d[m]; best_k[m] = k; best_t[m] = t[m]
    T_ = tang[best_k]; N_ = np.c_[-T_[:, 1], T_[:, 0]]
    S_ = s_node[best_k] + best_t
    n_off = ((XY - C[best_k]) * N_).sum(1)
    # along-axis warp around the nearest pier
    ip = np.clip(np.searchsorted(s_pier, S_), 1, len(s_pier) - 1)
    near = np.where(np.abs(S_ - s_pier[ip - 1]) < np.abs(S_ - s_pier[ip]), ip - 1, ip)
    u = S_ - s_pier[near]; au = np.abs(u); half = pitch / 2
    U0 = 0.48
    g = np.where(au <= U0, au * AQ_PIER_K,
                 np.where(au <= half, AQ_PIER_K * U0 + (au - U0) * (half - AQ_PIER_K * U0) / (half - U0), au))
    du = np.sign(u) * g - u
    newXY = XY + T_ * du[:, None] - N_ * (n_off * (1 - AQ_DEPTH_K))[:, None]
    # vertical: rigid lift for pier columns, interpolated lift elsewhere
    lift_v = np.interp(S_, s_pier, lifts)
    vert_pier = -np.ones(len(XY), int)
    for pi, p in enumerate(piers):
        for k in p['isl']:
            vert_pier[info[k][0]] = pi
    rigid = vert_pier >= 0
    lift_v[rigid] = lifts[vert_pier[rigid]]
    Z = Wv[:, 2] + lift_v
    ext = 0
    for pi, p in enumerate(piers):
        vs = info[p['bottom']][0]
        zmin = Wv[vs, 2].min()
        bot = vs[Wv[vs, 2] < zmin + 1e-4]
        target = p['tmin'] - AQ_SINK
        if Z[bot].min() > target:
            Z[bot] = target; ext += 1
    newW = np.c_[newXY, Z]
    co = L.local_from_world(o, newW)
    me.vertices.foreach_set('co', co.ravel()); me.update()
    # report: burial after (terrain vs plinth bottom/top), lifts
    bur = []
    for p in piers:
        vs = info[p['bottom']][0]
        bur.append(round(p['tmax'] - (p['zb'] + p['lift']), 3))
    report['aqueduct'] = {'piers': len(piers), 'pitch_wu': round(pitch, 3), 'lift_wu_min_med_max': [round(float(lifts.min()), 3), round(float(np.median(lifts)), 3), round(float(lifts.max()), 3)],
                          'uphill_burial_wu_max': max(bur), 'plinths_extended_down': ext,
                          'depth_k': AQ_DEPTH_K, 'pier_k': AQ_PIER_K,
                          'max_plan_shift_wu': round(float(np.max(np.linalg.norm(newXY - XY, axis=1))), 3)}


SECTION_FUNCS = []
if 'aq' in SECTIONS:
    SECTION_FUNCS += [do_aqueduct]
if 'kiln' in SECTIONS:
    SECTION_FUNCS += [do_kiln]
if 'pan' in SECTIONS:
    SECTION_FUNCS += [pan_paint, pan_dome, pan_materials]
if not already:
    if 'mtn' in SECTIONS:
        do_mountains()
    if 'col' in SECTIONS:
        col_paint(); col_podium(); col_fins(); col_hole_plug()
    for fn in SECTION_FUNCS:
        fn()
    sc[MARK] = 'wave1 r11 WD1'

# ====================================================================================== ownership check + save
fp_after = L.fingerprint(set(OWNED))
diff = sorted(k for k in set(fp_before) | set(fp_after) if fp_before.get(k) != fp_after.get(k))
report['foreign_changed'] = diff
if diff:
    raise SystemExit(f'WD1 step: objects outside ownership changed: {diff[:10]} - not saving')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT), copy=True)
report['saved'] = str(OUT)
if PREFIX:
    H = runpy.run_path(str(NB / 'scripts/integrate_assets.py'), run_name='integrate_assets_lib')
    report['render'] = H['render_two_pass'](PREFIX)
rp = OUT.with_suffix('.report.json')
rp.write_text(json.dumps(report, indent=1, ensure_ascii=False, default=str))
print('WD1 REPORT', json.dumps(report, ensure_ascii=False, default=str)[:4000])
