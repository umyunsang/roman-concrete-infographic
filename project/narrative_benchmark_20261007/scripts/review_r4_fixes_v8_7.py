"""v8.7: apply verified round-4 critic findings to the Blender map.

Run: blender -b out/roman_concrete_narrative_v8_6.blend --factory-startup --python scripts/review_r4_fixes_v8_7.py -- <test|final> [test_prefix]
"""
import bpy, bmesh, math, json, sys, runpy
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'out/roman_concrete_narrative_v8_6.blend'
OUT = ROOT / 'out/roman_concrete_narrative_v8_7.blend'
argv = sys.argv[sys.argv.index('--') + 1:]
MODE = argv[0]
assert Path(bpy.data.filepath).resolve() == SRC.resolve()
sc = bpy.context.scene; cam = sc.camera; O = bpy.data.objects
report = {}

def to_pt(p):
    v = world_to_camera_view(sc, cam, p); return np.array((v.x * 1191, (1 - v.y) * 1684))
frame = [cam.matrix_world @ v for v in cam.data.view_frame(scene=sc)]
origin = cam.matrix_world.translation
def ray(pt):
    u, v = pt[0] / 1191, 1 - pt[1] / 1684
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
def ground_pt(pt):
    h = TERRAIN.ray_cast(*ray(pt))[0]; assert h is not None, pt; return h

# 1. arena: terrain pokes into the hypogeum as paper-coloured patches -> an arena-earth skin on the terrain inside the bowl
col = O['COL_ruined']; cmw = col.matrix_world
co = np.array([cmw @ v.co for v in col.data.vertices])
wall = co[co[:, 2] > 2.0]; c = wall[:, :2].mean(0)
ev, evec = np.linalg.eigh(np.cov((wall[:, :2] - c).T)); ax = evec[:, ::-1]
uv = (wall[:, :2] - c) @ ax
A, B = np.percentile(np.abs(uv[:, 0]), 99.5), np.percentile(np.abs(uv[:, 1]), 99.5)
bm = bmesh.new(); NR, NT = 14, 120
grid = []
for i in range(NR + 1):
    r = 0.66 * i / NR; row = []
    for k in range(NT):
        t = 2 * math.pi * k / NT
        p2 = c + ax[:, 0] * A * r * math.cos(t) + ax[:, 1] * B * r * math.sin(t)
        row.append(bm.verts.new((p2[0], p2[1], tz(p2[0], p2[1]) + 0.03)))
    grid.append(row)
for i in range(NR):
    for k in range(NT):
        j = (k + 1) % NT
        if i == 0: bm.faces.new((grid[0][k], grid[1][k], grid[1][j])) if False else None
        bm.faces.new((grid[i][k], grid[i][j], grid[i + 1][j], grid[i + 1][k]))
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
me = bpy.data.meshes.new('R4_arena_skin'); bm.to_mesh(me); bm.free()
me.materials.append(bpy.data.materials['RC.v12.arena_earth'])
skin = O.new('R4_arena_skin', me); bpy.data.collections['20_LANDMARK'].objects.link(skin)

# 2. Colosseum: drop loose islands (< 400 faces) left on the podium
if col.data.users > 1: col.data = col.data.copy()
bm = bmesh.new(); bm.from_mesh(col.data); bm.faces.ensure_lookup_table()
seen = set(); small = []
for f in bm.faces:
    if f.index in seen: continue
    st = [f]; seen.add(f.index); comp = []
    while st:
        a = st.pop(); comp.append(a)
        for e in a.edges:
            for g in e.link_faces:
                if g.index not in seen: seen.add(g.index); st.append(g)
    if len(comp) < 400: small += comp
bmesh.ops.delete(bm, geom=small, context='FACES')
bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
bm.to_mesh(col.data); bm.free()
report['colosseum_loose_faces_removed'] = len(small)

# 3. podium tucks further under the collapsed SE wall (inner edge = smoothed wall line - 0.08 instead of - 0.03)
pod = O['R3_colosseum_podium']
bm = bmesh.new(); bm.from_mesh(pod.data); pmw = pod.matrix_world
N = 240
inner = [v for v in bm.verts if v.index % 3 == 0]  # build order: ri, ro, rl per angle
for v in inner:
    w = pmw @ v.co; q = (np.array((w.x, w.y)) - c) @ ax
    rn = math.hypot(q[0] / A, q[1] / B); t = math.atan2(q[1] / B, q[0] / A)
    r2 = max(0.66, rn - 0.05)
    p2 = c + ax[:, 0] * A * r2 * math.cos(t) + ax[:, 1] * B * r2 * math.sin(t)
    v.co = pmw.inverted() @ Vector((p2[0], p2[1], w.z))
bm.to_mesh(pod.data); bm.free()

# 4. road ends: plank/curb remnants beyond the D7 landings go; lower-bridge west junction gets a paved bed
road = O['R_core_road']
if road.data.users > 1: road.data = road.data.copy()
bm = bmesh.new(); bm.from_mesh(road.data); rmw = road.matrix_world
BOX = [(928, 952, 845, 866), (950, 960, 884, 895), (546, 566, 498, 515), (530, 546, 520, 536), (256, 266, 962, 970)]
gone = [f for f in bm.faces if any(x0 < p[0] < x1 and y0 < p[1] < y1 for (x0, x1, y0, y1) in BOX for p in [to_pt(rmw @ f.calc_center_median())])]
bmesh.ops.delete(bm, geom=gone, context='FACES')
bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
bm.to_mesh(road.data); bm.free()
report['road_remnant_faces'] = len(gone)
pts = [ground_pt(p) for p in [(246, 951), (272, 951), (276, 971), (250, 972)]]
bm = bmesh.new(); vs = [bm.verts.new((p.x, p.y, tz(p.x, p.y) + 0.05)) for p in pts]; bm.faces.new(vs)
me = bpy.data.meshes.new('R4_bridge_west_bed'); bm.to_mesh(me); bm.free()
me.materials.append(bpy.data.materials['RC.v12.base_road_foundation'])
bed = O.new('R4_bridge_west_bed', me); bpy.data.collections['35_FIELDS_ROADS'].objects.link(bed)

# 5. lime kiln 5pt further up-screen so CORE 2 keeps its outer margin (layout LY07-A)
kiln = O['D2_lime_kiln']
P = np.array([to_pt(kiln.matrix_world @ v.co) for v in kiln.data.vertices])
base_pt = ((P[:, 0].min() + P[:, 0].max()) / 2, P[:, 1].max())
g0, g1 = ground_pt(base_pt), ground_pt((base_pt[0], base_pt[1] - 5))
d = g1 - g0; d.z = tz(g1.x, g1.y) - tz(g0.x, g0.y)
kiln.location += d
bpy.context.view_layer.update()
P2 = np.array([to_pt(kiln.matrix_world @ v.co) for v in kiln.data.vertices])
report['kiln_bottom_pt'] = [round(float(base_pt[1]), 1), round(float(P2[:, 1].max()), 1)]

print('REPORT ' + json.dumps(report, ensure_ascii=False))
H = runpy.run_path(str(ROOT / 'scripts/integrate_assets.py'), run_name='helpers')
if MODE == 'test':
    print('RENDER ' + json.dumps(H['render_two_pass'](Path(argv[1]).with_suffix('.png'))))
else:
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT), copy=False)
    r = H['render_two_pass'](ROOT / 'renders/narrative_v8_7_r4.png'); report['render'] = r
    (ROOT / 'out/v8_7-review-r4-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print('RENDER ' + json.dumps(r))
