"""v8.6: apply verified round-3 critic findings to the Blender map.

Run: blender -b out/roman_concrete_narrative_v8_5.blend --factory-startup --python scripts/review_r3_fixes_v8_6.py -- <test|final> [test_prefix]
"""
import bpy, bmesh, math, json, sys, runpy
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'out/roman_concrete_narrative_v8_5.blend'
OUT = ROOT / 'out/roman_concrete_narrative_v8_6.blend'
argv = sys.argv[sys.argv.index('--') + 1:]
MODE = argv[0]
assert Path(bpy.data.filepath).resolve() == SRC.resolve()
sc = bpy.context.scene; cam = sc.camera; O = bpy.data.objects
report = {}

def lin(h):
    return tuple(((int(h[i:i + 2], 16) / 255 + 0.055) / 1.055) ** 2.4 for i in (1, 3, 5))
def new_mat(name, hexv, like='RC.v12.roman_stone'):
    m = bpy.data.materials.get(name) or bpy.data.materials[like].copy(); m.name = name
    c = (*lin(hexv), 1); m.diffuse_color = c
    if m.node_tree:
        b = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if b: b.inputs['Base Color'].default_value = c
    return m
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
def hit(bvh, pt):
    h, n, i, d = bvh.ray_cast(*ray(pt)); return (h, n) if h is not None else (None, None)
def wpp(p):
    r = cam.matrix_world.col[0].xyz.normalized(); return 1.0 / np.linalg.norm(to_pt(p + r) - to_pt(p))
TERRAIN = bvh_of([O['T_land']])
def tz(x, y):
    h = TERRAIN.ray_cast(Vector((x, y, 500)), Vector((0, 0, -1)))[0]; return h.z if h else 0.0
def strip_on(bvh, pts, width_pt, mat, name, coll='46_NARRATIVE_ASSETS', lift_pt=0.35):
    hits = [hit(bvh, p) for p in pts]
    assert all(h[0] is not None for h in hits), (name, pts)
    bm = bmesh.new(); L, R = [], []
    for k, (h, n) in enumerate(hits):
        a = hits[max(k - 1, 0)][0]; b = hits[min(k + 1, len(hits) - 1)][0]
        t = (b - a).normalized(); side = n.cross(t).normalized(); w = width_pt * wpp(h) / 2
        base = h + n * lift_pt * wpp(h)
        L.append(bm.verts.new(base + side * w)); R.append(bm.verts.new(base - side * w))
    for k in range(len(pts) - 1): bm.faces.new((L[k], L[k + 1], R[k + 1], R[k]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    o = O.new(name, me); bpy.data.collections[coll].objects.link(o); return o
def plane_of(o):
    P = [o.matrix_world @ v.co for v in o.data.vertices]; cen = sum(P, Vector()) / len(P)
    for i in range(2, len(P)):
        n = (P[1] - P[0]).cross(P[i] - P[0])
        if n.length > 1e-9: return cen, n.normalized()
def rebuild(o, pts2d):
    if o.data.users > 1: o.data = o.data.copy()
    cen, n = plane_of(o); inv = o.matrix_world.inverted(); W = []
    for p in pts2d:
        o_, d_ = ray(p); t = (cen - o_).dot(n) / d_.dot(n); W.append(o_ + d_ * t)
    bm = bmesh.new(); vs = [bm.verts.new(inv @ w) for w in W]; bm.faces.new(vs); bm.to_mesh(o.data); bm.free()

# 1. Colosseum: everything outside 0.955 x the wall ellipse and below 1.25 above ground goes; the travertine ring
#    becomes a 1.25 podium that tucks under the walls (3D I3-F2: strands, floor flakes, hole)
col = O['COL_ruined']
if col.data.users > 1: col.data = col.data.copy()
cmw = col.matrix_world
co = np.array([cmw @ v.co for v in col.data.vertices])
wall = co[co[:, 2] > 2.0]; c = wall[:, :2].mean(0)
ev, evec = np.linalg.eigh(np.cov((wall[:, :2] - c).T)); ax = evec[:, ::-1]
uv = (wall[:, :2] - c) @ ax
A, B = np.percentile(np.abs(uv[:, 0]), 99.5), np.percentile(np.abs(uv[:, 1]), 99.5)
def rn_of(x, y):
    q = (np.array((x, y)) - c) @ ax; return math.hypot(q[0] / A, q[1] / B)
LIFT, TALL = 0.6, 3.2
# per angle, the real outer wall line = outermost face of the standing (>= 3.2 above ground) structure.
# Low faces outside that line are scan debris (collapsed-ring strands, floor flakes) and go.
NB = 96
def polar(x, y):
    q = (np.array((x, y)) - c) @ ax
    return math.hypot(q[0] / A, q[1] / B), int((math.atan2(q[1] / B, q[0] / A) + math.pi) / (2 * math.pi) * NB) % NB
bm = bmesh.new(); bm.from_mesh(col.data)
info = []
for f in bm.faces:
    P = [cmw @ v.co for v in f.verts]
    x_, y_ = sum(p.x for p in P) / len(P), sum(p.y for p in P) / len(P)
    r_, b_ = polar(x_, y_); hmax = max(p.z for p in P) - tz(x_, y_)
    info.append((f, r_, b_, hmax))
tall_r = [[] for _ in range(NB)]
for f, r_, b_, h in info:
    if h >= TALL: tall_r[b_].append(r_)
wall_rn = np.array([np.percentile(sum((tall_r[(b + d) % NB] for d in (-1, 0, 1)), []), 98) if sum(len(tall_r[(b + d) % NB]) for d in (-1, 0, 1)) else 0.9 for b in range(NB)])
dead = [f for f, r_, b_, h in info if h < TALL and r_ > wall_rn[b_] + 0.012]
bmesh.ops.delete(bm, geom=dead, context='FACES')
bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
bm.to_mesh(col.data); bm.free()
report['colosseum_debris_faces'] = len(dead)
report['wall_rn_range'] = [round(float(wall_rn.min()), 3), round(float(wall_rn.max()), 3)]
bpy.data.objects.remove(O['R2_colosseum_piazza'], do_unlink=True)
TIBER = bvh_of([O['L02_tiber']])
# smooth the wall line around the ring (circular moving average) so the podium edge reads as one clean curve
k_ = np.ones(9) / 9
wall_s = np.convolve(np.concatenate([wall_rn[-4:], wall_rn, wall_rn[:4]]), k_, mode='valid')
N = 240
ts = np.linspace(0, 2 * math.pi, N, endpoint=False)
def ell(r, t):
    p2 = c + ax[:, 0] * A * r * math.cos(t) + ax[:, 1] * B * r * math.sin(t); return p2
rin, rout, zt = [], [], []
for t in ts:
    bb = int((math.atan2(math.sin(t), math.cos(t)) + math.pi) / (2 * math.pi) * NB) % NB
    w = wall_s[bb]; r_in = max(0.70, w - 0.03); r_out_max = w + 0.15; r_ok = r_out_max
    for r in np.linspace(w, r_out_max, 25):
        p2 = ell(r, t); pv = Vector((p2[0], p2[1], tz(p2[0], p2[1])))
        near = TIBER.find_nearest(pv)[0]
        if near is not None and (Vector((near.x, near.y, 0)) - Vector((pv.x, pv.y, 0))).length < 4 * wpp(pv) + 0.02:
            r_ok = max(w + 0.005, r - 0.01); break
    rin.append(r_in); rout.append(r_ok)
    p2 = ell(r_ok, t); zt.append(tz(p2[0], p2[1]))
zt = np.array(zt); zs = np.convolve(np.concatenate([zt[-6:], zt, zt[:6]]), np.ones(13) / 13, mode='valid')
rout = np.convolve(np.concatenate([rout[-3:], rout, rout[:3]]), np.ones(7) / 7, mode='valid')
bm = bmesh.new(); ri, ro, rl = [], [], []
for t, r_in, r_o, z in zip(ts, rin, rout, zs):
    pi_, po_ = ell(r_in, t), ell(r_o, t)
    ri.append(bm.verts.new((pi_[0], pi_[1], z + LIFT))); ro.append(bm.verts.new((po_[0], po_[1], z + LIFT)))
    rl.append(bm.verts.new((po_[0], po_[1], tz(po_[0], po_[1]) - 0.05)))
for k in range(N):
    j = (k + 1) % N
    bm.faces.new((ri[k], ri[j], ro[j], ro[k])); bm.faces.new((ro[k], ro[j], rl[j], rl[k]))
me = bpy.data.meshes.new('R3_colosseum_podium'); bm.to_mesh(me); bm.free()
me.materials.append(bpy.data.materials['RC.v12_4.piazza_travertine'])
pz = O.new('R3_colosseum_podium', me); bpy.data.collections['20_LANDMARK'].objects.link(pz)

# 2. CORE 1 crack readable at 1.5 m: one continuous groove, measured screen width >= 2.5pt (3D I3-F3)
for n in ('R1_frame_crack_col', 'R1_frame_crack_col2'):
    bpy.data.objects.remove(O[n], do_unlink=True)
bldg = bvh_of([O['NB_modern_building']])
groove = bpy.data.materials.get('RC.v12_5.crack_groove') or new_mat('RC.v12_5.crack_groove', '#2A211C')
# front-left column face x 714-722 (probed); side faces foreshorten the ribbon to ~0.4x, so model width 6.5pt
strip_on(bldg, [(718, 448), (720, 456), (717, 464), (719.5, 472), (717.5, 480), (719, 489)], 6.5, groove, 'R3_frame_crack_col')
strip_on(bldg, [(748, 466), (750, 475), (747, 484), (749.5, 494)], 5.0, groove, 'R3_frame_crack_col2')

# 3. CORE 5 specimen cracks a touch wider (2.2 -> 2.8pt)
healed = bpy.data.materials['RC.v12_5.healed_fill']
for n, mat, src in (('R2_healed_fill', healed, 'R1_specimen_healed'), ('R2_leak_crack', groove, 'R1_specimen_leaking')):
    bpy.data.objects.remove(O[n], do_unlink=True)
    P = np.array([to_pt(O[src].matrix_world @ v.co) for v in O[src].data.vertices])
    x, y = (P[:, 0].min() + P[:, 0].max()) / 2, (P[:, 1].min() + P[:, 1].max()) / 2
    strip_on(bvh_of([O[src]]), [(x - 6, y - 16), (x - 2, y - 10), (x - 5, y - 4), (x + 1, y + 2), (x - 2, y + 8), (x + 3, y + 14)], 2.8, mat, n.replace('R2', 'R3'))

# 4. structure-model leaders only on paper: block edge + 1pt -> label - 1.5pt (color CL-18)
LEAD = {'S_lead03': (1231.9, 314.6, 320.3), 'S_lead05': (1258.5, 314.6, 328.6), 'S_lead07': (1287.0, 316.6, 324.3), 'S_lead09': (1308.0, 319.6, 323.1)}
for n, (y, x0, x1) in LEAD.items():
    rebuild(O[n], [(x0, y - 0.45), (x1, y - 0.45), (x1, y + 0.45), (x0, y + 0.45)])
report['structure_leaders'] = LEAD

# 5. harbour pin follows its block (moved up 14.8pt): drop dashes below the new title top; clear two wave marks
pin = O['S_pin_harbor']
if pin.data.users > 1: pin.data = pin.data.copy()
bm = bmesh.new(); bm.from_mesh(pin.data); pmw = pin.matrix_world
cut = [f for f in bm.faces if to_pt(pmw @ f.calc_center_median())[1] > 1518]
bmesh.ops.delete(bm, geom=cut, context='FACES'); bm.to_mesh(pin.data); bm.free()
Wm = O['W_water_marks']
if Wm.data.users > 1: Wm.data = Wm.data.copy()
bm = bmesh.new(); bm.from_mesh(Wm.data); wmw = Wm.matrix_world
ZONES = [(228, 352, 1515, 1584), (266, 290, 1506, 1522)]
gone = [f for f in bm.faces if any(x0 < p[0] < x1 and y0 < p[1] < y1 for (x0, x1, y0, y1) in ZONES for p in [to_pt(wmw @ f.calc_center_median())])]
bmesh.ops.delete(bm, geom=gone, context='FACES'); bm.to_mesh(Wm.data); bm.free()
report['harbour'] = {'pin_dash_faces_cut': len(cut), 'wave_faces_removed': len(gone)}

# 6. CORE underlines start at the title-2 ink and run its ink width (typography TY-15-1)
UL = {1: (528.8, 382, 109.6), 2: (58.5, 744, 74.8), 3: (409.4, 1028, 131.9), 4: (639.5, 1028, 110.7), 5: (983.3, 813, 169.1)}
for k, (x, Y, w) in UL.items():
    rebuild(O[f'S_core{k}_underline'], [(x, Y + 51.55), (x + w, Y + 51.55), (x + w, Y + 52.75), (x, Y + 52.75)])
report['underlines'] = UL

print('REPORT ' + json.dumps(report, ensure_ascii=False))
H = runpy.run_path(str(ROOT / 'scripts/integrate_assets.py'), run_name='helpers')
if MODE == 'test':
    print('RENDER ' + json.dumps(H['render_two_pass'](Path(argv[1]).with_suffix('.png'))))
else:
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT), copy=False)
    r = H['render_two_pass'](ROOT / 'renders/narrative_v8_6_r3.png'); report['render'] = r
    (ROOT / 'out/v8_6-review-r3-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print('RENDER ' + json.dumps(r))
