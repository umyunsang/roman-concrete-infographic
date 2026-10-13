"""v8.4 = v8.3 + remaining round-1 3D cleanups (illustration A2): Colosseum ground skirt/outline, road hole, mountain tail.

Run: blender -b out/roman_concrete_narrative_v8_3.blend --factory-startup --python scripts/review_r1_addendum_v8_4.py -- <test|final> [test_prefix]
"""
import bpy, bmesh, math, json, sys, runpy
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'out/roman_concrete_narrative_v8_3.blend'
OUT = ROOT / 'out/roman_concrete_narrative_v8_4.blend'
argv = sys.argv[sys.argv.index('--') + 1:]
MODE = argv[0]
assert Path(bpy.data.filepath).resolve() == SRC.resolve()
sc = bpy.context.scene; cam = sc.camera; O = bpy.data.objects
report = {}

def to_pt(p):
    v = world_to_camera_view(sc, cam, p); return np.array((v.x * 1191, (1 - v.y) * 1684))
def lin(h):
    return tuple(((int(h[i:i + 2], 16) / 255 + 0.055) / 1.055) ** 2.4 for i in (1, 3, 5))
def new_mat(name, hexv, like='RC.v12.roman_stone'):
    m = bpy.data.materials.get(name) or bpy.data.materials[like].copy(); m.name = name
    c = (*lin(hexv), 1); m.diffuse_color = c
    if m.node_tree:
        b = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if b: b.inputs['Base Color'].default_value = c
    return m
dg = bpy.context.evaluated_depsgraph_get()
def bvh_of(objs):
    verts, polys = [], []
    for o in objs:
        ev = o.evaluated_get(dg); me = ev.to_mesh(); mw = o.matrix_world; b = len(verts)
        verts += [mw @ v.co for v in me.vertices]; polys += [[b + i for i in p.vertices] for p in me.polygons]
        ev.to_mesh_clear()
    return BVHTree.FromPolygons(verts, polys)
TERRAIN = bvh_of([O['T_land']])
frame = [cam.matrix_world @ v for v in cam.data.view_frame(scene=sc)]
origin = cam.matrix_world.translation
def ray(pt):
    u, v = pt[0] / 1191, 1 - pt[1] / 1684
    tr, br, bl, tl = frame
    return origin, ((bl + (br - bl) * u + (tl - bl) * v) - origin).normalized()

# 1. Colosseum: travertine piazza ring hides the scan's ground skirt (stains) and the thin footprint outline
col = O['COL_ruined']; mw = col.matrix_world
co = np.array([mw @ v.co for v in col.data.vertices])
wall = co[co[:, 2] > 2.0]
c = wall[:, :2].mean(0)
ev, evec = np.linalg.eigh(np.cov((wall[:, :2] - c).T))
ax = evec[:, ::-1]  # major first
uv = (wall[:, :2] - c) @ ax
A, B = np.percentile(np.abs(uv[:, 0]), 99.5), np.percentile(np.abs(uv[:, 1]), 99.5)
allv = (co[:, :2] - c) @ ax
rn = np.hypot(allv[:, 0] / A, allv[:, 1] / B)
skirt = (rn > 1.0) & (rn < 1.13) & (co[:, 2] < 2.0)
# measured: outside skirt sits 0.04-0.07 above terrain (p90 0.3-0.7) and never beyond 1.11 x the wall ellipse
R_IN, R_OUT, LIFT = 1.0, 1.12, 0.42
def tz(x, y):
    h = TERRAIN.ray_cast(Vector((x, y, 500)), Vector((0, 0, -1)))[0]; return h.z if h else 0.0
bm = bmesh.new(); N = 180; ring_in, ring_out, ring_low = [], [], []
for k in range(N):
    t = 2 * math.pi * k / N
    for r, lst in ((R_IN, ring_in), (R_OUT, ring_out)):
        p2 = c + ax[:, 0] * A * r * math.cos(t) + ax[:, 1] * B * r * math.sin(t)
        lst.append(bm.verts.new((p2[0], p2[1], tz(p2[0], p2[1]) + LIFT)))
    v = ring_out[-1]; ring_low.append(bm.verts.new((v.co.x, v.co.y, tz(v.co.x, v.co.y) - 0.05)))
for k in range(N):
    j = (k + 1) % N
    bm.faces.new((ring_in[k], ring_in[j], ring_out[j], ring_out[k]))
    bm.faces.new((ring_out[k], ring_out[j], ring_low[j], ring_low[k]))
z_top = LIFT
me = bpy.data.meshes.new('R1_colosseum_piazza'); bm.to_mesh(me); bm.free()
me.materials.append(new_mat('RC.v12_4.piazza_travertine', '#D2C2A2'))
pz = O.new('R1_colosseum_piazza', me)
bpy.data.collections['20_LANDMARK'].objects.link(pz)
report['piazza'] = {'A': round(float(A), 2), 'B': round(float(B), 2), 'z_top': round(z_top, 3), 'skirt_verts': int(skirt.sum())}

# 2. CORE 5 road hole (≈925-950, 885-915 pt): paved base strip under the stones
road = O['R_core_road']; rmw = road.matrix_world
def tz(pt):
    o_, d_ = ray(pt); h = TERRAIN.ray_cast(o_, d_)[0]; return h
pts = [(905, 933), (920, 914), (934, 897), (945, 885)]
H = [tz(p) for p in pts]
bm = bmesh.new(); L, Rr = [], []
for k, h in enumerate(H):
    a = H[max(k - 1, 0)]; b = H[min(k + 1, len(H) - 1)]
    t = (b - a); t.z = 0; t.normalize(); s = Vector((-t.y, t.x, 0))
    wpp = 1.0 / np.linalg.norm(to_pt(h + cam.matrix_world.col[0].xyz.normalized()) - to_pt(h))
    w = 16 * wpp
    L.append(bm.verts.new(h + s * w + Vector((0, 0, 0.05)))); Rr.append(bm.verts.new(h - s * w + Vector((0, 0, 0.05))))
for k in range(len(H) - 1):
    bm.faces.new((L[k], L[k + 1], Rr[k + 1], Rr[k]))
me = bpy.data.meshes.new('R1_road5_bed'); bm.to_mesh(me); bm.free()
me.materials.append(bpy.data.materials['RC.v12.base_road_foundation'])
bed = O.new('R1_road5_bed', me); bpy.data.collections['35_FIELDS_ROADS'].objects.link(bed)

# 3. mountain tail (≈25-42, 288-306 pt) on L01_terminillo
m = O['L01_terminillo']
if m.data.users > 1: m.data = m.data.copy()
bm = bmesh.new(); bm.from_mesh(m.data); mmw = m.matrix_world
gone = [v for v in bm.verts if (lambda p: p[0] < 41 and p[1] > 293)(to_pt(mmw @ v.co))]
bmesh.ops.delete(bm, geom=gone, context='VERTS')
bm.to_mesh(m.data); bm.free()
report['mountain_tail_verts'] = len(gone)

print('REPORT ' + json.dumps(report, ensure_ascii=False))
Hh = runpy.run_path(str(ROOT / 'scripts/integrate_assets.py'), run_name='helpers')
if MODE == 'test':
    print('RENDER ' + json.dumps(Hh['render_two_pass'](Path(argv[1]).with_suffix('.png'))))
else:
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT), copy=False)
    res = Hh['render_two_pass'](ROOT / 'renders/narrative_v8_4_r1.png'); report['render'] = res
    (ROOT / 'out/v8_4-review-r1-addendum.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print('RENDER ' + json.dumps(res))
