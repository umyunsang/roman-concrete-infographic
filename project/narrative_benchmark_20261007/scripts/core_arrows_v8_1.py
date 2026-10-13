"""v8.1: unify CORE badge/underline colour to CORE 2, hide timeline, add Meshy direction arrows.

Run: blender -b out/roman_concrete_narrative_v8.blend --factory-startup --python scripts/core_arrows_v8_1.py -- <arrow.glb> <test|final>
Never overwrites v8; saves out/roman_concrete_narrative_v8_1.blend in final mode.
"""
import bpy, bmesh, math, json, sys, runpy
from pathlib import Path
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'out/roman_concrete_narrative_v8.blend'
OUT = ROOT / 'out/roman_concrete_narrative_v8_1.blend'
argv = sys.argv[sys.argv.index('--') + 1:]
ARROW_GLB, MODE = Path(argv[0]), argv[1]
assert Path(bpy.data.filepath).resolve() == SRC.resolve()
W_PT, H_PT = 1191, 1684
sc = bpy.context.scene
cam = sc.camera
report = {}

# 1. CORE 1~5 badge + underline -> CORE 2 material/colour
mat2 = bpy.data.materials['RC.v12.base_badge_2']
ref = bpy.data.objects['S_core2_badge']
for i in (1, 3, 4, 5):
    for part in ('badge', 'underline'):
        o = bpy.data.objects[f'S_core{i}_{part}']
        if o.data.users > 1:
            o.data = o.data.copy()
        for slot in o.material_slots:
            slot.material = mat2
        o.color = ref.color
report['core_recoloured'] = [f'S_core{i}_{p}' for i in (1, 3, 4, 5) for p in ('badge', 'underline')]

# 2. timeline shapes off (Figma timeline texts are removed separately)
tl = [o for o in bpy.data.objects if o.name.startswith('S_time_')]
for o in tl:
    o.hide_render = True
    o.hide_viewport = True
report['timeline_hidden'] = sorted(o.name for o in tl)

# 3. ground BVH (terrain + roads/fields), camera rays from poster pt
dg = bpy.context.evaluated_depsgraph_get()
def world_mesh(objs):
    verts, polys = [], []
    for o in objs:
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        mw = o.matrix_world
        base = len(verts)
        verts += [mw @ v.co for v in me.vertices]
        polys += [[base + i for i in p.vertices] for p in me.polygons]
        ev.to_mesh_clear()
    return BVHTree.FromPolygons(verts, polys)
ground_objs = [bpy.data.objects['T_land']] + [o for o in bpy.data.collections['35_FIELDS_ROADS'].objects if o.type == 'MESH' and not o.hide_render]
GROUND = world_mesh(ground_objs)
TERRAIN = world_mesh([bpy.data.objects['T_land']])

frame = [cam.matrix_world @ v for v in cam.data.view_frame(scene=sc)]  # tr, br, bl, tl
origin = cam.matrix_world.translation
def ray(pt):
    u, v = pt[0] / W_PT, 1 - pt[1] / H_PT
    tr, br, bl, tl_ = frame
    p = bl + (br - bl) * u + (tl_ - bl) * v
    return origin, (p - origin).normalized()
def ground_at(pt, bvh=GROUND):
    o, d = ray(pt)
    hit, n, i, dist = bvh.ray_cast(o, d)
    assert hit is not None, pt
    return hit
def to_pt(p):
    v = world_to_camera_view(sc, cam, p)
    return (v.x * W_PT, (1 - v.y) * H_PT)
def height_at(x, y, bvh=GROUND):
    hit = bvh.ray_cast(Vector((x, y, 500)), Vector((0, 0, -1)))[0]
    return hit.z if hit else None

# 4. arrow mesh from Meshy GLB: lay flat, cut the spear tail square, unit length, head = +X
before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(ARROW_GLB))
imported = [o for o in bpy.data.objects if o not in before]
src = next(o for o in imported if o.type == 'MESH')
me = src.data.copy()
me.transform(src.matrix_world)
me.transform(Matrix.Rotation(math.radians(90), 4, 'X'))  # width z->y, thickness y->z
for o in imported:
    bpy.data.objects.remove(o, do_unlink=True)
bm = bmesh.new(); bm.from_mesh(me)
xs = [v.co.x for v in bm.verts]
CUT = -0.50  # spear taper ends at x≈-0.55; shaft is constant 0.44 wide from there
geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
res = bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(CUT, 0, 0), plane_no=(1, 0, 0), clear_inner=True)
cut_edges = [e for e in res['geom_cut'] if isinstance(e, bmesh.types.BMEdge)]
bmesh.ops.holes_fill(bm, edges=cut_edges, sides=0)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
xs = [v.co.x for v in bm.verts]; ys = [v.co.y for v in bm.verts]; zs = [v.co.z for v in bm.verts]
x0, x1 = min(xs), max(xs)
L0 = x1 - x0
THICK = float(argv[2]) if len(argv) > 2 else 2.2  # chunkier slab reads as an object at poster scale
for v in bm.verts:
    v.co.x = (v.co.x - x0) / L0          # tail 0 -> tip 1
    v.co.y = v.co.y / L0
    v.co.z = (v.co.z - min(zs)) / L0 * THICK
# Meshy's head is only 1.7x the shaft and flat-sided, so it reads as a sign post.
# Re-proportion the same mesh (y only, bevels kept) into a classic arrow:
# narrow shaft, barbed head base at HEAD_U, straight taper to the tip.
HEAD_U, SHAFT_HW, HEAD_HW = 0.50, 0.095, 0.27
bins = np.linspace(0, 1, 61)
us = np.array([v.co.x for v in bm.verts]); ys_ = np.array([abs(v.co.y) for v in bm.verts])
idx = np.clip(np.digitize(us, bins) - 1, 0, 59)
w = np.array([ys_[idx == i].max() if (idx == i).any() else 0 for i in range(60)])
for i in range(60):
    if w[i] == 0: w[i] = w[i - 1]
def target(u):
    return SHAFT_HW if u < HEAD_U else max(HEAD_HW * (1 - u) / (1 - HEAD_U), 0.004)
for v, i in zip(bm.verts, idx):
    v.co.y *= target(v.co.x) / max(w[i], 0.02)
ys = [v.co.y for v in bm.verts]
bm.to_mesh(me); bm.free()
me.name = 'ARROW_dir_mesh'
for p in me.polygons:
    p.use_smooth = False
arrow_mat = bpy.data.materials.get('RC.v12_1.direction_arrow') or mat2.copy()
arrow_mat.name = 'RC.v12_1.direction_arrow'
# CORE 2 title colour #983821 (sRGB) -> linear; lit top faces land near the badge tone
lin = tuple(((c / 255 + 0.055) / 1.055) ** 2.4 for c in (0x98, 0x38, 0x21))
arrow_mat.diffuse_color = (*lin, 1)
if arrow_mat.node_tree:
    bsdf = next((n for n in arrow_mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf: bsdf.inputs['Base Color'].default_value = (*lin, 1)
me.materials.clear(); me.materials.append(arrow_mat)
width_ratio = max(ys) - min(ys)
report['arrow_mesh'] = {'tris': sum(len(p.vertices) - 2 for p in me.polygons), 'width_ratio': round(width_ratio, 3), 'thick_ratio': round((max(zs) - min(zs)) / L0 * THICK, 3)}

col = bpy.data.collections.get('47_DIRECTION_ARROWS') or bpy.data.collections.new('47_DIRECTION_ARROWS')
if col.name not in sc.collection.children:
    sc.collection.children.link(col)
for o in list(col.objects):
    bpy.data.objects.remove(o, do_unlink=True)

# user marks (poster pt, tail -> head) from KakaoTalk_Photo_2026-10-12-13-13-44 red strokes
MARKS = {'A1_core1_to_2': ((503, 409), (457, 445)),
         'A2_core2_to_34': ((191, 960), (250, 1008)),
         'A3_core34_to_5': ((790, 1011), (860, 972))}
SCREEN_LEN = json.loads(argv[3]) if len(argv) > 3 else {}
placed = {}
for name, (tail, head) in MARKS.items():
    mid_pt = ((tail[0] + head[0]) / 2, (tail[1] + head[1]) / 2)
    gt, gh = ground_at(tail), ground_at(head)
    d = gh - gt; d.z = 0
    yaw = math.atan2(d.y, d.x)
    gm = ground_at(mid_pt)
    # world length so the projected tail->tip matches the target screen length
    target = SCREEN_LEN.get(name, math.dist(tail, head))
    dirv = Vector((math.cos(yaw), math.sin(yaw), 0))
    def screen_len(L):
        a, b = gm - dirv * L / 2, gm + dirv * L / 2
        return math.dist(to_pt(a), to_pt(b))
    L = d.length
    for _ in range(20):
        L *= target / screen_len(L)
    o = bpy.data.objects.new(name, me)
    col.objects.link(o)
    o.color = (*lin, 1)
    o.rotation_euler = (0, 0, yaw)
    o.scale = (L, L, L)
    start = gm - dirv * L / 2
    # rest on the highest ground sample under the footprint
    hs = []
    for s in np.linspace(0, 1, 9):
        for w in (-0.5, 0, 0.5):
            p = start + dirv * L * s + Vector((-dirv.y, dirv.x, 0)) * L * width_ratio * w
            h = height_at(p.x, p.y)
            if h is not None: hs.append(h)
    lift = L * 0.02
    o.location = (start.x, start.y, max(hs) + lift)
    bpy.context.view_layer.update()
    tip = o.matrix_world @ Vector((1, 0, 0)); tailw = o.matrix_world @ Vector((0, 0, 0))
    placed[name] = {'tail_pt': [round(c, 1) for c in to_pt(tailw)], 'tip_pt': [round(c, 1) for c in to_pt(tip)],
                    'world_len': round(L, 3), 'yaw_deg': round(math.degrees(yaw), 2), 'z': round(o.location.z, 3),
                    'ground_range': [round(min(hs), 3), round(max(hs), 3)]}
report['arrows'] = placed

# screen bbox of each arrow (all verts) for overlap checks
def screen_box(o):
    pts = [to_pt(o.matrix_world @ v.co) for v in list(o.data.vertices)[::7]]
    xs, ys = zip(*pts)
    return [round(min(xs), 1), round(max(xs), 1), round(min(ys), 1), round(max(ys), 1)]
report['arrow_screen_boxes'] = {o.name: screen_box(o) for o in col.objects}

# 5. the small hay-bale field patch under arrow A2's head moves down the same river bank
F = bpy.data.objects['F_centuriatio']
if F.data.users > 1:
    F.data = F.data.copy()
bm = bmesh.new(); bm.from_mesh(F.data); bm.verts.ensure_lookup_table()
mw = F.matrix_world
seen, islands = set(), []
for v in bm.verts:
    if v.index in seen: continue
    seen.add(v.index); stack, comp = [v], []
    while stack:
        a = stack.pop(); comp.append(a)
        for e in a.link_edges:
            b = e.other_vert(a)
            if b.index not in seen:
                seen.add(b.index); stack.append(b)
    islands.append(comp)
ZONE = (215, 292, 955, 1022)  # whole bale patch incl. its loose plate pieces
moving = []
for comp in islands:
    pts = [to_pt(mw @ v.co) for v in comp]
    xs_, ys2 = zip(*pts)
    if min(xs_) >= ZONE[0] and max(xs_) <= ZONE[1] and min(ys2) >= ZONE[2] and max(ys2) <= ZONE[3]:
        moving.append(comp)
assert moving, 'bale patch not found'
allp = [to_pt(mw @ v.co) for comp in moving for v in comp]
bx = (min(p[0] for p in allp), max(p[0] for p in allp), min(p[1] for p in allp), max(p[1] for p in allp))
cx, cy = (bx[0] + bx[1]) / 2, (bx[2] + bx[3]) / 2
# free sand below the ribbed patch, between DETAIL 2 copy (x<=162) and the river (x>=245)
FREE = (178, 240, 1076, 1112)
TARGET = ((FREE[0] + FREE[1]) / 2, (FREE[2] + FREE[3]) / 2)
k = min(1.0, (FREE[1] - FREE[0]) / (bx[1] - bx[0]), (FREE[3] - FREE[2]) / (bx[3] - bx[2]))
g0, g1 = ground_at((cx, cy), TERRAIN), ground_at(TARGET, TERRAIN)
inv = mw.inverted()
for comp in moving:
    for v in comp:
        pw = mw @ v.co
        v.co = inv @ (g1 + (pw - g0) * k)
delta = g1 - g0
moved_idx = [v.index for comp in moving for v in comp]
n_islands, n_verts = len(moving), len(moved_idx)
bm.to_mesh(F.data); bm.free(); F.data.update()
allp2 = [to_pt(mw @ F.data.vertices[i].co) for i in moved_idx]
report['moved_field_patch'] = {'islands': n_islands, 'verts': n_verts,
    'from_box': [round(min(p[0] for p in allp)), round(max(p[0] for p in allp)), round(min(p[1] for p in allp)), round(max(p[1] for p in allp))],
    'to_box': [round(min(p[0] for p in allp2)), round(max(p[0] for p in allp2)), round(min(p[1] for p in allp2)), round(max(p[1] for p in allp2))],
    'world_delta': [round(c, 3) for c in delta], 'scale': round(k, 3)}
print('REPORT ' + json.dumps(report, ensure_ascii=False))

EXTRA = ROOT / 'scripts/core_arrows_v8_1_extra.py'
if EXTRA.exists():
    runpy.run_path(str(EXTRA), init_globals={'report': report, 'to_pt': to_pt, 'ground_at': ground_at, 'height_at': height_at, 'col': col})

if MODE == 'test':
    r = sc.render
    r.resolution_percentage = 48
    r.film_transparent = False
    H = runpy.run_path(str(ROOT / 'scripts/integrate_assets.py'), run_name='helpers')
    out = Path(argv[4] if len(argv) > 4 else '/tmp/arrow_test')
    res = H['render_two_pass'](out.with_suffix('.png'))
    print('RENDER ' + json.dumps(res))
elif MODE == 'final':
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT), copy=False)
    H = runpy.run_path(str(ROOT / 'scripts/integrate_assets.py'), run_name='helpers')
    res = H['render_two_pass'](ROOT / 'renders/narrative_v8_1_core_arrows.png')
    report['render'] = res
    (ROOT / 'out/v8_1-core-arrows-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print('RENDER ' + json.dumps(res))
