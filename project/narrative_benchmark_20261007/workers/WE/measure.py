"""measure.py - read-only checks for the WE worker (run on the input and on the step output).

Blender -b <in.blend> --factory-startup --python measure.py -- <out.json>
Camera rays through poster-point grids against the render-visible map objects (map pass), plus geometric checks.
Never saves the blend.
"""
import bpy, sys, json, math, hashlib
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

HERE = Path(__file__).resolve().parent
NB = HERE.parents[1]
sys.path.insert(0, str(NB / 'workers/layout'))
from common import Screen, world_verts, map_visible_objects   # noqa: E402

ROADSET = {'R_core_road', 'R_via_ostiensis', 'R_via_appia', 'R1_road_landing1', 'R1_road_landing5',
           'R_roadgeo_ostiensis_junction_fill', 'R4_bridge_west_bed', 'R1_road5_bed', 'B_pons1', 'B_pons2',
           'B_pons1_parapet0', 'B_pons1_parapet1', 'B_pons2_parapet0', 'B_pons2_parapet1', 'R_we_paving_bed'}
WATER = {'L02_tiber', 'L10_sea', 'W_water_marks'}
S = Screen()
out = {}


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


H0 = sha(bpy.data.filepath)


class Caster:
    def __init__(self, box, pad=8.0, names=None):
        x0, x1, y0, y1 = box
        dg = bpy.context.evaluated_depsgraph_get()
        verts, polys, owner = [], [], []
        self.names = []
        for o in map_visible_objects():
            if names is not None and o.name not in names:
                continue
            ev = o.evaluated_get(dg); me = ev.to_mesh()
            if len(me.vertices) == 0:
                ev.to_mesh_clear(); continue
            co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
            Wv = (np.c_[co, np.ones(len(co))] @ np.array(o.matrix_world).T)[:, :3]
            P = S.project(Wv)
            if P[:, 0].max() < x0 - pad or P[:, 0].min() > x1 + pad or P[:, 1].max() < y0 - pad or P[:, 1].min() > y1 + pad:
                ev.to_mesh_clear(); continue
            k = len(self.names); self.names.append(o.name)
            b = len(verts); verts.extend(map(tuple, Wv))
            for p in me.polygons:
                polys.append([b + i for i in p.vertices]); owner.append(k)
            ev.to_mesh_clear()
        self.bvh = BVHTree.FromPolygons(verts, polys) if polys else None
        self.owner = np.array(owner)

    def hit(self, pt):
        if self.bvh is None:
            return None, None
        o, d = S.ray(pt)
        loc, nor, idx, dist = self.bvh.ray_cast(o, d)
        if idx is None:
            return None, None
        return self.names[self.owner[idx]], loc

    def grid(self, box, step):
        x0, x1, y0, y1 = box
        xs = np.arange(x0, x1 + 1e-9, step); ys = np.arange(y0, y1 + 1e-9, step)
        N = np.empty((len(ys), len(xs)), object); L = np.zeros((len(ys), len(xs), 3))
        for j, y in enumerate(ys):
            for i, x in enumerate(xs):
                n, loc = self.hit((x, y)); N[j, i] = n
                if loc is not None:
                    L[j, i] = loc[:]
        return xs, ys, N, L


def disk(r):
    R = int(math.ceil(r))
    return [(dy, dx) for dy in range(-R, R + 1) for dx in range(-R, R + 1) if dx * dx + dy * dy <= r * r + 1e-9]


def dilate(m, r):
    out = np.zeros_like(m); H, W = m.shape
    for dy, dx in disk(r):
        ys0, ys1 = max(0, dy), H + min(0, dy); xs0, xs1 = max(0, dx), W + min(0, dx)
        out[ys0:ys1, xs0:xs1] |= m[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
    return out


def erode(m, r):
    return ~dilate(~m, r)


def components(mask):
    lab = np.zeros(mask.shape, int); n = 0; sizes = []
    H, W = mask.shape
    for j in range(H):
        for i in range(W):
            if mask[j, i] and not lab[j, i]:
                n += 1; st = [(j, i)]; lab[j, i] = n; c = 0
                while st:
                    a, b = st.pop(); c += 1
                    for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        y, x = a + da, b + db
                        if 0 <= y < H and 0 <= x < W and mask[y, x] and not lab[y, x]:
                            lab[y, x] = n; st.append((y, x))
                sizes.append(c)
    return sizes


def road_gaps(name, box, step=0.25, r_close=1.5, r_open=0.22):
    C = Caster(box)
    xs, ys, N, L = C.grid(box, step)
    road = np.vectorize(lambda n: n in ROADSET)(N)
    terr = (N == 'T_land')
    closed = erode(dilate(road, r_close / step), r_close / step)
    gap = closed & ~road & terr
    gap_o = dilate(erode(gap, r_open / step), r_open / step) & gap
    a = step * step
    sz = components(gap_o)
    out[f'gap_{name}'] = {'box': box, 'road_pt2': round(float(closed.sum() * a), 1), 'terrain_in_road_pt2': round(float(gap.sum() * a), 1),
                          'after_open_pt2': round(float(gap_o.sum() * a), 1), 'p_percent': round(100 * float(gap_o.sum()) / max(1, closed.sum()), 3),
                          'largest_blob_pt2': round(max(sz) * a, 2) if sz else 0.0, 'blobs_ge_2pt2': int(sum(1 for s_ in sz if s_ * a >= 2.0))}


def road_over_water(box=(238.0, 285.0, 690.0, 735.0), step=0.25):
    C = Caster(box)
    land = bpy.data.objects['T_land']
    dg = bpy.context.evaluated_depsgraph_get()
    from common import bvh_of
    tb, _ = bvh_of([land])
    xs, ys, N, L = C.grid(box, step)
    over = 0; road_pts = []; water_pts = []
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            n = N[j, i]
            if n in ROADSET and not n.startswith('B_pons'):
                p = L[j, i]
                h = tb.ray_cast(Vector((p[0], p[1], p[2] + 0.01)), Vector((0, 0, -1)))[0]
                road_pts.append((x, y))
                if h is None:
                    over += 1
            elif n in ('L02_tiber', 'W_water_marks'):
                water_pts.append((x, y))
    gap = None
    if road_pts and water_pts:
        kd = KDTree(len(water_pts))
        for k, p in enumerate(water_pts):
            kd.insert((p[0], p[1], 0), k)
        kd.balance()
        # ignore the road samples next to the bridge (water under the deck)
        bw = Caster(box, names={'B_pons1', 'B_pons1_parapet0', 'B_pons1_parapet1'})
        ds = []
        for p in road_pts:
            d = kd.find((p[0], p[1], 0))[2]
            ds.append(d)
        gap = round(float(min(ds)), 2)
    out['road_over_water'] = {'box': box, 'samples_over_water': over, 'area_pt2': over * step * step, 'road_water_min_gap_pt': gap}


def bridge_cover():
    land = bpy.data.objects['T_land']
    from common import bvh_of
    tb, _ = bvh_of([land])
    res = {}
    for bn, box in (('B_pons1', (220.0, 330.0, 645.0, 720.0)), ('B_pons2', (240.0, 380.0, 935.0, 1025.0))):
        parts = {bn, bn + '_parapet0', bn + '_parapet1'}
        Cb = Caster(box, names=parts); Ca = Caster(box)
        step = 0.35
        sil = cov = 0
        for y in np.arange(box[2], box[3], step):
            for x in np.arange(box[0], box[1], step):
                nb, _ = Cb.hit((x, y))
                if nb is None:
                    continue
                sil += 1
                na, _ = Ca.hit((x, y))
                if na == 'T_land':
                    cov += 1
        o = bpy.data.objects[bn]; W = world_verts(o)
        k = 1.0 / S.world_per_pt(Vector(W.mean(0)))
        bur = []
        for x, y, z in W:
            h = tb.ray_cast(Vector((x, y, 50)), Vector((0, 0, -1)))[0]
            if h is not None and h.z > z:
                bur.append((h.z - z) * k)
        res[bn] = {'silhouette_pt2': round(sil * step * step, 1), 'covered_by_terrain_pt2': round(cov * step * step, 1),
                   'covered_percent': round(100 * cov / max(1, sil), 2), 'buried_vertices': len(bur),
                   'burial_max_pt': round(max(bur), 2) if bur else 0.0}
    out['bridges'] = res


def fields_checks():
    f = bpy.data.objects['F_centuriatio']; me = f.data
    W = world_verts(f)
    role = np.zeros(len(me.polygons), np.int32); me.attributes['rc_v12_13_field_role'].data.foreach_get('value', role)
    from common import bvh_of
    tb, _ = bvh_of([bpy.data.objects['T_land']])
    # island labels
    E = np.empty(len(me.edges) * 2, np.int32); me.edges.foreach_get('vertices', E); E = E.reshape(-1, 2)
    parent = np.arange(len(W))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for a, b in E:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    lab = np.array([find(i) for i in range(len(W))])
    flab = np.array([lab[p.vertices[0]] for p in me.polygons])
    kinds = {}
    for p, r in zip(me.polygons, role):
        kinds.setdefault(flab[p.index], []).append(r)
    kind = {k: ('straw' if np.bincount(v).argmax() == 13 else 'vine' if np.bincount(v).argmax() == 12 else 'plate') for k, v in kinds.items()}
    # terrain poking through plates: sample plate faces (centre + vertices pulled 15 % inwards)
    poke = []; nsamp = 0
    for p in me.polygons:
        if kind[flab[p.index]] != 'plate':
            continue
        V = W[list(p.vertices)]; c = V.mean(0)
        for q in [c] + [c + (v - c) * 0.85 for v in V]:
            nsamp += 1
            h = tb.ray_cast(Vector((q[0], q[1], 50)), Vector((0, 0, -1)))[0]
            if h is not None and h.z > q[2] - 0.005:
                poke.append((h.z - q[2], *S.to_pt(Vector(q))))
    poke.sort(reverse=True)
    out['plates_terrain_above'] = {'samples': nsamp, 'samples_with_ground_above_plate': len(poke),
                                   'worst': [[round(a, 3), round(x, 1), round(y, 1)] for a, x, y in poke[:12]]}
    # aqueduct: straw / vine islands near pier hulls, plate samples inside piers
    a = bpy.data.objects.get('L05_aqua_claudia')
    if a is not None:
        Wa = world_verts(a)
        Ea = np.empty(len(a.data.edges) * 2, np.int32); a.data.edges.foreach_get('vertices', Ea); Ea = Ea.reshape(-1, 2)
        pa = np.arange(len(Wa))

        def fa(x):
            while pa[x] != x:
                pa[x] = pa[pa[x]]; x = pa[x]
            return x
        for u, v in Ea:
            ru, rv = fa(u), fa(v)
            if ru != rv:
                pa[ru] = rv
        la = np.array([fa(i) for i in range(len(Wa))])
        bv = BVHTree.FromPolygons([tuple(v) for v in Wa], [list(p.vertices) for p in a.data.polygons])
        pen = []
        for k, kd_ in kind.items():
            idx = np.nonzero(lab == k)[0]
            for q in W[idx][::max(1, len(idx) // 30)]:
                # inside-test: ray up and count hits of the aqueduct (odd = inside)
                cnt = 0; o_ = Vector(q); d_ = Vector((0.0, 0.0, 1.0)); start = o_.copy()
                for _ in range(20):
                    h = bv.ray_cast(start, d_)
                    if h[0] is None:
                        break
                    cnt += 1; start = h[0] + d_ * 1e-4
                if cnt % 2 == 1:
                    pen.append((kd_, *S.to_pt(Vector(q)))); break
        out['aqueduct_penetration'] = {'islands_with_vertex_inside_aqueduct': len(pen),
                                       'by_kind': {t: sum(1 for p in pen if p[0] == t) for t in ('straw', 'vine', 'plate')},
                                       'at_pt': [[t, round(x, 1), round(y, 1)] for t, x, y in pen[:20]]}
    # straw float: lower ring vs support (plate faces or ground)
    pf = [p.index for p in me.polygons if kind[flab[p.index]] == 'plate']
    sb = BVHTree.FromPolygons([tuple(v) for v in W], [list(me.polygons[i].vertices) for i in pf])
    gaps = []; hs = []
    for k, kd_ in kind.items():
        if kd_ != 'straw':
            continue
        w = W[lab == k]; lv_ = np.unique(np.round(w[:, 2], 4)); rz = lv_[1] if len(lv_) > 1 else lv_[0]
        ring = w[np.abs(w[:, 2] - rz) < 1e-3]; hs.append(np.ptp(w[:, 2]))
        best = -np.inf
        for x, y, _ in ring:
            for b in (sb, tb):
                h = b.ray_cast(Vector((x, y, rz + 0.6)), Vector((0, 0, -1)))[0]
                if h is not None:
                    best = max(best, h.z); break
        gaps.append(rz - best)
    gaps = np.array(gaps); hs = np.array(hs)
    out['straws'] = {'n': int(len(gaps)), 'ring_gap_min_med_max': np.round(np.percentile(gaps, [0, 50, 100]), 3).tolist(),
                     'height_min_max_ratio': [round(float(hs.min()), 3), round(float(hs.max()), 3), round(float(hs.max() / hs.min()), 3)]}


def plate_cover(name, box, step=0.25):
    """terrain samples inside the F_centuriatio silhouette (ray hits the fields alone, but the scene shows T_land)."""
    Cf = Caster(box, names={'F_centuriatio'}); Ca = Caster(box)
    sil = cov = 0; pts = []
    for y in np.arange(box[2], box[3], step):
        for x in np.arange(box[0], box[1], step):
            n, _ = Cf.hit((x, y))
            if n is None:
                continue
            sil += 1
            na, _ = Ca.hit((x, y))
            if na == 'T_land':
                cov += 1; pts.append((x, y))
    out[f'plate_cover_{name}'] = {'box': box, 'silhouette_pt2': round(sil * step * step, 1), 'terrain_over_plate_pt2': round(cov * step * step, 2)}


def bench_gap():
    b = bpy.data.objects['R1_lab_bench']; W = world_verts(b)
    from common import bvh_of
    tb, _ = bvh_of([bpy.data.objects['T_land']])
    zb = W[:, 2].min(); bot = W[W[:, 2] < zb + 1e-4]
    c = bot.mean(0)
    k = 1.0 / S.world_per_pt(Vector(c))
    g = []
    for u in np.linspace(0.02, 0.98, 30):
        for v in np.linspace(0.02, 0.98, 8):
            # bilinear over the bottom quad (order by angle)
            ang = np.arctan2(bot[:, 1] - c[1], bot[:, 0] - c[0]); q = bot[np.argsort(ang)]
            p = (1 - u) * ((1 - v) * q[0] + v * q[1]) + u * ((1 - v) * q[3] + v * q[2])
            h = tb.ray_cast(Vector((p[0], p[1], 50)), Vector((0, 0, -1)))[0]
            if h is not None:
                g.append((zb - h.z) * k)
    g = np.array(g)
    out['bench_gap_pt'] = {'median': round(float(np.median(g)), 2), 'max': round(float(g.max()), 2), 'min': round(float(g.min()), 2),
                           'share_over_0.41': round(float((g > 0.41).mean()), 3)}


def tiber_sea():
    riv = bpy.data.objects['L02_tiber']; sea = bpy.data.objects['L10_sea']
    W = world_verts(riv)
    sb = BVHTree.FromPolygons([tuple(v) for v in world_verts(sea)], [list(p.vertices) for p in sea.data.polygons])
    d = []
    for x, y, z in W:
        h = sb.ray_cast(Vector((x, y, 5)), Vector((0, 0, -1)))[0]
        if h is not None:
            d.append(h.z - z)
    d = np.array(d)
    out['tiber_over_sea'] = {'vertices_over_sea': int(len(d)), 'min_depth_below_sea': round(float(d.min()), 4) if len(d) else None,
                             'within_0.01': int((np.abs(d) < 0.01).sum())}


road_gaps('w_west', (214.0, 250.0, 835.0, 915.0))
road_gaps('w_all', (215.0, 290.0, 696.0, 962.0))
road_gaps('sw_wedge', (352.0, 380.0, 975.0, 998.0))
road_gaps('sw_kerb', (495.0, 540.0, 995.0, 1032.0))
road_gaps('sw_all', (338.0, 590.0, 980.0, 1030.0))
road_gaps('land1', (495.0, 580.0, 488.0, 545.0))
road_gaps('land5', (880.0, 972.0, 850.0, 945.0))
road_gaps('nw', (294.0, 560.0, 500.0, 672.0), step=0.35)
road_gaps('appia', (842.0, 1191.0, 936.0, 995.0), step=0.35)
road_over_water()
bridge_cover()
fields_checks()
plate_cover('sw_bank', (170.0, 240.0, 1040.0, 1125.0))
plate_cover('sw_vine', (30.0, 115.0, 1235.0, 1295.0))
plate_cover('nw_vine', (265.0, 290.0, 465.0, 490.0))
bench_gap()
tiber_sea()
assert sha(bpy.data.filepath) == H0
Path(sys.argv[sys.argv.index('--') + 1]).write_text(json.dumps(out, indent=1))
print('MEASURE ' + json.dumps(out))
