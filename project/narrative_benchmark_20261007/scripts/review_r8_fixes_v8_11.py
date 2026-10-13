"""v8.11: round-8 3D findings (true Pantheon form, visible step-1/2 cracks) + value field round-1 findings.

Run: blender -b out/roman_concrete_narrative_v8_10.blend --factory-startup --python scripts/review_r8_fixes_v8_11.py -- <test|final> [test_prefix]
Never overwrites v8_10; final saves out/roman_concrete_narrative_v8_11.blend.
"""
import bpy, bmesh, math, json, sys, runpy
from pathlib import Path
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'out/roman_concrete_narrative_v8_10.blend'
OUT = ROOT / 'out/roman_concrete_narrative_v8_11.blend'
GLB = ROOT / 'models/pantheon_v1/pantheon_meshy71.glb'
argv = sys.argv[sys.argv.index('--') + 1:]
MODE = argv[0]
assert Path(bpy.data.filepath).resolve() == SRC.resolve()
W_PT, H_PT = 1191, 1684
sc = bpy.context.scene; cam = sc.camera; O = bpy.data.objects
report = {}

def lin(h):
    return tuple(((int(h[i:i + 2], 16) / 255 + 0.055) / 1.055) ** 2.4 for i in (1, 3, 5))
def hexof(c):
    return '#%02X%02X%02X' % tuple(round(255 * (x * 12.92 if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055)) for x in c[:3])
def scaled_mat(src, name, k):
    """copy of material src with linear diffuse reflectance x k (value-field fixes keep hue)."""
    m = bpy.data.materials.get(name) or bpy.data.materials[src].copy(); m.name = name
    c = bpy.data.materials[src].diffuse_color
    m.diffuse_color = (*(min(1.0, x * k) for x in c[:3]), 1)
    return m
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
def world_per_pt(p):
    r = cam.matrix_world.col[0].xyz.normalized()
    return 1.0 / np.linalg.norm(to_pt(p + r) - to_pt(p))
def strip_on(bvh, pts, width_pt, mat, name, lift=0.02):
    hits = [hit(bvh, p) for p in pts]
    assert all(h[0] is not None for h in hits), (name, pts, [h[0] is None for h in hits])
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
    o = O.new(name, me); return o, [tuple(round(float(x), 3) for x in n) for h, n in hits]
def link(objs, colname):
    col = bpy.data.collections[colname]
    for o in objs:
        for c in list(o.users_collection): c.objects.unlink(o)
        col.objects.link(o)
TERRAIN = bvh_of([O['T_land']])
def tz(x, y):
    h = TERRAIN.ray_cast(Vector((x, y, 500)), Vector((0, 0, -1)))[0]; return h.z if h else 0.0

# 1. Pantheon (3D NEW-01): rotunda + stepped dome + portico from Meshy 7.1 replaces the peripteral temple
old = O['L03_forum_temple']
ow = np.array([old.matrix_world @ v.co for v in old.data.vertices])
op = np.array([to_pt(Vector(p)) for p in ow])
report['pantheon_old_screen'] = [round(float(v), 1) for v in (op[:, 0].min(), op[:, 0].max(), op[:, 1].min(), op[:, 1].max())]
cx, cy = (ow[:, 0].min() + ow[:, 0].max()) / 2, (ow[:, 1].min() + ow[:, 1].max()) / 2
old.hide_render = True; old.hide_viewport = True
before = set(O)
bpy.ops.import_scene.gltf(filepath=str(GLB))
new = [o for o in O if o not in before and o.type == 'MESH']
assert len(new) == 1, [o.name for o in new]
pan = new[0]; pan.name = 'R8_pantheon'; pan.data.name = 'R8_pantheon'
for o in [o for o in O if o not in before and o is not pan]: O.remove(o, do_unlink=True)
pan.parent = None; pan.matrix_world = Matrix.Identity(4)
dec = pan.modifiers.new('dec', 'DECIMATE'); dec.ratio = 0.07
dg = bpy.context.evaluated_depsgraph_get()
me2 = bpy.data.meshes.new_from_object(pan.evaluated_get(dg)); pan.modifiers.clear()
old_me = pan.data; pan.data = me2; me2.name = 'R8_pantheon'; bpy.data.meshes.remove(old_me)
me = pan.data; me.materials.clear()
for n in ('RC.v12.roman_stone', 'RC.v12.roman_roof', 'RC.v12.roman_plinth'): me.materials.append(bpy.data.materials[n])
co = np.array([v.co[:] for v in me.vertices]); R = co[:, 0].max(); yc = co[:, 1].max() - R
zmin, zmax = co[:, 2].min(), co[:, 2].max()
idx = []
for p in me.polygons:
    c = p.center; n = p.normal
    r = math.hypot(c.x, c.y - yc)
    if c.z > 0.262 and r < R * 0.99 and c.y > yc - R:
        idx.append(1)                                   # stepped dome + rings above the drum cornice
    elif c.y < -0.48 and c.z > 0.02 and n.z > 0.3:
        idx.append(1)                                   # portico roof slopes
    elif c.z < zmin + 0.06:
        idx.append(2)                                   # base course / portico steps
    else:
        idx.append(0)
me.polygons.foreach_set('material_index', idx)
me.shade_smooth(); me.set_sharp_from_angle(angle=math.radians(32))
report['pantheon_faces'] = len(me.polygons); report['pantheon_roof_faces'] = idx.count(1)

def place(yaw_deg, diam_pt, base_xy):
    gz = tz(*base_xy); base = Vector((base_xy[0], base_xy[1], gz))
    s = diam_pt * world_per_pt(base) / (2 * R)
    pan.matrix_world = Matrix.Translation((base.x, base.y, gz - zmin * s)) @ Matrix.Rotation(math.radians(yaw_deg), 4, 'Z') @ Matrix.Scale(s, 4)
    bpy.context.view_layer.update()
    return s
def screen_box():
    mw = pan.matrix_world; P = np.array([to_pt(mw @ Vector(v)) for v in co[::7]]); return P
def portico_dir(yaw_deg):
    b = Vector((cx, cy, tz(cx, cy)))
    d = Matrix.Rotation(math.radians(yaw_deg), 3, 'Z') @ Vector((0, -1, 0))
    s = to_pt(b + d) - to_pt(b); return math.degrees(math.atan2(s[1], s[0]))
TARGET_DIR = 128.0   # screen angle (y down): portico faces lower-left, toward the viewer
yaw = min(range(0, 360, 2), key=lambda a: abs(((portico_dir(a) - TARGET_DIR) + 180) % 360 - 180))
s = place(yaw, 62.0, (cx, cy))
P = screen_box()
# keep dome top >= 459pt (milestone base 452pt + gap) and left end >= 410pt (label 797:79 ends at 402pt)
dy = max(0.0, 459 - P[:, 1].min()); dx = max(0.0, 411 - P[:, 0].min())
if dx or dy:
    b0 = Vector((cx, cy, tz(cx, cy))); o_, d_ = ray(to_pt(b0) + np.array((dx, dy)))
    t = (b0.z - o_.z) / d_.z; b1 = o_ + d_ * t
    s = place(yaw, 62.0, (b1.x, b1.y)); P = screen_box()
report['pantheon'] = {'yaw': yaw, 'portico_screen_deg': round(portico_dir(yaw), 1), 'scale': round(s, 4),
                      'screen_box': [round(float(v), 1) for v in (P[:, 0].min(), P[:, 0].max(), P[:, 1].min(), P[:, 1].max())]}
link([pan], '40_REGION')

# 2. CORE 4 step cracks (3D F-01): continuous groove on cubes 1-2, water in the step-1 crack, calcium line in step 2,
#    step-3 healed seam widened to the same 2.5pt
cubes = bvh_of([O['NB_core4_sequence_GRAY03']])
P3 = [(826, 1205), (832, 1213), (821, 1219), (830, 1224), (822, 1231), (830, 1235), (825, 1243)]
P2 = [(x - 78, y) for x, y in P3]; P1 = [(x - 156, y) for x, y in P3]
groove = bpy.data.materials['RC.v12_5.crack_groove']
water = bpy.data.materials['RC.v12.base_water_process']
calc = bpy.data.materials['RC.v12.base_lime_calcium_crystal']
made, normals = [], {}
for name, pts, w, mat, lift in [('R8_crack_step1', P1, 2.5, groove, 0.03), ('R8_crack_step2', P2, 2.5, groove, 0.03),
                                ('R8_water_step1', P1[:3], 2.0, water, 0.06),
                                ('R8_calcium_step2', [(748.9, 1218.9), (743.6, 1219.3), (752, 1224), (744, 1231)], 1.6, calc, 0.06),
                                ('R8_healed_step3', P3, 2.5, calc, 0.03)]:
    o, nn = strip_on(cubes, pts, w, mat, name, lift); made.append(o); normals[name] = nn[:2]
link(made, '81_NOSHADOW')
# the model's own 1.5pt step-3 seam (inside GRAY02, with shaded groove walls) sits a little off the new seam -> remove it
g2 = O['NB_core4_sequence_GRAY02']
if g2.data.users > 1: g2.data = g2.data.copy()
bm = bmesh.new(); bm.from_mesh(g2.data); mw2 = g2.matrix_world
gone = [f for f in bm.faces if (lambda p: 810 < p[0] < 845 and 1195 < p[1] < 1250)(to_pt(mw2 @ f.calc_center_median()))]
bmesh.ops.delete(bm, geom=gone, context='FACES')
bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
bm.to_mesh(g2.data); bm.free(); report['old_step3_seam_faces'] = len(gone)
for n in ('NB_core4_sequence_GRAY01', 'R1_water_in_crack1', 'R1_calcium_dot0', 'R1_calcium_dot1', 'R1_calcium_dot2'):
    O[n].hide_render = True; O[n].hide_viewport = True
drops = O['NB_core4_sequence_GRAY04']
dw = np.array([drops.matrix_world @ v.co for v in drops.data.vertices]); c = Vector(dw.mean(0))
sp = np.array([to_pt(Vector(p)) for p in dw]); cur = np.array(((sp[:, 0].min() + sp[:, 0].max()) / 2, (sp[:, 1].min() + sp[:, 1].max()) / 2))
o_, d_ = ray(to_pt(c) + (np.array((671.0, 1174.0)) - cur)); t = (c.z - o_.z) / d_.z
drops.location += (o_ + d_ * t) - c
bpy.context.view_layer.update()
sp = np.array([to_pt(drops.matrix_world @ v.co) for v in drops.data.vertices])
report['crack_sequence'] = {'normals': normals, 'drops_box': [round(float(v), 1) for v in (sp[:, 0].min(), sp[:, 0].max(), sp[:, 1].min(), sp[:, 1].max())]}

# 3. value field F1: DETAIL tower/section lighter, lime-concrete cubes lighter, CORE 1 frame darker, grove A lighter
mid = scaled_mat('RC.v12.base_stone_middle', 'RC.v12_11.tower_middle', 1.22)
hv = scaled_mat('RC.v12_3.stone_heavy', 'RC.v12_11.tower_heavy', 1.54)
shv = scaled_mat('RC.v12_9.sect_heavy', 'RC.v12_11.sect_heavy', 1.54)
fd = scaled_mat('RC.v12.base_concrete_dense', 'RC.v12_11.tower_foundation', 1.77)
for on, m in (('D3_middle', mid), ('S_sect1', mid), ('D3_heavy', hv), ('S_sect2', shv), ('D3_foundation', fd), ('S_sect3', fd)):
    for sl in O[on].material_slots: sl.material = m
spec = bpy.data.materials['RC.v12.base_lime_specimen_matrix']
spec_before = hexof(spec.diffuse_color)
spec.diffuse_color = (*(x * 1.29 for x in spec.diffuse_color[:3]), 1)
conc = bpy.data.materials['RC.v12.concrete']; conc_before = hexof(conc.diffuse_color)
conc.diffuse_color = (*(x * 0.53 for x in conc.diffuse_color[:3]), 1)
fl, fll = bpy.data.materials['RC.v12.foliage'], bpy.data.materials['RC.v12.foliage_light']
pale = bpy.data.materials.get('RC.v12_11.foliage_pale') or fll.copy(); pale.name = 'RC.v12_11.foliage_pale'
pale.diffuse_color = (*(min(1.0, b * b / a) for a, b in zip(fl.diffuse_color[:3], fll.diffuse_color[:3])), 1)
GROVE_A = ['T_pine.001', 'T_pine.002', 'T_pine.003', 'T_pine.011', 'T_pine.013', 'T_pine.017', 'T_pine.018', 'T_pine.019']
for n in GROVE_A:
    for sl in O[n].material_slots:
        if sl.material in (fl, fll):
            m = fll if sl.material == fl else pale
            sl.link = 'OBJECT'; sl.material = m
# value F2: land one value step above sea/river (x1.07 linear)
land = bpy.data.materials['RC.v12.base_terrain']; land_before = hexof(land.diffuse_color)
land.diffuse_color = (*(min(1.0, x * 1.07) for x in land.diffuse_color[:3]), 1)
report['value'] = {'tower_middle': hexof(mid.diffuse_color), 'tower_heavy': hexof(hv.diffuse_color), 'sect_heavy': hexof(shv.diffuse_color),
                   'tower_foundation': hexof(fd.diffuse_color), 'specimen_matrix': [spec_before, hexof(spec.diffuse_color)],
                   'frame_concrete': [conc_before, hexof(conc.diffuse_color)], 'foliage_pale': hexof(pale.diffuse_color),
                   'terrain': [land_before, hexof(land.diffuse_color)], 'grove_a': GROVE_A}

print('REPORT ' + json.dumps(report, ensure_ascii=False))
H = runpy.run_path(str(ROOT / 'scripts/integrate_assets.py'), run_name='helpers')
if MODE == 'test':
    print('RENDER ' + json.dumps(H['render_two_pass'](Path(argv[1]).with_suffix('.png'))))
else:
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT), copy=False)
    r = H['render_two_pass'](ROOT / 'renders/narrative_v8_11_r8.png'); report['render'] = r
    (ROOT / 'out/v8_11-review-r8-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print('RENDER ' + json.dumps(r))
