"""Field colouring step (worker 'fields'): Roman farmland colours for F_centuriatio only.

How the furrows are modelled (measured on v8_11): every field plate is an open sheet, a 2-column x N-row quad grid.
Rows run along the ridges; consecutive inner rows alternate about +0.022 / -0.048 above / below the plate's own
plane (crest / trough, 0.306 apart), so each quad is one sloped facet that spans crest -> trough. The two end rows
are a raised lip (+0.07..0.12). Face normals point down (-z) and every facet centre sits at mid-height, which is why
"top faces by face-centre height" found nothing. Flat plates have the same lip but no alternation.

What this step does
1. Classifies every face island of F_centuriatio: stake (12 faces, 6 boundary edges), round straw pile (18 faces,
   12 boundary edges), ridged plate (row-height alternation > 0.03), flat plate.
2. Ridged plates: each crest->trough facet is cut once along the ridge (CROP_FRAC of the way from the crest), so the
   ridge top (crest side of both facets) gets the crop colour and the furrow bottom + end lips get the soil colour.
   The cut points lie on the original facet edges, so the silhouette and the surface do not move.
3. Crop type per plate (wheat / young barley / beans / ploughed fallow) and ground type per flat plate (pasture,
   hay meadow, stubble), chosen greedily with a fixed seed so that touching / nearby plates avoid the same type.
   Plates carrying stakes are vineyard / orchard ground (pasture or hay meadow), plates carrying straw piles are
   stubble or mown hay meadow. Stakes = vine-leaf green, piles = straw.
4. Roles are stored in the face attribute ATTR; a second run on an already processed mesh only re-applies
   materials from that attribute (no second cut), so the step is idempotent.

Run: Blender -b <any.blend> --factory-startup --python step.py -- <out.blend> [test_render_prefix]
"""
import bpy, bmesh, sys, json, runpy, math
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                      # .../nb_work
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
if not argv:
    raise SystemExit('usage: blender -b <in.blend> --factory-startup --python step.py -- <out.blend> [test_prefix]')
OUT = Path(argv[0]).resolve()
PREFIX = argv[1] if len(argv) > 1 else None
SRC = Path(bpy.data.filepath).resolve() if bpy.data.filepath else None
if SRC is not None and OUT == SRC:
    raise RuntimeError(f'refusing to overwrite the input blend {SRC}')
if OUT.name == 'roman_concrete_narrative_v8_11.blend':
    raise RuntimeError('refusing to write over the v8_11 base file name')

OBJ = 'F_centuriatio'
ATTR = 'rc_v12_13_field_role'
SEED = 1313
CROP_FRAC = 0.5          # fraction of each crest->trough facet painted as crop (measured from the crest)
RIDGE_ALT_MIN = 0.03     # mean |2nd difference| of row heights; measured: ridged 0.06-0.08, flat < 0.01
TOUCH_GAP, NEAR_GAP = 0.1, 1.5   # world units between plate footprints (1 unit ~ 6.5pt on screen)

# Diffuse colours (sRGB hex). Workbench STUDIO light renders up-facing faces at about the diffuse colour; facets
# turned from the light about 8 L* darker (measured on the v8_11 render). Targets: Oklch C <= 0.09, hue 60-130,
# rendered L* 62-84. Slot order is fixed (role id = material slot index; slot 0 keeps the original base material).
PALETTE = [
    ('soil_wheat',   '#BFA889'), ('crop_wheat',   '#DBC58A'),
    ('soil_barley',  '#BAA284'), ('crop_barley',  '#B6C18E'),
    ('soil_bean',    '#C9B699'), ('crop_bean',    '#9EAF7E'),
    ('soil_fallow',  '#B89F82'), ('crop_fallow',  '#CCBCA2'),
    ('ground_pasture', '#BFC594'), ('ground_meadow', '#D3CA96'), ('ground_stubble', '#DFD1A6'),
    ('vine', '#95A773'), ('straw', '#DABE81'),
]
CROPS = ['wheat', 'barley', 'bean', 'fallow']
BASE_MAT = 'RC.v12.base_field'
report = {'input': str(SRC), 'output': str(OUT)}


def lin(hexv):
    return tuple(((int(hexv[i:i + 2], 16) / 255 + 0.055) / 1.055) ** 2.4 if int(hexv[i:i + 2], 16) / 255 > 0.04045
                 else int(hexv[i:i + 2], 16) / 255 / 12.92 for i in (1, 3, 5))


ob = bpy.data.objects.get(OBJ)
if ob is None or ob.type != 'MESH':
    raise RuntimeError(f'object {OBJ!r} (mesh) not found in {SRC}')
if ob.data.users > 1:
    ob.data = ob.data.copy()
me = ob.data

# ---- materials (same template as the original field material, so only the colour differs) ----
template = bpy.data.materials.get(BASE_MAT)
if template is None:
    template = me.materials[0] if len(me.materials) and me.materials[0] else None
mats = []
for key, hexv in PALETTE:
    name = f'RC.v12_13.field_{key}'
    m = bpy.data.materials.get(name)
    if m is None:
        m = template.copy() if template is not None else bpy.data.materials.new(name)
        m.name = name
    m.diffuse_color = (*lin(hexv), 1.0)
    if m.node_tree:
        for n in m.node_tree.nodes:
            if n.type == 'BSDF_PRINCIPLED':
                n.inputs['Base Color'].default_value = (*lin(hexv), 1.0)
    mats.append(m)
ROLE = {key: i + 1 for i, (key, _) in enumerate(PALETTE)}       # 0 = untouched (base material)


def islands(bm):
    seen = set(); out = []
    for f in bm.faces:
        if f.index in seen: continue
        st = [f]; seen.add(f.index); fs = []
        while st:
            a = st.pop(); fs.append(a)
            for e in a.edges:
                for g in e.link_faces:
                    if g.index not in seen: seen.add(g.index); st.append(g)
        out.append(fs)
    return out


def rows_along(fs, verts, along_mask_fn):
    """connected components of verts through edges accepted by along_mask_fn"""
    vid = {v: i for i, v in enumerate(verts)}; parent = list(range(len(verts)))
    def find(i):
        while parent[i] != i: parent[i] = parent[parent[i]]; i = parent[i]
        return i
    for e in {e for f in fs for e in f.edges}:
        if along_mask_fn(e):
            a, b = find(vid[e.verts[0]]), find(vid[e.verts[1]]); parent[a] = b
    comp = {}
    for v in verts: comp.setdefault(find(vid[v]), []).append(v)
    return list(comp.values())


already = ATTR in me.attributes
mw = ob.matrix_world
if not already:
    bm = bmesh.new(); bm.from_mesh(me)
    # layers first: adding a layer later invalidates the element wrappers held in the island lists
    lay = bm.faces.layers.int.get(ATTR) or bm.faces.layers.int.new(ATTR)
    fpl = bm.faces.layers.int.new('_rc_tmp_plate')
    vcl = bm.verts.layers.int.new('_rc_tmp_class')
    bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    W = lambda v: np.array((mw @ v.co)[:])
    plates, props = [], []
    for fs in islands(bm):
        edges = {e for f in fs for e in f.edges}
        bnd = sum(1 for e in edges if len(e.link_faces) == 1)
        verts = sorted({v for f in fs for v in f.verts}, key=lambda v: v.index)
        P = np.array([W(v) for v in verts]); ext = P.max(0) - P.min(0)
        if len(fs) == 12 and bnd == 6 and max(ext[0], ext[1]) < 0.5:
            props.append(('vine', fs)); continue
        if len(fs) == 18 and bnd == 12 and max(ext[0], ext[1]) < 1.2:
            props.append(('straw', fs)); continue
        A = np.c_[P[:, 0], P[:, 1], np.ones(len(P))]; cf = np.linalg.lstsq(A, P[:, 2], rcond=None)[0]
        res = {v: float(p[2] - A[i] @ cf) for i, (v, p) in enumerate(zip(verts, P))}
        # two grid directions from the edges
        ang = []
        for e in edges:
            d = W(e.verts[1]) - W(e.verts[0])
            if math.hypot(d[0], d[1]) > 0.05: ang.append(math.atan2(d[1], d[0]) % math.pi)
        hist = np.histogram(ang, bins=36, range=(0, math.pi))[0]; th1 = (np.argmax(hist) + 0.5) * math.pi / 36
        best = None
        for cross in (th1, th1 + math.pi / 2):
            cd = np.array((math.cos(cross), math.sin(cross)))
            def is_along(e, cd=cd):
                d = W(e.verts[1]) - W(e.verts[0]); n = math.hypot(d[0], d[1])
                return n > 0.05 and abs(d[0] * cd[0] + d[1] * cd[1]) / n < 0.5
            rows = rows_along(fs, verts, is_along)
            rows.sort(key=lambda R: float(np.mean([W(v)[:2] @ cd for v in R])))
            rr = np.array([np.mean([res[v] for v in R]) for R in rows])
            inner = rr[1:-1]
            if len(inner) >= 3:
                d2 = inner[1:-1] - (inner[:-2] + inner[2:]) / 2; alt = float(np.abs(d2).mean())
            else:
                d2 = np.zeros(0); alt = 0.0
            if best is None or alt > best[0]: best = (alt, rows, d2)
        alt, rows, d2 = best
        c = P.mean(0)
        pl = dict(fs=fs, verts=verts, rows=rows, alt=alt, c=c, mn=P.min(0), mx=P.max(0), ridged=alt > RIDGE_ALT_MIN)
        if pl['ridged']:
            # parity of crest rows among inner rows (inner row k <-> rows[k+1]); d2[j] belongs to inner row j+1
            par = np.array([(j + 1) % 2 for j in range(len(d2))])
            m0 = d2[par == 0].mean() if (par == 0).any() else 0; m1 = d2[par == 1].mean() if (par == 1).any() else 0
            crest_par = 0 if m0 > m1 else 1
            agree = float(np.mean([(d2[j] > 0) == (par[j] == crest_par) for j in range(len(d2))]))
            pl['agree'] = agree
            cls = {}
            for k, R in enumerate(rows):
                tag = 'END' if k in (0, len(rows) - 1) else ('CREST' if (k - 1) % 2 == crest_par else 'TROUGH')
                for v in R: cls[v] = tag
            pl['cls'] = cls
        plates.append(pl)

    # ---- props sit on which plate (xy footprint) ----
    for pl in plates: pl['n_vine'] = pl['n_straw'] = 0
    off_plate = {'vine': 0, 'straw': 0}
    for kind, fs in props:
        c = np.mean([W(v) for f in fs for v in f.verts], 0); hit = False
        for pl in plates:
            if pl['mn'][0] - 0.05 <= c[0] <= pl['mx'][0] + 0.05 and pl['mn'][1] - 0.05 <= c[1] <= pl['mx'][1] + 0.05:
                pl['n_' + kind] += 1; hit = True; break
        if not hit: off_plate[kind] += 1

    # ---- type per plate: fixed seed, avoid the same type on touching / nearby plates ----
    plates.sort(key=lambda p: (round(float(p['c'][0]), 2), round(float(p['c'][1]), 2)))
    def gap(a, b):
        dx = max(a['mn'][0] - b['mx'][0], b['mn'][0] - a['mx'][0], 0.0)
        dy = max(a['mn'][1] - b['mx'][1], b['mn'][1] - a['mx'][1], 0.0)
        return math.hypot(dx, dy)
    nb = [[] for _ in plates]
    for i in range(len(plates)):
        for j in range(i + 1, len(plates)):
            a, b = plates[i], plates[j]; g = gap(a, b)
            if g <= NEAR_GAP:
                ox = min(a['mx'][0], b['mx'][0]) - max(a['mn'][0], b['mn'][0])
                oy = min(a['mx'][1], b['mx'][1]) - max(a['mn'][1], b['mn'][1])
                w = 1.0 if g <= TOUCH_GAP and max(ox, oy) > 0.3 else 0.35   # shared side vs corner / nearby
                nb[i].append((j, w)); nb[j].append((i, w))
    rng = np.random.default_rng(SEED)
    used = {}
    order = list(range(len(plates)))
    for i in order:
        p = plates[i]
        if p['ridged']: cands = CROPS
        elif p['n_vine']: cands = ['ground_pasture', 'ground_meadow']
        elif p['n_straw']: cands = ['ground_stubble', 'ground_meadow']
        else: cands = ['ground_pasture', 'ground_meadow', 'ground_stubble']
        jitter = rng.random(len(cands)) * 1e-3
        cost = []
        for k, t in enumerate(cands):
            same = sum(w for j, w in nb[i] if plates[j].get('type') == t)
            cost.append(same + 0.02 * used.get(t, 0) + jitter[k])
        t = cands[int(np.argmin(cost))]; p['type'] = t; used[t] = used.get(t, 0) + 1

    # ---- roles of props and flat plates, plate id + vertex class layers for the ridged ones ----
    # (BMesh python wrappers do not survive bmesh.ops, so everything the cut needs lives in custom-data layers)
    END, CREST, TROUGH, MID = 1, 2, 3, 4
    for kind, fs in props:
        for f in fs: f[lay] = ROLE[kind]; f[fpl] = 0
    code = {'END': END, 'CREST': CREST, 'TROUGH': TROUGH}
    for pi_, p in enumerate(plates):
        for f in p['fs']:
            f[fpl] = pi_ + 1
            f[lay] = 0 if p['ridged'] else ROLE[p['type']]
        if p['ridged']:
            for v, tag in p['cls'].items(): v[vcl] = code[tag]

    # ---- cut every crest->trough facet once along the ridge ----
    cut = []
    for p in plates:
        if not p['ridged']: continue
        for e in sorted({e for f in p['fs'] for e in f.edges}, key=lambda e: e.index):
            if {e.verts[0][vcl], e.verts[1][vcl]} == {CREST, TROUGH}: cut.append(e)
    nf0 = len(bm.faces)
    r = bmesh.ops.subdivide_edges(bm, edges=cut, cuts=1, use_grid_fill=True)
    new_verts = [g for g in r['geom_inner'] if isinstance(g, bmesh.types.BMVert)]
    for v in new_verts: v[vcl] = MID          # layer values of new verts are interpolated; reset first
    for v in new_verts:
        nbv = [e.other_vert(v) for e in v.link_edges]
        cr = [u for u in nbv if u[vcl] == CREST]; tr = [u for u in nbv if u[vcl] == TROUGH]
        if len(cr) != 1 or len(tr) != 1:
            raise RuntimeError(f'cut vertex without one crest + one trough neighbour ({len(cr)}, {len(tr)})')
        v.co = cr[0].co + CROP_FRAC * (tr[0].co - cr[0].co)
    bm.faces.ensure_lookup_table()
    report['split'] = {'edges_cut': len(cut), 'new_vertices': len(new_verts), 'faces_before': nf0,
                       'faces_after': len(bm.faces), 'crop_frac': CROP_FRAC}

    # ---- roles of the ridged plates' faces from the vertex classes ----
    anomalies = 0
    for f in bm.faces:
        pid = f[fpl]
        if pid and plates[pid - 1]['ridged']:
            t = plates[pid - 1]['type']; cl = {v[vcl] for v in f.verts}
            if END in cl or cl <= {MID, TROUGH}: f[lay] = ROLE['soil_' + t]
            elif cl <= {CREST, MID}: f[lay] = ROLE['crop_' + t]
            else: f[lay] = ROLE['soil_' + t]; anomalies += 1
        f.material_index = f[lay]
    bm.faces.layers.int.remove(fpl); bm.verts.layers.int.remove(vcl)
    bm.to_mesh(me); bm.free(); me.update()
    rid = [p for p in plates if p['ridged']]
    report['islands'] = {'plates': len(plates), 'ridged': len(rid), 'flat': len(plates) - len(rid),
                         'stakes': sum(1 for k, _ in props if k == 'vine'), 'straw_piles': sum(1 for k, _ in props if k == 'straw'),
                         'props_off_plate': off_plate}
    report['ridge_alt_range'] = {'ridged': [round(min(p['alt'] for p in rid), 4), round(max(p['alt'] for p in rid), 4)],
                                 'flat_max': round(max([p['alt'] for p in plates if not p['ridged']] or [0]), 4)}
    report['ridge_parity_agreement_min'] = round(min(p['agree'] for p in rid), 3)
    report['face_anomalies'] = anomalies
    tc = {}
    for p in plates: tc[p['type']] = tc.get(p['type'], 0) + 1
    report['plate_types'] = tc
    same_touch = sum(1 for i, p in enumerate(plates) for j, w in nb[i] if j > i and w == 1.0 and plates[j]['type'] == p['type'])
    same_near = sum(1 for i, p in enumerate(plates) for j, w in nb[i] if j > i and w < 1.0 and plates[j]['type'] == p['type'])
    n_touch = sum(1 for i in range(len(plates)) for j, w in nb[i] if j > i and w == 1.0)
    n_near = sum(1 for i in range(len(plates)) for j, w in nb[i] if j > i and w < 1.0)
    report['neighbour_same_type'] = {'touching_pairs': n_touch, 'touching_same': same_touch,
                                     'near_pairs': n_near, 'near_same': same_near}
else:
    report['reused_roles'] = True

# ---- material slots in fixed order, material_index = stored role ----
base = bpy.data.materials.get(BASE_MAT)
me.materials.clear()
me.materials.append(base)
for m in mats: me.materials.append(m)
roles = np.zeros(len(me.polygons), dtype=np.int32)
me.attributes[ATTR].data.foreach_get('value', roles)
me.polygons.foreach_set('material_index', roles)
me.update()
cnt = np.bincount(roles, minlength=len(PALETTE) + 1)
report['faces_by_material'] = {(BASE_MAT if i == 0 else mats[i - 1].name): int(c) for i, c in enumerate(cnt) if c}
report['palette'] = {f'RC.v12_13.field_{k}': h for k, h in PALETTE}
report['faces_total'] = len(me.polygons)
print('REPORT ' + json.dumps(report, ensure_ascii=False))

OUT.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT), copy=False)
OUT.with_suffix('.step.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
if PREFIX:
    H = runpy.run_path(str(ROOT / 'scripts/integrate_assets.py'), run_name='helpers')
    print('RENDER ' + json.dumps(H['render_two_pass'](Path(PREFIX + '.png'))))
