"""v8.5: apply verified round-2 critic findings to the Blender map.

Run: blender -b out/roman_concrete_narrative_v8_4.blend --factory-startup --python scripts/review_r2_fixes_v8_5.py -- <test|final> [test_prefix]
"""
import bpy, bmesh, math, json, sys, runpy
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'out/roman_concrete_narrative_v8_4.blend'
OUT = ROOT / 'out/roman_concrete_narrative_v8_5.blend'
argv = sys.argv[sys.argv.index('--') + 1:]
MODE = argv[0]
assert Path(bpy.data.filepath).resolve() == SRC.resolve()
sc = bpy.context.scene; cam = sc.camera; O = bpy.data.objects
report = {}

def lin(h):
    return tuple(((int(h[i:i + 2], 16) / 255 + 0.055) / 1.055) ** 2.4 for i in (1, 3, 5))
def set_color(m, hexv):
    c = (*lin(hexv), 1); m.diffuse_color = c
    if m.node_tree:
        b = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if b: b.inputs['Base Color'].default_value = c
def new_mat(name, hexv, like='RC.v12.roman_stone'):
    m = bpy.data.materials.get(name) or bpy.data.materials[like].copy(); m.name = name; set_color(m, hexv); return m
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
def strip_on(bvh, pts, width_pt, mat, name, lift_pt=0.35):
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
    o = O.new(name, me); bpy.data.collections['46_NARRATIVE_ASSETS'].objects.link(o); return o

# 1. specimens: the 'no quicklime' cylinder carries no lime grains; cracks read at 1.5 m (infographic F-15, 3D NEW-01/F-01)
for n in [n for n in O.keys() if n.startswith('R1_leak_clast')] + ['R1_leak_crack', 'R1_healed_fill']:
    bpy.data.objects.remove(O[n], do_unlink=True)
for n in [n for n in O.keys() if n.startswith('R1_healed_clast')]:
    O[n].scale *= 1.7
SA, SB = bvh_of([O['R1_specimen_healed']]), bvh_of([O['R1_specimen_leaking']])
def centre_pt(o):
    P = np.array([to_pt(o.matrix_world @ v.co) for v in o.data.vertices]); return (P[:, 0].min() + P[:, 0].max()) / 2, (P[:, 1].min() + P[:, 1].max()) / 2
ca, cb = centre_pt(O['R1_specimen_healed']), centre_pt(O['R1_specimen_leaking'])
def crack(c):  # 32pt continuous zigzag on the face that looks at the camera
    x, y = c
    return [(x - 6, y - 16), (x - 2, y - 10), (x - 5, y - 4), (x + 1, y + 2), (x - 2, y + 8), (x + 3, y + 14)]
groove = new_mat('RC.v12_5.crack_groove', '#2A211C')
healed = new_mat('RC.v12_5.healed_fill', '#F2EEE4')
strip_on(SA, crack(ca), 2.2, healed, 'R2_healed_fill')
strip_on(SB, crack(cb), 2.2, groove, 'R2_leak_crack')
report['specimens'] = {'healed_centre': [round(v, 1) for v in ca], 'leaking_centre': [round(v, 1) for v in cb]}

# 2. colour: workers' cloth and rust leave the accent's neighbourhood (color CL-12/22); heavy stone step (3D F-07)
set_color(bpy.data.materials['RC.v12.cloth'], '#A47C66')
set_color(bpy.data.materials['RC.v12_3.rust_stain'], '#71594A')
set_color(bpy.data.materials['RC.v12_3.stone_heavy'], '#8B7D65')

# 3. wave marks under '(서기 79년)' and beside '티레니아해' (hierarchy F-03, typography TY-F1, layout LY-02)
Wm = O['W_water_marks']
if Wm.data.users > 1: Wm.data = Wm.data.copy()
bm = bmesh.new(); bm.from_mesh(Wm.data); mw = Wm.matrix_world
ZONES = [(846, 872, 1545, 1570), (186, 210, 1530, 1552)]
gone = [f for f in bm.faces if any(x0 < p[0] < x1 and y0 < p[1] < y1 for (x0, x1, y0, y1) in ZONES for p in [to_pt(mw @ f.calc_center_median())])]
bmesh.ops.delete(bm, geom=gone, context='FACES'); bm.to_mesh(Wm.data); bm.free()
report['wave_faces_removed'] = len(gone)

# 4. Colosseum: scan debris outside the wall ellipse goes; piazza ring tucks under the walls and stays 4pt off the Tiber (3D F-02, F-06)
col = O['COL_ruined']
if col.data.users > 1: col.data = col.data.copy()
cmw = col.matrix_world
co = np.array([cmw @ v.co for v in col.data.vertices])
wall = co[co[:, 2] > 2.0]; c = wall[:, :2].mean(0)
ev, evec = np.linalg.eigh(np.cov((wall[:, :2] - c).T)); ax = evec[:, ::-1]
uv = (wall[:, :2] - c) @ ax
A, B = np.percentile(np.abs(uv[:, 0]), 99.5), np.percentile(np.abs(uv[:, 1]), 99.5)
bm = bmesh.new(); bm.from_mesh(col.data)
def rn_of(p):
    q = (np.array((p.x, p.y)) - c) @ ax; return math.hypot(q[0] / A, q[1] / B)
dead = []
for f in bm.faces:
    p = cmw @ f.calc_center_median()
    if rn_of(p) > 1.01 and p.z < tz(p.x, p.y) + 3.0: dead.append(f)
bmesh.ops.delete(bm, geom=dead, context='FACES')
loose = [v for v in bm.verts if not v.link_faces]
bmesh.ops.delete(bm, geom=loose, context='VERTS')
bm.to_mesh(col.data); bm.free()
report['colosseum_debris_faces'] = len(dead)
bpy.data.objects.remove(O['R1_colosseum_piazza'], do_unlink=True)
TIBER = bvh_of([O['L02_tiber']])
R_IN, R_OUT, LIFT = 0.94, 1.12, 0.42
bm = bmesh.new(); N = 200; ri, ro, rl = [], [], []
for k in range(N):
    t = 2 * math.pi * k / N
    def at(r):
        p2 = c + ax[:, 0] * A * r * math.cos(t) + ax[:, 1] * B * r * math.sin(t); return Vector((p2[0], p2[1], tz(p2[0], p2[1]) + LIFT))
    r_ok = R_OUT
    for r in np.linspace(1.0, R_OUT, 25):
        p = at(r); near = TIBER.find_nearest(p)[0]
        if near is not None and (Vector((near.x, near.y, 0)) - Vector((p.x, p.y, 0))).length < 4 * wpp(p) + 0.02:
            r_ok = max(1.0, r - 0.01); break
    ri.append(bm.verts.new(at(R_IN))); po = at(r_ok); ro.append(bm.verts.new(po))
    rl.append(bm.verts.new((po.x, po.y, tz(po.x, po.y) - 0.05)))
for k in range(N):
    j = (k + 1) % N
    bm.faces.new((ri[k], ri[j], ro[j], ro[k])); bm.faces.new((ro[k], ro[j], rl[j], rl[k]))
me = bpy.data.meshes.new('R2_colosseum_piazza'); bm.to_mesh(me); bm.free()
me.materials.append(bpy.data.materials['RC.v12_4.piazza_travertine'])
pz = O.new('R2_colosseum_piazza', me); bpy.data.collections['20_LANDMARK'].objects.link(pz)

# 5. Via Ostiensis reaches the harbour shore instead of stopping in open land (3D F-04)
road = O['R_via_ostiensis']
if road.data.users > 1: road.data = road.data.copy()
rmw = road.matrix_world; rinv = rmw.inverted()
bm = bmesh.new(); bm.from_mesh(road.data)
seg = [f for f in bm.faces if 1296 < to_pt(rmw @ f.calc_center_median())[1] <= 1352]
segc = sum((rmw @ f.calc_center_median() for f in seg), Vector()) / len(seg)
far = [f for f in bm.faces if 1250 < to_pt(rmw @ f.calc_center_median())[1] <= 1296]
farc = sum((rmw @ f.calc_center_median() for f in far), Vector()) / len(far)
step = segc - farc; step.z = 0
SEA = bvh_of([O['L10_sea']])
added = 0
for rep in (1, 2):
    dup = bmesh.ops.duplicate(bm, geom=seg)
    for v in [g for g in dup['geom'] if isinstance(g, bmesh.types.BMVert)]:
        w = rmw @ v.co; nw = w + step * rep
        nw.z = w.z + (tz(nw.x, nw.y) - tz(w.x, w.y))
        v.co = rinv @ nw
    faces = [g for g in dup['geom'] if isinstance(g, bmesh.types.BMFace)]
    wet = []
    for f in faces:
        p = rmw @ f.calc_center_median()
        s = SEA.ray_cast(Vector((p.x, p.y, 500)), Vector((0, 0, -1)))[0]
        if s is not None and s.z > tz(p.x, p.y) - 0.01: wet.append(f)
    bmesh.ops.delete(bm, geom=wet, context='FACES'); added += len(faces) - len(wet)
bm.to_mesh(road.data); bm.free()
report['ostiensis_faces_added'] = added

# 6. researchers scene: four adults to one height (≈21pt) about their own feet (3D F-03)
res = O['C5_researchers']
if res.data.users > 1: res.data = res.data.copy()
mw = res.matrix_world; inv = mw.inverted()
RB = bvh_of([res])
co = np.array([mw @ v.co for v in res.data.vertices])
done = {}
# head-top and feet points measured on the 2x render (critic F-03): left 30.8, back 25.4, front 28.7, red 22.0 pt -> 21 pt
FIG = {'left': ((884, 1176.5), (884, 1204.5), 21 / 30.8), 'back': ((913, 1168), (913, 1191), 21 / 25.4),
       'front': ((907, 1186.5), (906, 1212.5), 21 / 28.7), 'red': ((951, 1196.5), (951, 1215.5), 21 / 22.0)}
for name, (head_pt, feet_pt, k) in FIG.items():
    hh, _ = hit(RB, head_pt); hf, _ = hit(RB, feet_pt)
    if hh is None or hf is None: done[name] = 'miss'; continue
    Hw = max(hh.z - hf.z, 1e-3)
    r = 0.24 * Hw
    d = np.hypot(co[:, 0] - hh.x, co[:, 1] - hh.y)
    sel = (d < r) & (co[:, 2] > hf.z + 0.02 * Hw) & (co[:, 2] < hh.z + 0.08 * Hw)
    feet = Vector((hh.x, hh.y, hf.z))
    for i in np.nonzero(sel)[0]:
        res.data.vertices[i].co = inv @ (feet + (Vector(co[i]) - feet) * k)
    done[name] = {'H_world': round(Hw, 3), 'scale': round(k, 2), 'verts': int(sel.sum())}
res.data.update()
report['researchers'] = done

# 7. Pompeii pin ends on the quicklime heap (layout LY-06)
pin, dot = O['S_pin_pompeii'], O['S_pin_pompeii_dot']
for ob in (pin, dot):
    if ob.data.users > 1: ob.data = ob.data.copy()
bm = bmesh.new(); bm.from_mesh(pin.data); pmw = pin.matrix_world
cut = [f for f in bm.faces if to_pt(pmw @ f.calc_center_median())[1] < 1496]
bmesh.ops.delete(bm, geom=cut, context='FACES'); bm.to_mesh(pin.data); bm.free()
dc = sum((dot.matrix_world @ v.co for v in dot.data.vertices), Vector()) / len(dot.data.vertices)
s0 = to_pt(dc); o_, d_ = ray((s0[0], s0[1] + 12))
n = (origin - dc).normalized(); t = (dc - o_).dot(n) / d_.dot(n)
dot.location += (o_ + d_ * t) - dc
report['pompeii_pin'] = {'dash_faces_cut': len(cut)}

# 8. trees: smooth canopies (3D F-08)
for o in bpy.data.collections['60_TREES'].all_objects:
    if o.type == 'MESH':
        for p in o.data.polygons: p.use_smooth = True

# 9. CORE badges + underlines for the 19.5/24.5 module; badge centre (X+10.5, Y+13.55), underline Y+51.55..52.75
CORE = {1: (528, 382, 113), 2: (57.5, 744, 77), 3: (408.5, 1028, 135), 4: (638.5, 1028, 113), 5: (982.5, 813, 171)}
def plane_of(o):
    P = [o.matrix_world @ v.co for v in o.data.vertices]; cen = sum(P, Vector()) / len(P)
    for i in range(2, len(P)):
        n = (P[1] - P[0]).cross(P[i] - P[0])
        if n.length > 1e-9: return cen, n.normalized()
def rebuild(o, pts2d):
    cen, n = plane_of(o); inv = o.matrix_world.inverted()
    W = []
    for p in pts2d:
        o_, d_ = ray(p); t = (cen - o_).dot(n) / d_.dot(n); W.append(o_ + d_ * t)
    bm = bmesh.new(); vs = [bm.verts.new(inv @ w) for w in W]; bm.faces.new(vs); bm.to_mesh(o.data); bm.free()
for k, (X, Y, w2) in CORE.items():
    b, u = O[f'S_core{k}_badge'], O[f'S_core{k}_underline']
    cx, cy = X + 10.5, Y + 13.55
    rebuild(b, [(cx + 10.5 * math.cos(a), cy + 10.5 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 49)[:-1]])
    rebuild(u, [(X, Y + 51.55), (X + w2, Y + 51.55), (X + w2, Y + 52.75), (X, Y + 52.75)])
report['core_overlays'] = CORE

print('REPORT ' + json.dumps(report, ensure_ascii=False))
H = runpy.run_path(str(ROOT / 'scripts/integrate_assets.py'), run_name='helpers')
if MODE == 'test':
    print('RENDER ' + json.dumps(H['render_two_pass'](Path(argv[1]).with_suffix('.png'))))
else:
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT), copy=False)
    r = H['render_two_pass'](ROOT / 'renders/narrative_v8_5_r2.png'); report['render'] = r
    (ROOT / 'out/v8_5-review-r2-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print('RENDER ' + json.dumps(r))
