"""v8.3: apply verified round-1 critic findings to the Blender map (Figma text fixes are done separately).

Run: blender -b out/roman_concrete_narrative_v8_2.blend --factory-startup --python scripts/review_r1_fixes_v8_3.py -- <test|final> [test_prefix]
Never overwrites v8_2; final saves out/roman_concrete_narrative_v8_3.blend.
"""
import bpy, bmesh, math, json, sys, runpy
from pathlib import Path
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'out/roman_concrete_narrative_v8_2.blend'
OUT = ROOT / 'out/roman_concrete_narrative_v8_3.blend'
argv = sys.argv[sys.argv.index('--') + 1:]
MODE = argv[0]
assert Path(bpy.data.filepath).resolve() == SRC.resolve()
W_PT, H_PT = 1191, 1684
sc = bpy.context.scene
cam = sc.camera
O = bpy.data.objects
report = {}

def lin(h):
    return tuple(((int(h[i:i + 2], 16) / 255 + 0.055) / 1.055) ** 2.4 for i in (1, 3, 5))

def set_color(mat, hexv):
    c = (*lin(hexv), 1)
    mat.diffuse_color = c
    if mat.node_tree:
        b = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if b: b.inputs['Base Color'].default_value = c

def new_mat(name, hexv, like='RC.v12.roman_stone'):
    m = bpy.data.materials.get(name) or bpy.data.materials[like].copy()
    m.name = name; set_color(m, hexv); return m

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
def hit(bvh, pt):
    h, n, i, d = bvh.ray_cast(*ray(pt)); return (h, n) if h is not None else (None, None)

GROUND = bvh_of([O['T_land']] + [o for o in bpy.data.collections['35_FIELDS_ROADS'].objects if o.type == 'MESH' and not o.hide_render])
SEA = bvh_of([O['L10_sea']])
TERRAIN = bvh_of([O['T_land']])

def world_per_pt(p):
    """world length that spans 1pt on screen at point p (horizontal camera-right direction)."""
    r = cam.matrix_world.col[0].xyz.normalized()
    return 1.0 / np.linalg.norm(to_pt(p + r) - to_pt(p))

def strip_on(bvh, pts, width_pt, mat, name, lift=0.02):
    """flat ribbon following screen polyline pts, projected onto bvh surface (cracks, stains)."""
    hits = [hit(bvh, p) for p in pts]
    assert all(h[0] is not None for h in hits), (name, pts)
    bm = bmesh.new(); left, right = [], []
    for k, (h, n) in enumerate(hits):
        a = hits[max(k - 1, 0)][0]; b = hits[min(k + 1, len(hits) - 1)][0]
        t = (b - a).normalized(); side = n.cross(t).normalized()
        w = width_pt * world_per_pt(h) / 2
        base = h + n * lift * world_per_pt(h)
        left.append(bm.verts.new(base + side * w)); right.append(bm.verts.new(base - side * w))
    for k in range(len(pts) - 1):
        bm.faces.new((left[k], left[k + 1], right[k + 1], right[k]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    o = O.new(name, me); return o

def blob_at(bvh, pt, radius_pt, mat, name, flat=1.0):
    h, n = hit(bvh, pt); assert h is not None, name
    r = radius_pt * world_per_pt(h)
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=r)
    for v in bm.verts: v.co.z *= flat
    bm.to_mesh(me); bm.free(); me.materials.append(mat)
    o = O.new(name, me); o.location = h + n * r * 0.6; return o

def link(objs, colname):
    col = bpy.data.collections.get(colname) or bpy.data.collections.new(colname)
    if col.name not in sc.collection.children: sc.collection.children.link(col)
    for o in objs:
        for c in list(o.users_collection): c.objects.unlink(o)
        col.objects.link(o)
    return col

# 1. colours (color F1/F2/F6/F7, illustration m4)
set_color(bpy.data.materials['RC.v12.base_sea_river'], '#A0CFCF')
set_color(bpy.data.materials['RC.v12.base_line'], '#3E3A31')
set_color(bpy.data.materials['RC.v12.base_lime_specimen_matrix'], '#8D6E5D')
for n in ('H_book1', 'H_book2'):
    for s in O[n].material_slots: s.material = bpy.data.materials['RC.v12.toolwood']
for s in O['H_book1_pages'].material_slots: s.material = bpy.data.materials['RC.v12.linen']
heavy = new_mat('RC.v12_3.stone_heavy', '#7A6D58')
for s in O['D3_heavy'].material_slots: s.material = heavy
report['colours'] = 'sea #A0CFCF, line #3E3A31, specimen #8D6E5D, books wood/linen, D3_heavy #7A6D58'

# 2. retire ambiguous / superseded objects (infographic F6, illustration A5, layout F5, color F6)
HIDE = ['L03_forum_vesta', 'L04_palatine', 'L04_palatine_arch', 'S_lab_island', 'S_lead00', 'S_lead01',
        'S_lead_dot0', 'S_lead_dot1', 'S_pin_privernum', 'S_pin_privernum_dot']
for n in HIDE:
    O[n].hide_render = True; O[n].hide_viewport = True
report['hidden'] = HIDE

# 3. kiln: drop the stray statue on the dome (z > 6.45)
k = O['D2_lime_kiln']
if k.data.users > 1: k.data = k.data.copy()
bm = bmesh.new(); bm.from_mesh(k.data); mw = k.matrix_world
kill = [v for v in bm.verts if (mw @ v.co).z > 6.45]
bmesh.ops.delete(bm, geom=kill, context='VERTS')
edges = [e for e in bm.edges if e.is_boundary]
bmesh.ops.holes_fill(bm, edges=edges, sides=0)
bm.to_mesh(k.data); bm.free()
report['kiln_statue_verts_removed'] = len(kill)

# 4. mixing scene: the right-hand figure is 1.44x the left one -> scale 0.7 about her feet
mix = O['C2_hot_mixing']
if mix.data.users > 1: mix.data = mix.data.copy()
mw = mix.matrix_world; inv = mw.inverted()
co = np.array([mw @ v.co for v in mix.data.vertices])
scr = np.array([to_pt(Vector(p)) for p in co])
top = (co[:, 2] > 3.0) & (scr[:, 0] > 165)
axis = co[top, :2].mean(0)
dxy = np.hypot(co[:, 0] - axis[0], co[:, 1] - axis[1])
body_r = np.percentile(dxy[top], 98) * 1.35
sel = (dxy < body_r) & (co[:, 2] > 0.05) & (scr[:, 0] > 160)
feet = co[sel, 2].min()
piv = Vector((axis[0], axis[1], feet))
for i in np.nonzero(sel)[0]:
    p = Vector(co[i]); mix.data.vertices[i].co = inv @ (piv + (p - piv) * 0.7)
mix.data.update()
report['mixing_woman'] = {'verts': int(sel.sum()), 'pivot': [round(c, 2) for c in piv], 'height_before': round(float(co[sel, 2].max() - feet), 2)}

# 5. crack sequence: water drops onto step 1, calcium dots and a water thread on step 2/1
drops = O['NB_core4_sequence_GRAY04']
c = Vector(np.mean([drops.matrix_world @ v.co for v in drops.data.vertices], axis=0))
s = to_pt(c); o_, d_ = ray((s[0] - 73, s[1]))
t = (c.z - o_.z) / d_.z
drops.location += (o_ + d_ * t) - c
cubes = bvh_of([O['NB_core4_sequence_GRAY03']])
calc = bpy.data.materials['RC.v12.base_lime_calcium_crystal']
water = bpy.data.materials['RC.v12.base_water_process']
seq_new = [blob_at(cubes, p, 1.3, calc, f'R1_calcium_dot{i}') for i, p in enumerate([(739, 1211), (742, 1219), (745, 1227)])]
seq_new.append(strip_on(cubes, [(667, 1205), (670, 1213), (668, 1221), (672, 1230)], 1.6, water, 'R1_water_in_crack1'))
link(seq_new, '81_NOSHADOW')
report['crack_sequence'] = {'drops_moved_pt': -73, 'calcium_dots': 3, 'water_thread': True}

# 6. CORE 1 picture: a real crack + rust stain on the reinforced frame (infographic F3, illustration A4)
bldg = bvh_of([O['NB_modern_building']])
crack_mat = new_mat('RC.v12_3.crack_dark', '#2E2A22')
rust = new_mat('RC.v12_3.rust_stain', '#8A4A2A')
# column faces probed on screen: front-left column x 714-722, middle column x 744-752 (y 432-516)
c1 = [strip_on(bldg, [(718, 452), (720, 461), (717, 470), (719.5, 480), (718, 489)], 2.6, crack_mat, 'R1_frame_crack_col'),
      strip_on(bldg, [(718, 491), (718.3, 500), (718.6, 510)], 4.0, rust, 'R1_frame_rust'),
      strip_on(bldg, [(748, 468), (750, 477), (747, 486), (749.5, 495)], 2.2, crack_mat, 'R1_frame_crack_col2')]
link(c1, '46_NARRATIVE_ASSETS')

# 7. CORE 5 picture: two lime-clast specimens on a lab bench, healed vs leaking (infographic F3, illustration A4)
r_axis = cam.matrix_world.col[0].xyz; r_axis.z = 0; r_axis.normalize()
f_axis = Vector((-r_axis.y, r_axis.x, 0))
if f_axis.dot((origin - Vector((0, 0, 0))).normalized()) < 0: f_axis = -f_axis
bench_c, _ = hit(GROUND, (1072, 742))
wpp = world_per_pt(bench_c)
spec_mat = new_mat('RC.v12_3.specimen_cylinder', '#A58A78')  # lighter than the cubes so a dark crack reads
bench_mat = bpy.data.materials['RC.v12.labstone']
def box_obj(name, center, size_r, size_f, h, mat, z0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = r_axis * v.co.x * size_r + f_axis * v.co.y * size_f + Vector((0, 0, (v.co.z + 0.5) * h))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    o = O.new(name, me); o.location = Vector((center.x, center.y, z0)); return o
def cyl_obj(name, center, radius, h, mat, z0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=40, radius1=radius, radius2=radius, depth=h)
    for v in bm.verts: v.co.z += h / 2
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    for p in me.polygons: p.use_smooth = True
    o = O.new(name, me); o.location = Vector((center.x, center.y, z0)); return o
bench_h = 9 * wpp
zg = max(height for height in [GROUND.ray_cast(bench_c + r_axis * dx * wpp + Vector((0, 0, 500)), Vector((0, 0, -1)))[0].z for dx in (-70, 0, 70)])
spec = [box_obj('R1_lab_bench', bench_c, 160 * wpp, 46 * wpp, bench_h, bench_mat, zg)]
top_z = zg + bench_h
cA = bench_c - r_axis * 38 * wpp; cB = bench_c + r_axis * 38 * wpp
spec += [cyl_obj('R1_specimen_healed', cA, 17 * wpp, 52 * wpp, spec_mat, top_z),
         cyl_obj('R1_specimen_leaking', cB, 17 * wpp, 52 * wpp, spec_mat, top_z)]
for o in spec: link([o], '47_DIRECTION_ARROWS' if False else '46_NARRATIVE_ASSETS')
bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
sA, sB = to_pt(cA + Vector((0, 0, top_z - cA.z + 26 * wpp))), to_pt(cB + Vector((0, 0, top_z - cB.z + 26 * wpp)))
SA, SB = bvh_of([spec[1]]), bvh_of([spec[2]])
def zig(c, dy=14):
    return [(c[0] - 7, c[1] - dy), (c[0] - 1, c[1] - dy / 2), (c[0] - 4, c[1]), (c[0] + 3, c[1] + dy / 2), (c[0] + 1, c[1] + dy)]
extra = [strip_on(SA, zig(sA), 2.6, calc, 'R1_healed_fill'),
         strip_on(SB, zig(sB), 2.8, crack_mat, 'R1_leak_crack')]
extra += [blob_at(SA, (sA[0] + dx, sA[1] + dy), 1.4, calc, f'R1_healed_clast{i}') for i, (dx, dy) in enumerate([(8, -10), (-9, 6), (6, 12)])]
extra += [blob_at(SB, (sB[0] + dx, sB[1] + dy), 1.4, calc, f'R1_leak_clast{i}') for i, (dx, dy) in enumerate([(9, -9), (-9, 8)])]
extra += [blob_at(SB, (sB[0] + 2, sB[1] + 21 + 6 * i), 1.5 - 0.15 * i, water, f'R1_leak_drop{i}', flat=1.25) for i in range(3)]
pud_c = cB + f_axis * 20 * wpp
bm = bmesh.new(); bmesh.ops.create_circle(bm, cap_ends=True, segments=32, radius=1.0)
for v in bm.verts: v.co = r_axis * v.co.x * 14 * wpp + f_axis * v.co.y * 7 * wpp
me = bpy.data.meshes.new('R1_leak_puddle'); bm.to_mesh(me); bm.free(); me.materials.append(water)
pud = O.new('R1_leak_puddle', me); pud.location = Vector((pud_c.x, pud_c.y, top_z + 0.05 * wpp)); extra.append(pud)
link(extra, '46_NARRATIVE_ASSETS')
report['specimens'] = {'bench_center_pt': [round(float(v), 1) for v in to_pt(bench_c)], 'A_mid_pt': [round(float(v), 1) for v in sA], 'B_mid_pt': [round(float(v), 1) for v in sB]}

# 8. seawater principle model joins the marine cluster in the sea (infographic F5)
d1 = [o for o in bpy.data.collections['50_DETAIL_MODEL'].all_objects if o.name.startswith('D1_')]
pts = np.array([to_pt(o.matrix_world @ v.co) for o in d1 if o.type == 'MESH' for v in list(o.data.vertices)[::5]])
cur = ((pts[:, 0].min() + pts[:, 0].max()) / 2, pts[:, 1].max())
g0, _ = hit(GROUND, cur); g1, _ = hit(SEA, (80, 1657))
delta = g1 - g0
K_D1 = 0.7  # nearer the camera the model reads 1.5x larger; bring it back to its old on-screen size
roots = [o for o in d1 if not (o.parent and o.parent.name.startswith('D1_'))]
assert all(o.parent is None for o in roots)
for o in roots:
    o.location = g1 + (o.location - g0) * K_D1
    o.scale = o.scale * K_D1
bpy.context.view_layer.update()
Wm = O['W_water_marks']
if Wm.data.users > 1: Wm.data = Wm.data.copy()
bm = bmesh.new(); bm.from_mesh(Wm.data); mwm = Wm.matrix_world
pts2 = np.array([to_pt(o.matrix_world @ v.co) for o in d1 if o.type == 'MESH' for v in list(o.data.vertices)[::3]])
bx0, bx1, by0, by1 = pts2[:, 0].min() - 8, pts2[:, 0].max() + 8, pts2[:, 1].min() - 8, pts2[:, 1].max() + 8
gone_w = [f for f in bm.faces if (lambda p: bx0 < p[0] < bx1 and by0 < p[1] < by1)(to_pt(mwm @ f.calc_center_median()))]
bmesh.ops.delete(bm, geom=gone_w, context='FACES'); bm.to_mesh(Wm.data); bm.free()
report['wave_faces_cleared_around_model'] = len(gone_w)
report['seawater_model_box_pt'] = [round(float(v), 1) for v in (bx0 + 8, bx1 - 8, by0 + 8, by1 - 8)]
report['seawater_model'] = {'from_base_pt': [round(float(v), 1) for v in cur], 'to_base_pt': [74, 1652]}

# 9. roads: CORE 1 end leaves the copy, CORE 5 end stops 20pt short with a paved landing (typography T1, layout F1, illustration A1/B1)
road = O['R_core_road']
if road.data.users > 1: road.data = road.data.copy()
bm = bmesh.new(); bm.from_mesh(road.data); mw = road.matrix_world
def fpt(f): return to_pt(mw @ f.calc_center_median())
gone1 = [f for f in bm.faces if (lambda p: p[0] > 512 and p[1] < 506)(fpt(f))]
gone5 = [f for f in bm.faces if (lambda p: p[0] > 948 and p[1] < 880)(fpt(f))]
bmesh.ops.delete(bm, geom=gone1 + gone5, context='FACES')
bm.to_mesh(road.data); bm.free()
bpy.context.view_layer.update()
def road_end(cond):
    P = [mw @ f.center for f in road.data.polygons if cond(to_pt(mw @ f.center))]
    return sum(P, Vector()) / len(P)
mw = road.matrix_world
ends = {'1': road_end(lambda p: p[0] > 505 and 506 <= p[1] < 520), '5': road_end(lambda p: 925 < p[0] <= 948 and 862 < p[1] < 892)}
lands = []
for k, e in ends.items():
    wl = world_per_pt(e)
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=48, radius1=17 * wl, radius2=17 * wl, depth=0.6 * wl)
    me = bpy.data.meshes.new(f'R1_road_landing{k}'); bm.to_mesh(me); bm.free(); me.materials.append(bpy.data.materials['RC.v12.base_road_foundation'])
    # sit on bare terrain just under the road's stone tops (the road stands proud of T_land)
    zt = max(TERRAIN.ray_cast(Vector((e.x + dx * wl * 14, e.y + dy * wl * 14, 500)), Vector((0, 0, -1)))[0].z for dx in (-1, 0, 1) for dy in (-1, 0, 1))
    land = O.new(f'R1_road_landing{k}', me); land.location = Vector((e.x, e.y, zt + 0.15 * wl)); lands.append(land)
link(lands, '35_FIELDS_ROADS')
report['road_landings_pt'] = {k: [round(float(v), 1) for v in to_pt(e)] for k, e in ends.items()}
report['road_trim_faces'] = {'core1': len(gone1), 'core5': len(gone5)}

# 10. field plate under CORE 5 copy (layout F1, illustration B1) -> removed
F = O['F_centuriatio']
if F.data.users > 1: F.data = F.data.copy()
bm = bmesh.new(); bm.from_mesh(F.data); mw = F.matrix_world
gone = [f for f in bm.faces if (lambda p: 955 < p[0] < 1060 and 895 < p[1] < 955)(to_pt(mw @ f.calc_center_median()))]
bmesh.ops.delete(bm, geom=gone, context='FACES')
bm.to_mesh(F.data); bm.free()
report['field_plate_faces_removed'] = len(gone)

# 11. heat cue on the making model reads at poster size (illustration A4)
for n in ('D2_heat0', 'D2_heat1', 'D2_heat2'):
    o = O[n]; o.scale *= 1.6

# 12. CORE badges + underlines follow the unified Figma module
#     module origin (X,Y) = Figma group top-left; badge centre (X+10.5, Y+13.3) d21; underline Y+50.6..51.8 over title-2 width
CORE = {1: (528, 382, 110), 2: (61.5, 744, 75), 3: (408.5, 1028, 131), 4: (638.5, 1028, 110), 5: (982.5, 816, 127)}
def plane_of(o):
    P = [o.matrix_world @ v.co for v in o.data.vertices]
    cen = sum(P, Vector()) / len(P)
    n = (P[1] - P[0]).cross(P[2] - P[0]).normalized()
    return cen, n
def on_plane(pt, cen, n):
    o_, d_ = ray(pt); t = (cen - o_).dot(n) / d_.dot(n); return o_ + d_ * t
def rebuild(o, pts2d, fan=False):
    cen, n = plane_of(o)
    W = [on_plane(p, cen, n) for p in pts2d]
    inv = o.matrix_world.inverted()
    bm = bmesh.new(); vs = [bm.verts.new(inv @ w) for w in W]
    bm.faces.new(vs); bm.to_mesh(o.data); bm.free()
for k, (X, Y, w2) in CORE.items():
    b = O[f'S_core{k}_badge']; u = O[f'S_core{k}_underline']
    for ob in (b, u):
        if ob.data.users > 1: ob.data = ob.data.copy()
    cx, cy = X + 10.5, Y + 13.3
    rebuild(b, [(cx + 10.5 * math.cos(a), cy + 10.5 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 49)[:-1]])
    rebuild(u, [(X, Y + 50.6), (X + w2, Y + 50.6), (X + w2, Y + 51.8), (X, Y + 51.8)])
report['core_overlays'] = CORE

print('REPORT ' + json.dumps(report, ensure_ascii=False))
H = runpy.run_path(str(ROOT / 'scripts/integrate_assets.py'), run_name='helpers')
if MODE == 'test':
    res = H['render_two_pass'](Path(argv[1]).with_suffix('.png'))
    print('RENDER ' + json.dumps(res))
elif MODE == 'final':
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT), copy=False)
    res = H['render_two_pass'](ROOT / 'renders/narrative_v8_3_r1.png')
    report['render'] = res
    (ROOT / 'out/v8_3-review-r1-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print('RENDER ' + json.dumps(res))
