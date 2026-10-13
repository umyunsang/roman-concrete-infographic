"""Road geometry step (roadgeo worker): terrain no longer covers the road pavers, kerbs and landing plates.

Run: Blender -b <in.blend> --factory-startup --python step.py -- <out.blend> [render_prefix]
  - refuses to write the input file, an existing file in out/ (published versions), or a non-.blend path
  - with render_prefix: also renders integrate_assets.render_two_pass(<prefix>.png) (48 %, 2 px/pt)
Idempotent: the terrain cap depends only on the road geometry, and T_land is only ever lowered to min(z, cap), so a
second run (same input, or its own output) changes nothing. Fill plates are found-or-created by name.

Defects (v8_13):
 A  south core road (R_core_road), bottom paver row at x 560-670 / y 1015-1025 pt: the ground (T_land) rises
    0.1-0.23 towards the camera there and covers the bottom row and the south kerb.
 B  Via Ostiensis (R_via_ostiensis) east half: the ground rises to the east and buries the east kerb and up to half
    of the paving (paver tops up to 0.25 below the ground); where the kerb is still visible the ground fills the
    running-bond notches between the paver ends and the kerb (paper colour shows). Same at the landing plates
    R1_road_landing1 / R1_road_landing5 (ground over the east kerb / beside R1_road5_bed).

Fix = a local road cutting in T_land, nothing is moved on the road:
  1. road surface field: every upward (|n.z| > 0.3) face of the selected road parts (per region, picked by the screen
     position of the face centre) is rasterised on a 0.1 world grid keeping the highest z = visible road surface.
  2. bed target = surface - 0.10 (paver tops sit 0.094 above their ground by construction; 0.10 puts the ground just
     under the paver bottoms / Ostiensis bed slabs and keeps kerbs embedded 0.01-0.07).
  3. cutting: cap(p) = min over road cells c of target(c) + SLOPE * max(0, |p - c| - SHOULDER): flat for SHOULDER
     (>= the T_land edge length, so no terrain triangle that touches the road keeps a high corner), then a bank of
     slope SLOPE (0.35 < tan 30 deg camera elevation, so the bank never hides the road from the camera).
  4. T_land vertex z = min(z, cap) inside the region boxes only. Vertices under/next to any other map object
     (ray down hits it within its resting height) and anything within PROTECT_R of the Colosseum podium / building
     and the milestones are never touched.
  5. Fill plates (paving material) only where a gap between road parts has no road part under it (see FILLS).
"""
import bpy, bmesh, sys, json, runpy, math, re
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

HERE = Path(__file__).resolve().parent
NB = next((p for p in [HERE, *HERE.parents] if (p / 'scripts/integrate_assets.py').exists()), HERE.parents[1])
OUT_DIR = NB / 'out'
sys.path.insert(0, str(NB / 'workers/layout'))
from common import Screen, world_verts, map_visible_objects   # noqa: E402

MARK = 'rc_roadgeo_v1'
CELL = 0.10          # world units, road surface raster
D_BELOW = 0.07       # ground under the road = visible road surface - D_BELOW
SHOULDER = 0.80      # flat ground beside the road before the bank (T_land edges are 0.4-0.9 long here)
SLOPE = 0.25         # bank slope (rise/run)
SMOOTH_ITERS = 16    # relaxed max-diffusion of the lowering (rounds the crease where the bank meets the old ground)
MAX_DROP = 0.60      # cone radius = SHOULDER + MAX_DROP / SLOPE; a larger needed drop is reported
PROTECT_R = 1.5      # no terrain vertex within this xy distance of the podium / Colosseum / milestones changes
PROTECT_NAMES = ('R3_colosseum_podium', 'COL_ruined', 'R4_arena_skin')
PROTECT_PREFIX = ('MS',)
ROAD_FAMILY = {'R_core_road', 'R_via_ostiensis', 'R_via_appia', 'R1_road_landing1', 'R1_road_landing5',
               'R4_bridge_west_bed', 'R1_road5_bed', 'B_pons1', 'B_pons2',
               'B_pons1_parapet0', 'B_pons1_parapet1', 'B_pons2_parapet0', 'B_pons2_parapet1'}
PIN_FADE_SLOPE = 0.6 # lowering allowed next to a pinned steep vertex: this slope times the xy distance to it
STEEP_NZ = 0.7       # T_land vertices on faces steeper than 45 deg (quay walls, pit walls) never move
KERB_MIN_FACES = 40  # same split rule as workers/roads/step.py (< 40 faces = paving part, >= 40 = kerb ribbon)
MAT_PAVE = 'RC.road.selce_basalt'
CLIP_BED = 'R1_road5_bed'
BED_SECTIONS = [(0, 1), (2, 3), (4, 5), (6, 7)]   # west, east vertex of each cross-section of R1_road5_bed
FILL_NAME = 'R_roadgeo_ostiensis_junction_fill'
# region: road objects whose upward faces (centre on screen inside box, pt) define the cutting
REGIONS = [
    ('A_core_south', ['R_core_road'], (545.0, 690.0, 1003.0, 1035.0)),
    ('B_ostiensis', ['R_via_ostiensis', FILL_NAME], (60.0, 420.0, 995.0, 1398.0)),
    ('B_landing1', ['R_core_road', 'R1_road_landing1'], (495.0, 580.0, 488.0, 545.0)),
    ('B_landing5', ['R_core_road', 'R1_road_landing5', 'R1_road5_bed'], (880.0, 972.0, 850.0, 945.0)),
]


def need(name):
    o = bpy.data.objects.get(name)
    if o is None:
        raise RuntimeError(f'roadgeo step: object {name!r} not found in {bpy.data.filepath}')
    if o.type != 'MESH':
        raise RuntimeError(f'roadgeo step: object {name!r} is {o.type}, expected MESH')
    return o


def up_faces(o, S, box):
    """triangles (m,3,3) world of the upward faces of o whose centre projects inside box."""
    me = o.data; W = world_verts(o); R = np.array(o.matrix_world.to_3x3())
    nrm = np.empty(len(me.polygons) * 3); me.polygons.foreach_get('normal', nrm); nrm = nrm.reshape(-1, 3) @ R.T
    nz = np.abs(nrm[:, 2]) / np.maximum(np.linalg.norm(nrm, axis=1), 1e-12)
    ls = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get('loop_start', ls)
    lt = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get('loop_total', lt)
    lv = np.empty(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', lv)
    cen = np.array([W[lv[s:s + t]].mean(0) for s, t in zip(ls, lt)]) if len(ls) else np.zeros((0, 3))
    P = S.project(cen) if len(cen) else np.zeros((0, 2))
    x0, x1, y0, y1 = box
    sel = (nz > 0.3) & (P[:, 0] >= x0) & (P[:, 0] <= x1) & (P[:, 1] >= y0) & (P[:, 1] <= y1)
    tris = []
    for f in np.nonzero(sel)[0]:
        v = lv[ls[f]:ls[f] + lt[f]]
        for k in range(1, len(v) - 1):
            tris.append(W[[v[0], v[k], v[k + 1]]])
    return np.array(tris).reshape(-1, 3, 3), int(sel.sum())


def rasterize_max(tris, x0, y0, nx, ny):
    top = np.full((ny, nx), -np.inf)
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
        inside = (u >= -1e-6) & (v >= -1e-6) & (w >= -1e-6)
        z = w * a[2] + u * b[2] + v * c[2]
        sub = top[j0:j1 + 1, i0:i1 + 1]
        np.maximum(sub, np.where(inside, z, -np.inf), out=sub)
    return top


def cone_cap(target):
    """cap(p) = min_c target(c) + SLOPE * max(0, |p-c| - SHOULDER) on the grid (inf where no road in reach)."""
    ny, nx = target.shape
    R = SHOULDER + MAX_DROP / SLOPE; rc = int(math.ceil(R / CELL))
    T = np.pad(target, rc, constant_values=np.inf)
    cap = np.full_like(target, np.inf)
    for dy in range(-rc, rc + 1):
        for dx in range(-rc, rc + 1):
            d = math.hypot(dx, dy) * CELL
            if d > R:
                continue
            np.minimum(cap, T[rc + dy:rc + dy + ny, rc + dx:rc + dx + nx] + SLOPE * max(0.0, d - SHOULDER), out=cap)
    return cap


def bilinear(grid, x0, y0, xy):
    ny, nx = grid.shape
    g = np.where(np.isfinite(grid), grid, 1e3)
    fx = (xy[:, 0] - x0) / CELL; fy = (xy[:, 1] - y0) / CELL
    i = np.clip(np.floor(fx).astype(int), 0, nx - 2); j = np.clip(np.floor(fy).astype(int), 0, ny - 2)
    tx = np.clip(fx - i, 0, 1); ty = np.clip(fy - j, 0, 1)
    return (g[j, i] * (1 - tx) * (1 - ty) + g[j, i + 1] * tx * (1 - ty) + g[j + 1, i] * (1 - tx) * ty + g[j + 1, i + 1] * tx * ty)


def protected_bvh(xy_box, land):
    """BVH of every render-visible map object except terrain and roads whose xy box meets xy_box."""
    x0, x1, y0, y1 = xy_box
    dg = bpy.context.evaluated_depsgraph_get()
    verts, polys, owner = [], [], []
    for o in map_visible_objects():
        if o == land or o.name in ROAD_FAMILY or o.name == FILL_NAME:
            continue
        ev = o.evaluated_get(dg); me = ev.to_mesh()
        if len(me.vertices) == 0:
            ev.to_mesh_clear(); continue
        co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
        Wv = (np.c_[co, np.ones(len(co))] @ np.array(o.matrix_world).T)[:, :3]
        if Wv[:, 0].max() < x0 or Wv[:, 0].min() > x1 or Wv[:, 1].max() < y0 or Wv[:, 1].min() > y1:
            ev.to_mesh_clear(); continue
        b = len(verts); verts.extend(map(tuple, Wv))
        for p in me.polygons:
            polys.append([b + i for i in p.vertices]); owner.append(o.name)
        ev.to_mesh_clear()
    return (BVHTree.FromPolygons(verts, polys) if polys else None), owner


def guard_kd():
    pts = []
    for o in bpy.data.objects:
        if o.type == 'MESH' and (o.name in PROTECT_NAMES or o.name.startswith(PROTECT_PREFIX)):
            W = world_verts(o)
            if len(W):
                step = max(1, len(W) // 20000)
                pts.extend(W[::step, :2].tolist())
    kd = KDTree(len(pts))
    for i, p in enumerate(pts):
        kd.insert((p[0], p[1], 0.0), i)
    kd.balance()
    return kd


def carve(S, land):
    me = land.data
    if me.users > 1:
        land.data = me.copy(); me = land.data
    LW = world_verts(land); nv = len(LW)
    d_req = np.zeros(nv)                 # required lowering (cutting under the road + bank)
    d_lim = np.full(nv, np.inf)          # largest allowed lowering (0 = never move)
    work = np.zeros(nv, bool)            # vertices the smoothing may touch (region boxes)
    kd = guard_kd()
    rep = {}
    for name, objs, box in REGIONS:
        tris = []; nface = {}
        for on in objs:
            t, n = up_faces(need(on), S, box); nface[on] = n
            if len(t):
                tris.append(t)
        if not tris:
            raise RuntimeError(f'roadgeo step: region {name} selects no road faces')
        tris = np.concatenate(tris)
        R = SHOULDER + MAX_DROP / SLOPE
        xa, xb = tris[:, :, 0].min() - R - CELL, tris[:, :, 0].max() + R + CELL
        ya, yb = tris[:, :, 1].min() - R - CELL, tris[:, :, 1].max() + R + CELL
        nx = int(math.ceil((xb - xa) / CELL)) + 1; ny = int(math.ceil((yb - ya) / CELL)) + 1
        top = rasterize_max(tris, xa, ya, nx, ny)
        target = np.where(np.isfinite(top), top - D_BELOW, np.inf)
        cap = cone_cap(target)
        idx = np.nonzero((LW[:, 0] >= xa) & (LW[:, 0] <= xb) & (LW[:, 1] >= ya) & (LW[:, 1] <= yb))[0]
        c = bilinear(cap, xa, ya, LW[idx, :2])
        needv = np.maximum(0.0, LW[idx, 2] - c)
        d_req[idx] = np.maximum(d_req[idx], needv)
        work[idx] = True
        bvh, owner = protected_bvh((xa, xb, ya, yb), land)
        n_guard = n_rest = n_floor = 0; resting_on = {}
        for vi in idx:
            x, y, z = LW[vi]
            if kd.find_range((x, y, 0.0), PROTECT_R):
                d_lim[vi] = 0.0; n_guard += 1; continue
            if bvh is None:
                continue
            for ox, oy in ((0, 0), (0.35, 0), (-0.35, 0), (0, 0.35), (0, -0.35)):
                h = bvh.ray_cast(Vector((x + ox, y + oy, z + 3.0)), Vector((0, 0, -1)))
                if h[0] is None:
                    continue
                if h[0].z >= z - 0.05:                    # something stands on the ground here
                    if h[0].z <= z + 0.6:
                        d_lim[vi] = 0.0; n_rest += 1; resting_on[owner[h[2]]] = resting_on.get(owner[h[2]], 0) + 1
                        break
                else:                                     # something lies under the ground (water): stay above it
                    lim = z - (h[0].z + 0.05)
                    if lim < d_lim[vi]:
                        d_lim[vi] = lim
                    if lim < needv[np.searchsorted(idx, vi)]:
                        n_floor += 1
        rep[name] = {'road_faces': nface, 'grid': [nx, ny], 'terrain_vertices_in_box': int(len(idx)),
                     'vertices_needing_cut': int((needv > 1e-6).sum()),
                     'needed_drop_max': round(float(needv.max()), 3) if len(needv) else 0.0,
                     'pinned_guard_radius': n_guard, 'pinned_object_on_ground': n_rest,
                     'objects_on_ground': resting_on, 'limited_by_object_below': n_floor,
                     'world_box': [round(v, 2) for v in (xa, xb, ya, yb)]}
    # T_land topology: steep faces (diorama skirt, quay and pit walls) and border vertices with a coincident partner
    # (the skirt's top row duplicates the border of the top surface): partners move together, other steep
    # vertices are pinned.
    ls = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get('loop_start', ls)
    lt = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get('loop_total', lt)
    lv = np.empty(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', lv)
    le = np.empty(len(me.loops), np.int32); me.loops.foreach_get('edge_index', le)
    fn = np.empty(len(me.polygons) * 3); me.polygons.foreach_get('normal', fn)
    fn = fn.reshape(-1, 3) @ np.array(land.matrix_world.to_3x3()).T
    steep_f = np.abs(fn[:, 2]) / np.maximum(np.linalg.norm(fn, axis=1), 1e-12) < STEEP_NZ
    fidx = np.repeat(np.arange(len(ls)), lt)
    flat_v = np.zeros(nv, bool); flat_v[lv[~steep_f[fidx]]] = True
    steep_v = np.zeros(nv, bool); steep_v[lv[steep_f[fidx]]] = True
    E = np.empty(len(me.edges) * 2, np.int32); me.edges.foreach_get('vertices', E); E = E.reshape(-1, 2)
    ecount = np.bincount(le, minlength=len(E))
    border = np.zeros(nv, bool); border[E[ecount == 1].ravel()] = True
    cand = np.nonzero(border & work)[0]
    groups = []
    if len(cand):
        kt = KDTree(len(cand))
        for k, vi in enumerate(cand):
            kt.insert(LW[vi], k)
        kt.balance(); seen = set()
        for k, vi in enumerate(cand):
            if vi in seen:
                continue
            g = sorted({int(cand[j]) for _, j, _ in kt.find_range(LW[vi], 1e-4)})
            seen.update(g)
            if len(g) > 1:
                groups.append(g)
    grouped = np.zeros(nv, bool)
    for g in groups:
        grouped[g] = True
    pin_steep = work & steep_v & ~flat_v & ~grouped
    rep['pinned_steep_vertices'] = int(pin_steep.sum())
    rep['pinned_steep_vertices_needing_cut'] = int((pin_steep & (d_req > 1e-6)).sum())
    rep['border_partner_groups'] = len(groups)
    d_lim[pin_steep] = 0.0
    for g in groups:                                      # partners share requirement and limit
        d_req[g] = d_req[g].max(); d_lim[g] = d_lim[g].min()
    d_lim = np.maximum(d_lim, 0.0)
    # smooth fall-off: d = max(d_req, relaxed neighbour mean), clipped to d_lim, inside the work set only
    Ew = E[work[E[:, 0]] | work[E[:, 1]]]
    deg = np.zeros(nv); np.add.at(deg, Ew[:, 0], 1); np.add.at(deg, Ew[:, 1], 1)
    dr = np.minimum(d_req, d_lim)
    d = dr.copy()
    for _ in range(SMOOTH_ITERS):
        s = np.zeros(nv); np.add.at(s, Ew[:, 0], d[Ew[:, 1]]); np.add.at(s, Ew[:, 1], d[Ew[:, 0]])
        m = np.where(deg > 0, s / np.maximum(deg, 1), 0.0)
        d = np.where(work, np.minimum(np.maximum(dr, 0.5 * d + 0.5 * m), d_lim), 0.0)
        for g in groups:
            d[g] = d[g].max()
    d[d < 1e-5] = 0.0
    newz = LW[:, 2] - d
    rep['smoothing_iterations'] = SMOOTH_ITERS
    rep['vertices_needing_cut'] = int((d_req > 1e-6).sum())
    rep['vertices_needing_cut_but_limited'] = int((d_req > d_lim + 1e-6).sum())
    rep['cut_shortfall_max'] = round(float(np.max(d_req - np.minimum(d_req, d_lim))), 3)
    rep['lowered_by_smoothing_only'] = int(((d > 0) & (d_req <= 1e-6)).sum())
    rep['drop_max'] = round(float(d.max()), 3)
    changed = np.nonzero(np.abs(newz - LW[:, 2]) > 1e-7)[0]
    if len(changed):
        Mi = np.array(land.matrix_world.inverted())
        Wn = LW.copy(); Wn[:, 2] = newz
        co = (np.c_[Wn, np.ones(len(Wn))] @ Mi.T)[:, :3]
        me.vertices.foreach_set('co', co.ravel()); me.update()
    rep['T_land_vertices_changed'] = int(len(changed))
    return rep


# ------------------------------------------------------------------ road parts: islands, kerb footprints
def islands(o):
    """loose parts of a mesh: list of (sorted vertex indices, face indices)."""
    me = o.data; nv = len(me.vertices)
    parent = np.arange(nv)

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    ev = np.empty(len(me.edges) * 2, np.int32); me.edges.foreach_get('vertices', ev)
    for a, b in ev.reshape(-1, 2):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    roots = np.array([find(i) for i in range(nv)])
    verts, faces = {}, {}
    for i, r in enumerate(roots):
        verts.setdefault(r, []).append(i)
    for p in me.polygons:
        faces.setdefault(roots[p.vertices[0]], []).append(p.index)
    return [(verts[r], faces.get(r, [])) for r in verts]


def kerb_footprint(o, faces):
    """xy polygons (list of (k,2) arrays) of the upward faces of a kerb part."""
    W = world_verts(o); R = o.matrix_world.to_3x3(); polys = []
    for f in faces:
        p = o.data.polygons[f]
        if abs((R @ p.normal).normalized().z) > 0.7:
            polys.append(W[list(p.vertices)][:, :2])
    return polys


def inside_any(pt, polys):
    x, y = pt
    for P in polys:
        if x < P[:, 0].min() or x > P[:, 0].max() or y < P[:, 1].min() or y > P[:, 1].max():
            continue
        ins = False; n = len(P)
        for i in range(n):
            x1, y1 = P[i]; x2, y2 = P[(i + 1) % n]
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                ins = not ins
        if ins:
            return True
    return False


def nearest_kerb(o, xy):
    """the kerb part (>= KERB_MIN_FACES faces) of o nearest to the xy point: (vertex ids, face ids, distance)."""
    W = world_verts(o); best = None
    for vs, fs in islands(o):
        if len(fs) < KERB_MIN_FACES:
            continue
        d = float(np.linalg.norm(W[vs, :2] - np.asarray(xy)[None], axis=1).min())
        if best is None or d < best[2]:
            best = (vs, fs, d)
    return best


# ------------------------------------------------------------------ B: tidy road ends (deterministic, idempotent)
def clip_bed_to_kerb(rep):
    """R1_road5_bed (flat fill at the landing5 road end) reaches up to ~1 unit past the outer edge of the east kerb;
    once the ground no longer hides it, that apron reads as paving outside the road. Each cross-section of the bed
    (vertex pairs west -> east) is cut at the outer kerb edge; sections past the kerb end keep the cut fraction of
    the last section that crosses the kerb. The cut is computed from the kerb and the bed's west edge only, so a
    second run moves nothing."""
    bed = need(CLIP_BED); kerb_obj = need('R_core_road')
    me = bed.data
    if me.users > 1:
        bed.data = me.copy(); me = bed.data
    W = world_verts(bed)
    secs = [(a, b) for a, b in BED_SECTIONS]
    if max(max(s) for s in secs) >= len(W):
        raise RuntimeError(f'roadgeo step: {CLIP_BED} has {len(W)} vertices, expected the 8-vertex v8_11 fill')
    east_mid = W[[b for a, b in secs]].mean(0)
    kv, kf, kd_ = nearest_kerb(kerb_obj, east_mid[:2])
    if kd_ > 2.0:
        raise RuntimeError(f'roadgeo step: no kerb within 2 units of the {CLIP_BED} east edge ({kd_:.2f})')
    polys = kerb_footprint(kerb_obj, kf)
    cuts = []
    for a, b in secs:
        A, B = W[a], W[b]; L = float(np.linalg.norm(B[:2] - A[:2])); u_out = None; seen = False
        for u in np.linspace(0.0, 1.0, int(L / 0.01) + 1):
            p = A[:2] + (B[:2] - A[:2]) * u
            if inside_any(p, polys):
                seen = True; u_out = u
            elif seen:
                break
        cuts.append(u_out)
    known = [u for u in cuts if u is not None]
    if not known:
        raise RuntimeError(f'roadgeo step: {CLIP_BED} sections never cross the kerb')
    moved = []
    for k, ((a, b), u) in enumerate(zip(secs, cuts)):
        if u is None:   # past the kerb end: same fraction as the nearest section that crosses the kerb
            j = min((j for j, c in enumerate(cuts) if c is not None), key=lambda j: abs(j - k)); u = cuts[j]
        A, B = W[a], W[b]
        if u < 1.0 - 1e-6:
            Wn = A + (B - A) * u
            W[b] = Wn; moved.append([int(b), round(float(np.linalg.norm((B - Wn)[:2])), 3)])
    Mi = np.array(bed.matrix_world.inverted())
    co = (np.c_[W, np.ones(len(W))] @ Mi.T)[:, :3]
    me.vertices.foreach_set('co', co.ravel()); me.update()
    rep['clip_bed'] = {'object': CLIP_BED, 'kerb_faces': len(kf), 'section_cut_fraction': [None if c is None else round(float(c), 3) for c in cuts],
                       'east_vertices_moved_in_by': moved}


def junction_fill(rep):
    """Via Ostiensis starts 0.3-0.8 short of the south kerb of the core road: paper showed between its first row and
    that kerb. A bed slab like the Ostiensis' own (0.07 thick, same top height as its first bed) is laid from the
    north edge of the first bed, along the road axis, until it is 0.10 inside the core-road kerb footprint. Built
    as object FILL_NAME (one 5-face box, paving material), recreated from scratch on every run."""
    ost = need('R_via_ostiensis'); core = need('R_core_road')
    W = world_verts(ost)
    beds = []
    for vs, fs in islands(ost):
        if len(vs) != 8 or len(fs) != 5:
            continue
        w = W[vs]; top = w[w[:, 2] > w[:, 2].min() + 0.03]
        if len(top) != 4:
            continue
        e = np.linalg.norm(np.roll(top[:, :2], 1, 0) - top[:, :2], axis=1)
        if e.max() > 1.8:                      # bed slab: ~2.0 x 0.47
            beds.append((w.mean(0), vs, top))
    if len(beds) < 2:
        raise RuntimeError('roadgeo step: Via Ostiensis bed slabs not found')
    kv, kf, _ = nearest_kerb(core, np.mean([b[0][:2] for b in beds[:5]], axis=0))
    KW = world_verts(core)[kv]
    kc = KW[:, :2].mean(0)
    beds.sort(key=lambda b: np.linalg.norm(KW[:, :2] - b[0][None, :2], axis=1).min())
    b0, b1 = beds[0], beds[1]
    t = (b1[0][:2] - b0[0][:2]); t /= np.linalg.norm(t)       # road axis, pointing away from the junction
    top = b0[2]; north = top[np.argsort(top[:, :2] @ t)[:2]]   # the two top corners nearest the junction
    polys = kerb_footprint(core, kf)
    Q = []
    for p in north:
        hit = None
        for s in np.arange(0.0, 3.0, 0.01):
            q = p[:2] - t * s
            if inside_any(q, polys):
                hit = s; break
        if hit is None:
            raise RuntimeError('roadgeo step: junction fill found no core-road kerb within 3 units')
        Q.append(np.r_[p[:2] - t * (hit + 0.10), p[2]])
    zt = float(north[:, 2].mean()); TH = 0.07
    quad = [north[0], north[1], Q[1], Q[0]]
    quad = [np.r_[q[:2], zt] for q in quad]
    # consistent winding (counter-clockwise from above)
    c = np.mean(quad, axis=0); quad.sort(key=lambda q: math.atan2(q[1] - c[1], q[0] - c[0]))
    me = bpy.data.meshes.get(FILL_NAME) or bpy.data.meshes.new(FILL_NAME)
    ob = bpy.data.objects.get(FILL_NAME)
    if ob is None:
        ob = bpy.data.objects.new(FILL_NAME, me)
        for col in ost.users_collection:
            col.objects.link(ob)
    elif ob.data != me:
        ob.data = me
    ob.matrix_world = ost.matrix_world.copy() if False else ob.matrix_world.__class__.Identity(4)
    bm = bmesh.new()
    T_ = [bm.verts.new((q[0], q[1], zt)) for q in quad]
    B_ = [bm.verts.new((q[0], q[1], zt - TH)) for q in quad]
    bm.faces.new(T_)
    for i in range(4):
        j = (i + 1) % 4
        f = bm.faces.new([T_[i], B_[i], B_[j], T_[j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(me); bm.free(); me.update()
    pave = bpy.data.materials.get(MAT_PAVE) or (ost.material_slots[0].material if ost.material_slots else None)
    me.materials.clear()
    if pave is not None:
        me.materials.append(pave)
    ob.hide_render = False; ob.hide_viewport = False
    span = [round(float(np.linalg.norm(Q[i][:2] - north[i][:2])), 3) for i in range(2)]
    rep['junction_fill'] = {'object': FILL_NAME, 'material': pave.name if pave else None, 'top_z': round(zt, 3),
                            'thickness': TH, 'length_along_road': span, 'core_kerb_faces': len(kf)}


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    if not argv:
        raise SystemExit('usage: blender -b in.blend --factory-startup --python step.py -- out.blend [render_prefix]')
    out = Path(argv[0]).resolve(); src = Path(bpy.data.filepath).resolve()
    published = out.parent == OUT_DIR.resolve() and (out.exists() or re.fullmatch(r'roman_concrete_narrative_v8_\d+\w*\.blend', out.name)
                                                     and any(p.name == out.name for p in OUT_DIR.glob('*.blend*')))
    if out == src or out.suffix != '.blend' or published:
        raise SystemExit(f'roadgeo step: refusing to write {out}')
    S = Screen()
    land = need('T_land')
    rep = {}
    clip_bed_to_kerb(rep)
    junction_fill(rep)
    for _, objs, _ in REGIONS:
        for n in objs:
            need(n)
    bpy.context.view_layer.update()
    rep['carve'] = carve(S, land)
    bpy.context.view_layer.update()
    bpy.context.scene[MARK] = json.dumps({'cell': CELL, 'd_below': D_BELOW, 'shoulder': SHOULDER, 'slope': SLOPE})
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(out), copy=True)
    rep['input'] = str(src); rep['output'] = str(out)
    if len(argv) > 1:
        prefix = Path(argv[1]).resolve()
        H = runpy.run_path(str(NB / 'scripts/integrate_assets.py'), run_name='helpers')
        rep['render'] = H['render_two_pass'](prefix.with_suffix('.png'))
    print('ROADGEO_STEP ' + json.dumps(rep, ensure_ascii=False))


if __name__ == '__main__':
    main()
