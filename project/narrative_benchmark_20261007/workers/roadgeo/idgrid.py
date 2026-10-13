"""idgrid.py - read-only visibility measurement for the roadgeo worker.

Blender -b <in.blend> --factory-startup --python idgrid.py -- <out.json> [--png-dir DIR] [--tag TAG]

Camera rays (the poster camera, through each sample point of a poster-point grid) are cast against every
render-visible map object whose screen box meets the region; the first hit gives (object, material) = what the map
pass shows there. Regions and checks:

  A  south core road bottom row, x 560-670 / y 1000-1032 (task: "x 560-670, y 1015-1025" band):
     - per 0.5 pt column: road band = first..last road hit; holes = T_land samples inside the band;
       'bottom_row_ok' = a paver-material sample lies within 1.2 pt above the south kerb's top edge
     - per paver of R_core_road whose centre projects into the box: visible fraction of its top face
       (5x5 inset samples, ray hits the road mesh first)
  B  Via Ostiensis + the two landing plates: terrain samples enclosed by road samples
     (closing of the road mask, r = 1.5 pt, then an opening r = 0.35 pt to drop sub-pixel paver joints)
     = 'gap' samples where the paper-coloured ground shows between paver ends. Reported per region in samples and pt^2.
Writes optional PNG class maps (road paver / kerb / terrain / other / gap highlighted) for eyeballing.
Never saves the blend.
"""
import bpy, sys, json, hashlib, math
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / 'layout'))
from common import Screen, world_verts, map_visible_objects   # noqa: E402

ROADSET = {'R_core_road', 'R_via_ostiensis', 'R_via_appia', 'R1_road_landing1', 'R1_road_landing5', 'R_roadgeo_ostiensis_junction_fill',
           'R4_bridge_west_bed', 'R1_road5_bed', 'B_pons1', 'B_pons2',
           'B_pons1_parapet0', 'B_pons1_parapet1', 'B_pons2_parapet0', 'B_pons2_parapet1'}
PAVE = 'RC.road.selce_basalt'
KERB = 'RC.road.umbo_limestone'
REGIONS_B = {   # name: (x0, x1, y0, y1) poster pt, step pt
    'ost_upper': ((300, 410, 995, 1120), 0.25),
    'ost_mid': ((180, 330, 1110, 1260), 0.25),
    'ost_low': ((90, 230, 1250, 1400), 0.25),
    'ost_end': ((60, 170, 1390, 1470), 0.25),
    'land1': ((495, 580, 490, 545), 0.2),
    'land5': ((880, 970, 850, 945), 0.2),
}
REGION_A = ((560, 670, 998, 1032), 0.2)
REF_A = ((440, 530, 985, 1020), 0.2)     # healthy stretch of the same south road, same checks (reference)


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


class Caster:
    def __init__(self, S, box, pad=6.0):
        x0, x1, y0, y1 = box
        dg = bpy.context.evaluated_depsgraph_get()
        verts, polys, owner, mat = [], [], [], []
        self.names = []
        for o in map_visible_objects():
            ev = o.evaluated_get(dg); me = ev.to_mesh()
            if len(me.vertices) == 0:
                ev.to_mesh_clear(); continue
            co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
            M = np.array(o.matrix_world); Wv = (np.c_[co, np.ones(len(co))] @ M.T)[:, :3]
            P = S.project(Wv)
            if P[:, 0].max() < x0 - pad or P[:, 0].min() > x1 + pad or P[:, 1].max() < y0 - pad or P[:, 1].min() > y1 + pad:
                ev.to_mesh_clear(); continue
            k = len(self.names); self.names.append(o.name)
            slots = [s.material.name if s.material else '' for s in o.material_slots]
            b = len(verts); verts.extend(map(tuple, Wv))
            mi = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', mi)
            for p, m in zip(me.polygons, mi):
                polys.append([b + i for i in p.vertices]); owner.append(k)
                mat.append(slots[m] if 0 <= m < len(slots) else '')
            ev.to_mesh_clear()
        self.bvh = BVHTree.FromPolygons(verts, polys)
        self.owner = np.array(owner); self.mat = mat
        self.S = S

    def hit(self, pt):
        o, d = self.S.ray(pt)
        loc, nor, idx, dist = self.bvh.ray_cast(o, d)
        if idx is None:
            return None, '', None
        return self.names[self.owner[idx]], self.mat[idx], loc

    def grid(self, box, step):
        x0, x1, y0, y1 = box
        xs = np.arange(x0, x1 + 1e-9, step); ys = np.arange(y0, y1 + 1e-9, step)
        cls = np.zeros((len(ys), len(xs)), np.int8)   # 0 other/none, 1 road paver, 2 road kerb, 3 terrain, 4 road other
        objn = np.empty((len(ys), len(xs)), object)
        for j, y in enumerate(ys):
            for i, x in enumerate(xs):
                n, m, _ = self.hit((x, y)); objn[j, i] = n
                if n in ROADSET:
                    cls[j, i] = 1 if m == PAVE else (2 if m == KERB else 4)
                elif n == 'T_land':
                    cls[j, i] = 3
        return xs, ys, cls, objn


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


def gap_mask(cls, step, r_close=1.5, r_open=0.35):
    road = (cls == 1) | (cls == 2) | (cls == 4)
    rc, ro = r_close / step, r_open / step
    closed = erode(dilate(road, rc), rc)
    gap = closed & ~road & (cls == 3)
    gap_open = dilate(erode(gap, ro), ro) & gap
    return gap, gap_open


def save_png(path, cls, extra=None):
    H, W = cls.shape
    col = np.array([[235, 235, 235], [110, 110, 110], [200, 190, 160], [250, 240, 215], [150, 120, 100]], np.float32) / 255
    rgb = col[cls]
    if extra is not None:
        rgb[extra] = (1.0, 0.0, 0.0)
    img = bpy.data.images.new('idgrid_tmp', W, H, alpha=True)
    px = np.concatenate([rgb[::-1], np.ones((H, W, 1), np.float32)], axis=2)
    img.pixels.foreach_set(px.ravel())
    img.filepath_raw = str(path); img.file_format = 'PNG'; img.save()
    bpy.data.images.remove(img)


def check_A(S, box, step, png=None):
    C = Caster(S, box)
    xs, ys, cls, objn = C.grid(box, step)
    col_stats = []
    holes_total = 0; bad_cols = 0; cols = 0
    for i, x in enumerate(xs):
        if abs((x - xs[0]) / 0.5 - round((x - xs[0]) / 0.5)) > 1e-6:
            continue
        c = cls[:, i]
        road_idx = np.nonzero((c == 1) | (c == 2))[0]
        if len(road_idx) == 0:
            continue
        cols += 1
        a, b = road_idx[0], road_idx[-1]
        holes = int((c[a:b + 1] == 3).sum()); holes_total += holes
        kerb_s = np.nonzero(c == 2)[0]
        # south kerb = last kerb run in the column
        ok = False
        if len(kerb_s):
            ks = kerb_s[-1]
            while ks - 1 >= 0 and c[ks - 1] == 2:
                ks -= 1
            above = c[max(0, ks - int(round(1.2 / step))):ks]
            ok = bool((above == 1).any())
        bad_cols += 0 if ok else 1
        col_stats.append([round(float(x), 2), holes, ok])
    # per-paver top-face visibility
    road = bpy.data.objects['R_core_road']; me = road.data; W = world_verts(road)
    vis = []
    mw = road.matrix_world
    for p in me.polygons:
        if p.material_index != 0 or len(p.vertices) != 4:
            continue
        n = (mw.to_3x3() @ p.normal).normalized()
        if n.z < 0.8 or p.area < 0.05:
            continue
        cpt = S.to_pt(mw @ p.center)
        if not (box[0] <= cpt[0] <= box[1] and box[2] <= cpt[1] <= box[3]):
            continue
        V = W[list(p.vertices)]; c = V.mean(0); seen = tot = 0
        for u in np.linspace(-0.4, 0.4, 5):
            for v in np.linspace(-0.4, 0.4, 5):
                q = c + ((V[1] + V[2]) / 2 - (V[0] + V[3]) / 2) * u + ((V[2] + V[3]) / 2 - (V[0] + V[1]) / 2) * v
                pt = S.to_pt(Vector(q)); nme, m, loc = C.hit(pt); tot += 1
                if nme == 'R_core_road' and loc is not None and (Vector(q) - loc).length < 0.03:
                    seen += 1
        vis.append([round(float(cpt[0]), 1), round(float(cpt[1]), 1), round(float(c[2]), 3), seen / tot])
    v = np.array([r[3] for r in vis]) if vis else np.zeros(0)
    if png:
        save_png(png, cls)
    return {'box': list(box), 'step_pt': step, 'columns': cols, 'hole_samples_in_road_band': holes_total,
            'hole_area_pt2': round(holes_total * step * step, 2),
            'columns_without_paver_above_south_kerb': bad_cols,
            'bad_columns_x': [c[0] for c in col_stats if not c[2]],
            'pavers_top_faces': len(vis), 'pavers_fully_visible(>=0.96)': int((v >= 0.96).sum()),
            'pavers_lt_50pct_visible': int((v < 0.5).sum()), 'pavers_lt_90pct_visible': int((v < 0.9).sum()),
            'paver_visible_fraction_mean': round(float(v.mean()), 4) if len(v) else None,
            'worst_pavers': sorted(vis, key=lambda r: r[3])[:12]}


def check_B(S, name, box, step, png=None):
    C = Caster(S, box)
    xs, ys, cls, objn = C.grid(box, step)
    gap, gap_open = gap_mask(cls, step)
    if png:
        save_png(png, cls, gap_open)
    return {'box': list(box), 'step_pt': step, 'gap_samples_raw': int(gap.sum()), 'gap_samples': int(gap_open.sum()),
            'gap_area_pt2': round(float(gap_open.sum()) * step * step, 2),
            'road_samples': int(((cls == 1) | (cls == 2) | (cls == 4)).sum()),
            'terrain_samples': int((cls == 3).sum())}


def main():
    argv = sys.argv[sys.argv.index('--') + 1:]
    out = Path(argv[0]).resolve()
    png_dir = None; tag = 'x'; only = None
    i = 1
    while i < len(argv):
        if argv[i] == '--png-dir': png_dir = Path(argv[i + 1]).resolve(); png_dir.mkdir(parents=True, exist_ok=True); i += 2
        elif argv[i] == '--tag': tag = argv[i + 1]; i += 2
        elif argv[i] == '--only': only = set(argv[i + 1].split(',')); i += 2
        else: raise SystemExit('bad arg ' + argv[i])
    h0 = sha(bpy.data.filepath)
    S = Screen()
    res = {'blend': bpy.data.filepath, 'blend_sha256': h0}
    if only is None or 'A' in only:
        res['A'] = check_A(S, *REGION_A, png=png_dir / f'{tag}_idA.png' if png_dir else None)
        res['A_reference_healthy'] = check_A(S, *REF_A)
    res['B'] = {}
    for n, (box, step) in REGIONS_B.items():
        if only is not None and n not in only:
            continue
        res['B'][n] = check_B(S, n, box, step, png=png_dir / f'{tag}_id_{n}.png' if png_dir else None)
    res['B_total_gap_samples'] = sum(v['gap_samples'] for v in res['B'].values())
    res['B_total_gap_area_pt2'] = round(sum(v['gap_area_pt2'] for v in res['B'].values()), 2)
    assert sha(bpy.data.filepath) == h0
    out.write_text(json.dumps(res, indent=1))
    print('IDGRID', json.dumps({k: (v if k != 'A' else {kk: v[kk] for kk in v if kk not in ('worst_pavers', 'bad_columns_x')})
                               for k, v in res.items() if k not in ('B',)}))
    print('IDGRID_B', json.dumps({n: [v['gap_samples'], v['gap_area_pt2']] for n, v in res['B'].items()}))


if __name__ == '__main__':
    main()
