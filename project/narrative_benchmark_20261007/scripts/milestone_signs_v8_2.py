"""v8.2: replace the flat direction arrows of v8.1 with Roman roadside milestones carrying an arrow board.

Run: blender -b out/roman_concrete_narrative_v8_1.blend --factory-startup --python scripts/milestone_signs_v8_2.py -- <sign.glb> <test|final> [test_out_prefix]
Mesh: Meshy 7.1 image-to-3d (concept text-to-image 01a12e6a…, mesh 01a12e6b-5456-721c-8aea-b6e8a00b2d5d).
"""
import bpy, bmesh, math, json, sys, runpy
from pathlib import Path
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'out/roman_concrete_narrative_v8_1.blend'
OUT = ROOT / 'out/roman_concrete_narrative_v8_2.blend'
argv = sys.argv[sys.argv.index('--') + 1:]
GLB, MODE = Path(argv[0]), argv[1]
assert Path(bpy.data.filepath).resolve() == SRC.resolve()
W_PT, H_PT = 1191, 1684
sc = bpy.context.scene
cam = sc.camera
dg = bpy.context.evaluated_depsgraph_get()
report = {}

# --- remove v8.1 flat arrows -------------------------------------------------
col = bpy.data.collections['47_DIRECTION_ARROWS']
report['removed'] = [o.name for o in col.objects]
for o in list(col.objects):
    bpy.data.objects.remove(o, do_unlink=True)
if 'ARROW_dir_mesh' in bpy.data.meshes:
    bpy.data.meshes.remove(bpy.data.meshes['ARROW_dir_mesh'])

# --- camera rays / ground ----------------------------------------------------
def world_bvh(objs):
    verts, polys = [], []
    for o in objs:
        ev = o.evaluated_get(dg); me = ev.to_mesh(); mw = o.matrix_world; b = len(verts)
        verts += [mw @ v.co for v in me.vertices]; polys += [[b + i for i in p.vertices] for p in me.polygons]
        ev.to_mesh_clear()
    return BVHTree.FromPolygons(verts, polys)
GROUND = world_bvh([bpy.data.objects['T_land']] + [o for o in bpy.data.collections['35_FIELDS_ROADS'].objects if o.type == 'MESH' and not o.hide_render])
frame = [cam.matrix_world @ v for v in cam.data.view_frame(scene=sc)]
origin = cam.matrix_world.translation
def ray(pt):
    u, v = pt[0] / W_PT, 1 - pt[1] / H_PT
    tr, br, bl, tl = frame
    return origin, ((bl + (br - bl) * u + (tl - bl) * v) - origin).normalized()
def ground_at(pt):
    hit = GROUND.ray_cast(*ray(pt))[0]; assert hit is not None, pt; return hit
def height_at(x, y):
    hit = GROUND.ray_cast(Vector((x, y, 500)), Vector((0, 0, -1)))[0]; return hit.z if hit else None
def to_pt(p):
    v = world_to_camera_view(sc, cam, p); return np.array((v.x * W_PT, (1 - v.y) * H_PT))

# --- import + decimate the Meshy milestone ------------------------------------
before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(GLB))
imported = [o for o in bpy.data.objects if o not in before]
src = next(o for o in imported if o.type == 'MESH')
for o in imported:
    if o is not src: bpy.data.objects.remove(o, do_unlink=True)
src.parent = None
dec = src.modifiers.new('dec', 'DECIMATE'); dec.ratio = 0.16
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
me = bpy.data.meshes.new_from_object(src.evaluated_get(dg))
me.transform(src.matrix_world)
bpy.data.objects.remove(src, do_unlink=True)
me.name = 'MILESTONE_sign_mesh'

# --- segment stone column / plinth / arrow board by geometry ----------------
co = np.array([v.co[:] for v in me.vertices])
zmin, zmax = co[:, 2].min(), co[:, 2].max(); H0 = zmax - zmin
u = (co[:, 2] - zmin) / H0
slices = np.linspace(0, 1, 41)
ext = []
for a, b in zip(slices[:-1], slices[1:]):
    s = (u >= a) & (u < b)
    ext.append(np.ptp(co[s, 0]) * np.ptp(co[s, 1]) if s.sum() > 10 else 0)
ext = np.array(ext); base_ext = ext[:3].max()
plinth_top = next(slices[i] for i in range(3, 40) if ext[i] < 0.6 * base_ext)
low = (u > plinth_top + 0.03) & (u < plinth_top + 0.25)
cx, cy = np.median(co[low, 0]), np.median(co[low, 1])
rad = np.percentile(np.hypot(co[low, 0] - cx, co[low, 1] - cy), 96)
dist = np.hypot(co[:, 0] - cx, co[:, 1] - cy)
far = (dist > rad * 1.35) & (u > plinth_top + 0.05)
P = co[far, :2] - (cx, cy)
evals, evecs = np.linalg.eigh(np.cov(P.T))
axis = evecs[:, 1]; normal = evecs[:, 0]
sA, sN = P @ axis, P @ normal
d0 = np.median(sN); half_t = np.percentile(np.abs(sN - d0), 97) * 1.25
# head = side whose far part spans more height (arrowhead taller than plank)
pos, neg = sA > 0, sA < 0
if np.ptp(u[far][pos]) < np.ptp(u[far][neg]):
    axis = -axis; sA = -sA
umin_b, umax_b = u[far].min() - 0.02, u[far].max() + 0.02
amin, amax = sA.min(), sA.max()
# canonical frame first: base centre at origin, board head along +X, board on the -Y side, unit height
ang = math.atan2(axis[1], axis[0])
R = Matrix.Rotation(-ang, 4, 'Z')
off = Vector((-cx, -cy, -zmin))
bm = bmesh.new(); bm.from_mesh(me)
for v in bm.verts:
    v.co = (R @ (v.co + off)) / H0
side = (R @ Vector((*(normal * d0), 0))).y
if side > 0:
    for v in bm.verts: v.co.y = -v.co.y
    bmesh.ops.reverse_faces(bm, faces=bm.faces)
r_u, t_u, pt_u = rad / H0, 2 * half_t / H0, plinth_top
# board = stone-free parts: outside the column cylinder inside the board band, or proud of the column front
counts = [0, 0, 0, 0]
cls = {}
for f in bm.faces:
    c = f.calc_center_median(); rr = math.hypot(c.x, c.y)
    if c.z < pt_u: idx = 1
    elif umin_b <= c.z <= umax_b and (rr > r_u * 1.08 or c.y < -(r_u + 0.3 * t_u)): idx = 2
    else: idx = 0
    cls[f] = idx
# iron straps: proud faces over the column that lie above/below the plank band beside the column
beside = [f.calc_center_median().z for f, i in cls.items() if i == 2 and r_u * 0.8 < abs(f.calc_center_median().x) < r_u * 1.4]
pz0, pz1 = min(beside), max(beside)
for f, i in cls.items():
    c = f.calc_center_median()
    if i == 2 and abs(c.x) < r_u * 0.8 and (c.z < pz0 - 0.004 or c.z > pz1 + 0.004):
        cls[f] = 3
for f, i in cls.items():
    f.material_index = i; counts[i] += 1
me.materials.clear()
for name in ('RC.v12.roman_stone', 'RC.v12.roman_plinth', 'RC.v12_1.direction_arrow', 'RC.v12.toolmetal'):
    me.materials.append(bpy.data.materials[name])
# the board carries the message: enlarge it about the column axis (length x1.45, height x1.3, thickness kept);
# vertices shared with stone/strap faces stay put so the column surface is never dragged along
KX, KZ = 1.45, 1.3
board_only = [v for v in bm.verts if v.link_faces and all(cls[f] == 2 for f in v.link_faces)]
zc = sum(v.co.z for v in board_only) / len(board_only)
for v in board_only:
    v.co.x *= KX; v.co.z = zc + (v.co.z - zc) * KZ
bm.to_mesh(me); bm.free()
for p in me.polygons: p.use_smooth = False
mi = np.zeros(len(me.polygons), int); me.polygons.foreach_get('material_index', mi)
assert set(np.unique(mi)) >= {0, 1, 2}, np.unique(mi)
bx = np.array([v.co[:] for v in me.vertices])
board_u = zc
report['mesh'] = {'tris': sum(len(p.vertices) - 2 for p in me.polygons), 'faces_stone_plinth_board_strap': counts,
                  'plinth_top_u': round(float(plinth_top), 3), 'column_r_over_H': round(float(r_u), 3),
                  'board_u': [round(float(umin_b), 3), round(float(umax_b), 3)], 'plank_band_u': [round(pz0, 3), round(pz1, 3)],
                  'x_extent': [round(float(bx[:, 0].min()), 3), round(float(bx[:, 0].max()), 3)], 'board_scale': [KX, KZ]}

# mirrored twin: board on +Y, so a sign can point either way with its board face to the camera
me_m = me.copy(); me_m.name = 'MILESTONE_sign_mesh_mirror'
bm = bmesh.new(); bm.from_mesh(me_m)
for v in bm.verts: v.co.y = -v.co.y
bmesh.ops.reverse_faces(bm, faces=bm.faces)
bm.to_mesh(me_m); bm.free()

# --- placement -----------------------------------------------------------------
# base = ground contact (poster pt), dir = screen direction the board should point (from user's red marks)
SIGNS = {
    'MS1_core1_to_2': {'base': (478, 446), 'dir': (-46, 36)},
    'MS2_core2_to_34': {'base': (236, 992), 'dir': (59, 48)},
    'MS3_core34_to_5': {'base': (797, 996), 'dir': (70, -39)},
}
SCREEN_H = float(argv[3]) if len(argv) > 3 and argv[3].replace('.', '').isdigit() else 70.0
tipx = bx[:, 0].max(); rootx = 0.0
placed = {}
for name, cfg in SIGNS.items():
    g = ground_at(cfg['base'])
    # unit-height object: find scale so base->top spans SCREEN_H pt
    S = 5.0
    for _ in range(25):
        S *= SCREEN_H / np.linalg.norm(to_pt(g + Vector((0, 0, S))) - to_pt(g))
    want = np.array(cfg['dir'], float); want /= np.linalg.norm(want)
    hb = board_u * S
    to_cam = (origin - (g + Vector((0, 0, hb)))).normalized()
    cands = []
    for deg in range(0, 360, 1):
        t = math.radians(deg)
        a = Vector((math.cos(t), math.sin(t), 0))
        root, tip = g + Vector((0, 0, hb)), g + Vector((0, 0, hb)) + a * tipx * S
        d = to_pt(tip) - to_pt(root); L = np.linalg.norm(d)
        err = math.degrees(math.acos(max(-1, min(1, float(d @ want) / L))))
        for mirror in (False, True):
            n = Vector((math.sin(t), -math.cos(t), 0)) * (-1 if mirror else 1)
            vis = n.dot(to_cam)  # >0: board face visible and board in front of the column
            cands.append((err, vis, deg, mirror, L))
    ok = [c for c in cands if c[1] > 0.35] or [c for c in cands if c[1] > 0.2]
    err, vis, deg, mirror, L = min(ok, key=lambda c: c[0] - 20 * c[1])
    o = bpy.data.objects.new(name, me_m if mirror else me); col.objects.link(o)
    o.rotation_euler = (0, 0, math.radians(deg)); o.scale = (S, S, S)
    # plinth footprint resting on the highest ground under it
    hs = [height_at(g.x + dx * S * 0.3, g.y + dy * S * 0.3) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    o.location = (g.x, g.y, max(h for h in hs if h is not None) - 0.01 * S)
    bpy.context.view_layer.update()
    pts = np.array([to_pt(o.matrix_world @ v.co) for v in list(o.data.vertices)[::9]])
    placed[name] = {'mirror': mirror, 'yaw_deg': deg, 'dir_err_deg': round(err, 1), 'board_face_visibility': round(vis, 2),
                    'board_screen_len': round(L, 1), 'scale': round(S, 3),
                    'screen_box': [round(float(pts[:, 0].min()), 1), round(float(pts[:, 0].max()), 1), round(float(pts[:, 1].min()), 1), round(float(pts[:, 1].max()), 1)]}
report['signs'] = placed
TEXT = {'C1_frame': (528, 702, 386, 493), 'apennine': (360, 432, 405, 447), 'lime_label': (143, 187, 1001, 1013),
        'C4_frame': (638, 817, 1032, 1139), 'privernum': (826, 894, 1020, 1095), 'C3_frame': (408, 599, 1028, 1119)}
gaps = {}
for name, p in placed.items():
    x0, x1, y0, y1 = p['screen_box']
    for k, (a0, a1, b0, b1) in TEXT.items():
        gap = max(a0 - x1, x0 - a1, b0 - y1, y0 - b1)
        if gap < 15: gaps[f'{name}~{k}'] = round(gap, 1)
report['near_text_gaps'] = gaps
print('REPORT ' + json.dumps(report, ensure_ascii=False))

H = runpy.run_path(str(ROOT / 'scripts/integrate_assets.py'), run_name='helpers')
if MODE == 'test':
    res = H['render_two_pass'](Path(argv[2] if len(argv) > 2 and not argv[2].replace('.', '').isdigit() else '/tmp/ms_test').with_suffix('.png'))
    print('RENDER ' + json.dumps(res))
elif MODE == 'final':
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT), copy=False)
    res = H['render_two_pass'](ROOT / 'renders/narrative_v8_2_milestones.png')
    report['render'] = res
    (ROOT / 'out/v8_2-milestones-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print('RENDER ' + json.dumps(res))
