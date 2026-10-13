"""WB step (wave 1, input v8_14): CORE ② hot-mixing scene C2 + 제작 원리 dice D2 + its leader.

Owned objects: C2_hot_mixing, D2_making, D2_cube, D2_heat0~2, D2_lime00~15 (not D2_lime_kiln), S_lead02, S_lead_dot2,
and the objects this step creates: C2_pourer, C2_mixer, C2_hoe, C2_water, C2_heat0~2.
Nothing else is changed (fingerprint of every other object, before/after; the step refuses to save otherwise).

What it does (see report json for numbers):
 1. C2_hot_mixing: the two old scanned workers (skin/linen/cloth/toolwood faces) are removed; the pit and platform are
    flattened (z x C2_FLAT) so the new, smaller workers can work over the rim; the paste takes the shared Roman-concrete
    token RC.v12.base_lime_specimen_matrix (same token as ③④⑤ and the dice); the scene moves on the ground by
    C2_SHIFT_PT (screen pt) and is re-seated on T_land by ray casts (no float, burial <= 1 pt).
 2. Two new workers (Meshy 7.1 / T2, prepared offline by meshy/prep_figures.py into assets/fig_*.npz):
    C2_pourer tilts a terracotta jar over the rim, C2_mixer works the paste with an iron-bladed hoe (C2_hoe).
    Standing height = PEOPLE_RATIO x median height of the ruin observers (C5_researchers).
 3. C2_water: the water stream from the jar mouth to the paste + the wet patch where it lands (base_water_process).
 4. C2_heat0~2: heat marks (copies of the D2 heat mark meshes, base_hot_mixing, 81_NOSHADOW) rising from the wet patch.
 5. D2_heat0~2: moved from the ② platform / field corner to just above the dice top face (concept: lime + water -> heat).
 6. D2 dice: irregular lime grains of varied size (<= 10 % of the cube edge), seated on T_land.
 7. S_lead_dot2: leader dot scaled about its centre so it covers <= 25 % of grain D2_lime04.
Run: Blender -b <in.blend> --factory-startup --python step.py -- <out.blend> [render_prefix]
Idempotent: first run stores the original C2/D2/leader meshes (fake-user copies WB_orig_*) and transforms in the scene
marker; a rerun restores them, deletes the created objects and recomputes (same result).
"""
import bpy, bmesh, sys, json, math, hashlib, os, time, runpy
import numpy as np
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

NB = Path('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work')
sys.path.insert(0, str(NB / 'workers' / 'layout'))
from common import Screen, need, bvh_of  # noqa: E402

ASSETS = NB / 'workers' / 'WB' / 'assets'
OUT_DIR = (NB / 'out').resolve()
MARK = 'rc_wb_v8_14'
T0 = time.time()

# ---------------------------------------------------------------- parameters
P = dict(
    C2_FLAT=0.32,                 # z scale of the C2 mesh (platform + pit + paste), about its base
    C2_PLAN=1.0,                  # x/y scale of the C2 mesh about the pit centre
    C2_SHIFT_PT=(0.0, 0.0),     # screen move of the scene (pt), done as a ground translation
    C2_EMBED=0.01,                # world: bottom ring sinks this far below the ground at its least-buried point
    PEOPLE_RATIO=1.18,            # standing height / median ruin-observer height (C5)
    POURER_ANG=210.0,             # deg, world azimuth of the pourer around the pit centre (from +x, ccw)
    POURER_GAP=0.08,              # world, toes clearance outside the pit wall
    MIXER_ANG=100.0,
    MIXER_GAP=0.0,
    MIXER_TURN=0.0,               # deg, extra yaw of the mixer away from facing the centre
    WATER_R0=0.10, WATER_R1=0.115, WATER_FWD=0.35,  # world radii of the stream (top, bottom)
    PUDDLE_R=0.50,
    HEAT_C2_H_PT=9.5, HEAT_C2_DX_PT=(2.0, 5.5, 9.0), HEAT_C2_LIFT_PT=0.6,
    HEAT_D2_H_PT=14.0, HEAT_D2_X_PT=(77.0, 85.0, 93.0), HEAT_D2_GAP_PT=2.0,
    HOE_R=0.068, BLADE_W=0.56, BLADE_H=0.36, BLADE_T=0.05,
    LEAD_DOT_SCALE=0.62,
    BIT_Z=0.45,                   # world z (before flattening) above which stone faces glued to the old workers go
    GRAIN_D=dict(top=[0.40, 0.18, 0.33, 0.14, 0.27, 0.38], px=[0.15, 0.40, 0.31, 0.21, 0.37], ny=[0.40, 0.15, 0.30, 0.20, 0.36]),
)
for k in list(P):
    if os.environ.get('WB_' + k):
        P[k] = json.loads(os.environ['WB_' + k])

TOK = {   # new C2-only tokens (sRGB hex); report lists them for the palette registry
    'RC.v12.c2_tunic': '#9C927C',       # PEOPLE clothes (critic OBJ_COLOR-21 value)
    'RC.v12.c2_terracotta': '#9C5C43',  # TERRA: fired-clay jar
    'RC.v12.c2_iron': '#4F4B45',        # IRON: hoe blade
    'RC.v12.c2_darkwood': '#6B5038',    # WOOD: hoe handle (dL* >= 15 against the paste)
}
OLD_PEOPLE = ('RC.v12.skin', 'RC.v12.linen', 'RC.v12.cloth', 'RC.v12.toolwood')
NEW_OBJS = ['C2_pourer', 'C2_mixer', 'C2_hoe', 'C2_water', 'C2_heat0', 'C2_heat1', 'C2_heat2']
LIMES = [f'D2_lime{i:02d}' for i in range(16)]
OWNED = ['C2_hot_mixing', 'D2_making', 'D2_cube', 'D2_heat0', 'D2_heat1', 'D2_heat2', 'S_lead02', 'S_lead_dot2'] + LIMES

# ---------------------------------------------------------------- arguments / output protection
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
if not argv:
    raise SystemExit('usage: blender -b <in.blend> --factory-startup --python step.py -- <out.blend> [render_prefix]')
SRC = Path(bpy.data.filepath).resolve()
OUT = Path(argv[0]).resolve()
PREFIX = Path(argv[1]).resolve() if len(argv) > 1 else None
if OUT.suffix != '.blend' or OUT == SRC or (OUT.parent == OUT_DIR and OUT.exists()) or \
        (OUT.parent == OUT_DIR and any(p.name == OUT.name for p in OUT_DIR.glob('*.blend*'))):
    raise SystemExit(f'refusing to write {OUT} (input file, existing out/ file, or not .blend)')
if 'Mobile Documents' in str(OUT) or str(OUT).startswith(str(Path.home() / 'Documents')):
    raise SystemExit(f'refusing to write into the iCloud Documents tree: {OUT}')
bpy.context.preferences.filepaths.save_version = 0
sc = bpy.context.scene
O = bpy.data.objects
report = {'step': 'WB_v8_14', 'input': str(SRC), 'output': str(OUT), 'params': P}


def r_(v, n=3):
    return [round(float(x), n) for x in v] if hasattr(v, '__len__') else round(float(v), n)


def srgb_lin(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]


# ---------------------------------------------------------------- fingerprints
def mesh_fp(me):
    h = hashlib.sha256()
    for label, coll, field, width, dt in (('v', me.vertices, 'co', 3, np.float32), ('e', me.edges, 'vertices', 2, np.int32),
                                          ('l', me.loops, 'vertex_index', 1, np.int32),
                                          ('ps', me.polygons, 'loop_start', 1, np.int32),
                                          ('pm', me.polygons, 'material_index', 1, np.int32)):
        a = np.empty(len(coll) * width, dt); coll.foreach_get(field, a)
        h.update(label.encode()); h.update(str(len(coll)).encode()); h.update(a.tobytes())
    return h.hexdigest()[:16]


def mat_fp(m):
    if m is None:
        return None
    vals = [list(m.diffuse_color)]
    if m.node_tree:
        for n in m.node_tree.nodes:
            for i in n.inputs:
                if hasattr(i, 'default_value'):
                    try:
                        vals.append(list(i.default_value))
                    except TypeError:
                        vals.append(i.default_value)
    return hashlib.sha256(json.dumps(vals, default=str).encode()).hexdigest()[:12]


def object_fp(o):
    h = hashlib.sha256()
    h.update(np.array(o.matrix_world, np.float64).round(6).tobytes())
    h.update(json.dumps([o.hide_render, o.hide_viewport, [c.name for c in o.users_collection],
                         [(s.material.name, mat_fp(s.material)) if s.material else None for s in o.material_slots],
                         o.data.name if o.data else None, o.parent.name if o.parent else None]).encode())
    if o.type == 'MESH':
        h.update(mesh_fp(o.data).encode())
    return h.hexdigest()[:16]


def scene_fp(skip):
    return {o.name: object_fp(o) for o in sorted(O, key=lambda x: x.name) if o.name not in skip}


# ---------------------------------------------------------------- idempotency: restore originals
def trs(o):
    return [list(o.location), list(o.rotation_euler), list(o.scale)]


prev = json.loads(sc[MARK]) if sc.get(MARK) else None
if prev is not None:
    for n in NEW_OBJS:
        o = O.get(n)
        if o is not None:
            d = o.data; bpy.data.objects.remove(o, do_unlink=True)
            if d is not None and d.users == 0:
                bpy.data.meshes.remove(d)
    for n, (loc, rot, scl) in prev['trs'].items():
        o = need(n); o.location, o.rotation_euler, o.scale = loc, rot, scl
    for n, mn in prev['meshes'].items():
        o = need(n); cur = o.data
        o.data = bpy.data.meshes[mn].copy(); o.data.name = prev['mesh_names'][n]
        if cur.users == 0:
            bpy.data.meshes.remove(cur)
        o.data.name = prev['mesh_names'][n]
    c2 = need('C2_hot_mixing')
    c2.data.materials.clear()
    for mn in prev['c2_slots']:
        c2.data.materials.append(bpy.data.materials[mn])
    bpy.context.view_layer.update()
    report['rerun'] = 'marker found: originals restored, everything recomputed'
else:
    store = {'trs': {}, 'meshes': {}, 'mesh_names': {}}
    for n in OWNED:
        o = need(n); store['trs'][n] = trs(o)
    for n in ['C2_hot_mixing', 'S_lead_dot2'] + LIMES:
        o = need(n); cp = o.data.copy(); cp.name = 'WB_orig_' + n; cp.use_fake_user = True
        store['meshes'][n] = cp.name; store['mesh_names'][n] = o.data.name
    store['c2_slots'] = [s.material.name for s in need('C2_hot_mixing').material_slots]
    prev = store
FP_BEFORE = scene_fp(set(OWNED) | set(NEW_OBJS))

# ---------------------------------------------------------------- materials
MAT = {}
base_mat = bpy.data.materials['RC.v12.linen']
for name, hx in TOK.items():
    m = bpy.data.materials.get(name)
    if m is None:
        m = base_mat.copy(); m.name = name
    lin = srgb_lin(hx)
    m.diffuse_color = (*lin, 1.0)
    if m.node_tree:
        b = next((nd for nd in m.node_tree.nodes if nd.type == 'BSDF_PRINCIPLED'), None)
        if b is not None:
            b.inputs['Base Color'].default_value = (*lin, 1.0)
    MAT[name] = m
for n in ['RC.v12.skin', 'RC.v12.cloth', 'RC.v12.roman_stone', 'RC.v12.basin', 'RC.v12.base_lime_specimen_matrix',
          'RC.v12.base_water_process', 'RC.v12.base_hot_mixing']:
    MAT[n] = bpy.data.materials[n]

S = Screen()
LAND = need('T_land')
land_bvh, _ = bvh_of([LAND])


def ground_z(x, y):
    h = land_bvh.ray_cast(Vector((x, y, 500)), Vector((0, 0, -1)))[0]
    if h is None:
        raise RuntimeError(f'no ground under ({x:.2f}, {y:.2f})')
    return h.z


def pt(p):
    return S.project(np.array([p], float))[0]


# ground translation per screen pt (local linearisation at a point)
def ground_shift_for(p, dpt):
    J = np.array([pt(p + np.array((1.0, 0, 0))) - pt(p), pt(p + np.array((0, 1.0, 0))) - pt(p)]).T   # 2x2
    d = np.linalg.solve(J, np.array(dpt, float))
    return np.array((d[0], d[1], 0.0))


# ---------------------------------------------------------------- 1. C2 platform / pit / paste
C2 = need('C2_hot_mixing')
me = C2.data
slot_names = [s.material.name for s in C2.material_slots]
bm = bmesh.new(); bm.from_mesh(me)
bm.faces.ensure_lookup_table()
Mw = np.array(C2.matrix_world)
def wpt(c):
    return Mw[:3, :3] @ np.array(c) + Mw[:3, 3]
# old workers = people-material faces, plus stone-coloured bits glued to them (sandals, patches): stone faces that
# share a vertex position with a worker face or chain to one, lie wholly above BIT_Z (platform + rocks stay) and lie within
# 0.35 world (xy) of a worker vertex. The pit (basin, paste) is never touched.
people_f = [f for f in bm.faces if slot_names[f.material_index] in OLD_PEOPLE]
pv = [v.co.copy() for f in people_f for v in f.verts]
from mathutils.kdtree import KDTree
kd3 = KDTree(len(pv))
for i, c in enumerate(pv): kd3.insert(c, i)
kd3.balance()
kd2 = KDTree(len(pv))
for i, c in enumerate(pv):
    w = wpt(c); kd2.insert((w[0], w[1], 0.0), i)
kd2.balance()
key = lambda c: (round(c.x, 5), round(c.y, 5), round(c.z, 5))
vf = {}
others = [f for f in bm.faces if slot_names[f.material_index] not in OLD_PEOPLE]
for f in others:
    for v in f.verts:
        vf.setdefault(key(v.co), []).append(f.index)
def stone_bit(f):
    if slot_names[f.material_index] != 'RC.v12.roman_stone':
        return False
    if min(wpt(v.co)[2] for v in f.verts) < P['BIT_Z']:
        return False
    c = wpt(f.calc_center_median())
    return kd2.find((c[0], c[1], 0.0))[2] < 0.35
seed = [f.index for f in others if any(kd3.find(v.co)[2] < 1e-4 for v in f.verts)]
bits = set(); stack = list(seed)
while stack:
    i = stack.pop()
    if i in bits:
        continue
    f = bm.faces[i]
    if not stone_bit(f):
        continue
    bits.add(i)
    for v in f.verts:
        for j in vf[key(v.co)]:
            if j not in bits:
                stack.append(j)
n_del = len(people_f); removed_bits = len(bits)
bmesh.ops.delete(bm, geom=people_f + [bm.faces[i] for i in bits], context='FACES')
bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
# flatten
for v in bm.verts:
    v.co.z *= P['C2_FLAT']
# paste -> Roman concrete token; drop unused slots
keep = [n for n in slot_names if n not in OLD_PEOPLE and n != 'RC.v12.mixture'] + ['RC.v12.base_lime_specimen_matrix']
remap = {}
for i, n in enumerate(slot_names):
    if n == 'RC.v12.mixture':
        remap[i] = keep.index('RC.v12.base_lime_specimen_matrix')
    elif n in keep:
        remap[i] = keep.index(n)
for f in bm.faces:
    f.material_index = remap[f.material_index]
# plan scale about the pit centre (local)
basin_i = keep.index('RC.v12.basin')
bc = np.array([0.0, 0.0])
bv = [v for f in bm.faces if f.material_index == basin_i for v in f.verts]
bc = np.mean([[v.co.x, v.co.y] for v in bv], axis=0)
for v in bm.verts:
    v.co.x = bc[0] + (v.co.x - bc[0]) * P['C2_PLAN']; v.co.y = bc[1] + (v.co.y - bc[1]) * P['C2_PLAN']
me.materials.clear()
for n in keep:
    me.materials.append(bpy.data.materials[n])
bm.to_mesh(me); bm.free(); me.update()
# move on the ground (screen shift), then seat on T_land
pc = np.array(C2.matrix_world @ Vector((bc[0], bc[1], 0.0)))
d = ground_shift_for(pc, P['C2_SHIFT_PT'])
C2.location = Vector(np.array(C2.location) + d)
bpy.context.view_layer.update()
Mw = np.array(C2.matrix_world)
V = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', V); V = V.reshape(-1, 3)
Wv = V @ Mw[:3, :3].T + Mw[:3, 3]
zmin = Wv[:, 2].min()
ring = Wv[Wv[:, 2] < zmin + 0.02]
ring = ring[np.linspace(0, len(ring) - 1, min(len(ring), 600)).astype(int)]
gz = np.array([ground_z(x, y) for x, y, _ in ring])
# seat: every sample of the bottom ring at or below the ground (lowest-relative point touches, minus C2_EMBED)
dz = float((gz - ring[:, 2]).min()) - P['C2_EMBED']
C2.location.z += dz
bpy.context.view_layer.update()
Mw = np.array(C2.matrix_world)
Wv = V @ Mw[:3, :3].T + Mw[:3, 3]
gap = ring[:, 2] + dz - gz
report['c2'] = {'deleted_people_faces': n_del, 'removed_stone_bits_on_workers': removed_bits, 'slots': keep,
                'ground_move_world': r_(d), 'seat_dz': round(float(dz), 4),
                'bottom_ring_minus_ground_min_max': [round(float(gap.min()), 4), round(float(gap.max()), 4)]}
c2_bvh = BVHTree.FromPolygons([Vector(p) for p in Wv], [list(p.vertices) for p in me.polygons])
PM = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', PM)
CEN = np.empty(len(me.polygons) * 3); me.polygons.foreach_get('center', CEN); CEN = CEN.reshape(-1, 3) @ Mw[:3, :3].T + Mw[:3, 3]
basin_w = CEN[PM == basin_i]
paste_i = keep.index('RC.v12.base_lime_specimen_matrix')
paste_w = CEN[PM == paste_i]
PIT_C = np.array((basin_w[:, 0].mean(), basin_w[:, 1].mean()))
rb = np.linalg.norm(basin_w[:, :2] - PIT_C, axis=1)
R_OUT = float(np.percentile(rb, 98)); R_IN = float(np.percentile(np.linalg.norm(paste_w[:, :2] - PIT_C, axis=1), 97))
stone_i = keep.index('RC.v12.roman_stone')
R_PLAT = float(np.percentile(np.linalg.norm(CEN[PM == stone_i][:, :2] - PIT_C, axis=1), 99))
report['c2']['pit'] = {'centre': r_(PIT_C), 'r_paste': round(R_IN, 3), 'r_wall_out': round(R_OUT, 3), 'r_platform': round(R_PLAT, 3),
                       'rim_top_z': round(float(basin_w[:, 2].max()), 3), 'paste_z_max': round(float(paste_w[:, 2].max()), 3)}


def surf_z(x, y, top=60.0):
    h = c2_bvh.ray_cast(Vector((x, y, top)), Vector((0, 0, -1)))
    return (h[0].z, h[2]) if h[0] is not None else (None, None)


def face_mat(idx):
    return keep[PM[idx]]


# ---------------------------------------------------------------- 2. people
def c5_height():
    c5 = need('C5_researchers'); m5 = c5.data
    mats = [s.material.name if s.material else '' for s in c5.material_slots]
    W5 = np.empty(len(m5.vertices) * 3); m5.vertices.foreach_get('co', W5); W5 = W5.reshape(-1, 3)
    M5 = np.array(c5.matrix_world); W5 = W5 @ M5[:3, :3].T + M5[:3, 3]
    vi = set()
    for p in m5.polygons:
        if mats[p.material_index] in ('RC.v12.skin', 'RC.v12.linen', 'RC.v12.cloth'):
            vi.update(p.vertices)
    Pp = W5[sorted(vi)]
    cell = 0.25; keys = {}
    for i, (x, y, z) in enumerate(Pp):
        keys.setdefault((int(math.floor(x / cell)), int(math.floor(y / cell))), []).append(i)
    lab = {}; cur = 0
    for k in sorted(keys):
        if k in lab: continue
        st = [k]; lab[k] = cur
        while st:
            a = st.pop()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    b = (a[0] + dx, a[1] + dy)
                    if b in keys and b not in lab:
                        lab[b] = cur; st.append(b)
        cur += 1
    hs = []
    for c in range(cur):
        idx = [i for k, v in keys.items() if lab[k] == c for i in v]
        if len(idx) >= 200:
            Q = Pp[idx]; hs.append(float(Q[:, 2].max() - Q[:, 2].min()))
    return float(np.median(hs)), hs


H5, H5_all = c5_height()
H_STAND = P['PEOPLE_RATIO'] * H5
report['people'] = {'c5_heights': r_(H5_all), 'c5_median': round(H5, 3), 'c2_standing_height': round(H_STAND, 3)}


def make_mesh_obj(name, V, F, mats_list, M_idx, coll_name):
    me_ = bpy.data.meshes.new(name)
    me_.from_pydata([tuple(v) for v in V], [], [tuple(int(i) for i in f) for f in F])
    me_.update()
    for m in mats_list:
        me_.materials.append(m)
    me_.polygons.foreach_set('material_index', np.asarray(M_idx, np.int32))
    for p in me_.polygons:
        p.use_smooth = True
    me_.update()
    ob = bpy.data.objects.new(name, me_)
    bpy.data.collections[coll_name].objects.link(ob)
    return ob


def figure(name, npz, stand_h_model, ang_deg, gap, turn_deg=0.0):
    D = np.load(npz)
    Vm = D['V'].astype(np.float64); s = H_STAND / stand_h_model
    u = np.array((math.cos(math.radians(ang_deg)), math.sin(math.radians(ang_deg))))     # pit centre -> worker
    # facing = -u (toward the centre): model faces -Y, so yaw theta with (sin, -cos) = -u
    th = math.atan2(-u[0], u[1]) + math.radians(turn_deg)
    R = np.array(Matrix.Rotation(th, 3, 'Z'))
    Vr = (Vm * s) @ R.T
    # toes reach (largest extent toward the centre) -> stand so that toes are GAP outside the wall
    fw = -u
    feet = Vr[Vm[:, 2] < 0.08 * Vm[:, 2].max()]
    toe = float((feet[:, :2] @ fw).max())
    r_feet = R_OUT + gap + toe
    xy = PIT_C + u * r_feet
    zs = [surf_z(xy[0] + dx, xy[1] + dy)[0] for dx, dy in ((0, 0), (0.15, 0), (-0.15, 0), (0, 0.15), (0, -0.15))]
    zs = [z for z in zs if z is not None]
    z = max(zs) - 0.01
    T = np.array((xy[0], xy[1], z))
    Wf = Vr + T
    cls_mat = [MAT['RC.v12.skin'], MAT['RC.v12.c2_tunic'], MAT['RC.v12.cloth'], MAT['RC.v12.cloth'], MAT['RC.v12.c2_terracotta']]
    ob = make_mesh_obj(name, Wf, D['F'], cls_mat, D['M'].astype(np.int32), '45_CORE_SCENES')
    info = {'scale': round(s, 4), 'yaw_deg': round(math.degrees(th), 2), 'feet_xy': r_(xy), 'feet_z': round(z, 3),
            'r_feet': round(r_feet, 3), 'posed_height': round(float(Wf[:, 2].max() - z), 3)}
    xf = lambda p: (np.asarray(p, float) * s) @ R.T + T
    return ob, xf, R, info, D


pour, pxf, pR, pinfo, PD = figure('C2_pourer', ASSETS / 'fig_pourer.npz', 1.9026, P['POURER_ANG'], P['POURER_GAP'])
mix, mxf, mR, minfo, MD = figure('C2_mixer', ASSETS / 'fig_mixer.npz', 1.03, P['MIXER_ANG'], P['MIXER_GAP'], P['MIXER_TURN'])
report['people']['pourer'] = pinfo; report['people']['mixer'] = minfo

# ---------------------------------------------------------------- 3. water: stream + wet patch
MOUTH = pxf(PD['mouth'])
AX = pR @ np.asarray(PD['axis'], float)
hdir = np.array((AX[0], AX[1], 0.0)); hdir /= np.linalg.norm(hdir)
# landing: straight below a point a little ahead of the mouth
fwd = P['WATER_FWD']
lx, ly = MOUTH[0] + hdir[0] * fwd, MOUTH[1] + hdir[1] * fwd
lz, lf = surf_z(lx, ly, top=float(MOUTH[2]) - 0.05)
if lz is None or np.linalg.norm(np.array((lx, ly)) - PIT_C) > R_IN + 0.05:
    print('DEBUG', json.dumps(report, default=float), 'mouth', MOUTH.tolist(), 'r_mouth', float(np.linalg.norm(MOUTH[:2] - PIT_C)), 'land', lx, ly, lz)
    raise RuntimeError(f'water would not land on the paste (hit {face_mat(lf) if lf is not None else None})')
LAND_P = np.array((lx, ly, lz))
ctrl = MOUTH + hdir * fwd * 1.05 + np.array((0, 0, 0.02))
def bez(t):
    return (1 - t) ** 2 * MOUTH + 2 * (1 - t) * t * ctrl + t * t * LAND_P
NR, NS = 20, 10
ring_pts = []
verts = []; faces = []
for i in range(NR + 1):
    t = i / NR; c = bez(t)
    tan = 2 * (1 - t) * (ctrl - MOUTH) + 2 * t * (LAND_P - ctrl); tan /= np.linalg.norm(tan)
    a = np.cross(tan, (0, 0, 1.0)) if abs(tan[2]) < 0.99 else np.array((1.0, 0, 0)); a /= np.linalg.norm(a)
    b = np.cross(tan, a)
    r = P['WATER_R0'] + (P['WATER_R1'] - P['WATER_R0']) * t
    for j in range(NS):
        ph = 2 * math.pi * j / NS
        verts.append(c + r * (math.cos(ph) * a + math.sin(ph) * b))
for i in range(NR):
    for j in range(NS):
        a0 = i * NS + j; a1 = i * NS + (j + 1) % NS
        faces.append((a0, a1, a1 + NS, a0 + NS))
top_c = len(verts); verts.append(MOUTH.copy()); faces += [(top_c, (j + 1) % NS, j) for j in range(NS)]
# wet patch: disc conforming to the paste around the landing point
base = len(verts); NRING, NSEG = 5, 24
verts.append(np.array((lx, ly, lz + 0.03)))
for k in range(1, NRING + 1):
    rr = P['PUDDLE_R'] * k / NRING
    for j in range(NSEG):
        ph = 2 * math.pi * j / NSEG
        x = lx + rr * math.cos(ph) * 1.0; y = ly + rr * math.sin(ph) * 0.8
        z_, _ = surf_z(x, y, top=float(lz) + 1.5)
        verts.append(np.array((x, y, (z_ if z_ is not None else lz) + 0.03)))
for j in range(NSEG):
    faces.append((base, base + 1 + j, base + 1 + (j + 1) % NSEG))
for k in range(1, NRING):
    r0 = base + 1 + (k - 1) * NSEG; r1 = base + 1 + k * NSEG
    for j in range(NSEG):
        faces.append((r0 + j, r1 + j, r1 + (j + 1) % NSEG, r0 + (j + 1) % NSEG))
water = make_mesh_obj('C2_water', np.array(verts), faces, [MAT['RC.v12.base_water_process']], [0] * len(faces), '45_CORE_SCENES')
report['water'] = {'landing_material': face_mat(lf), 'mouth': r_(MOUTH), 'landing': r_(LAND_P), 'drop_world': round(float(MOUTH[2] - lz), 3),
                   'mouth_pt': r_(pt(MOUTH), 2), 'landing_pt': r_(pt(LAND_P), 2),
                   'stream_len_pt': round(float(sum(np.linalg.norm(pt(bez((i + 1) / 20)) - pt(bez(i / 20))) for i in range(20))), 2)}

# ---------------------------------------------------------------- hoe
HT = mxf(MD['handle_top']); HD = mR @ np.asarray(MD['handle_dir'], float); HD /= np.linalg.norm(HD)
hit = c2_bvh.ray_cast(Vector(HT), Vector(HD))
if hit[0] is None or np.linalg.norm(np.array(hit[0])[:2] - PIT_C) > R_IN + 0.05:
    print('DEBUG hoe', 'HT', HT.tolist(), 'r_HT', float(np.linalg.norm(HT[:2] - PIT_C)), 'HD', HD.tolist(), 'hit', list(hit[0]) if hit[0] else None,
          'r_hit', float(np.linalg.norm(np.array(hit[0])[:2] - PIT_C)) if hit[0] else None, json.dumps(report['people'], default=float), json.dumps(report['c2']['pit']))
    raise RuntimeError(f'hoe line does not reach the paste (hit {face_mat(hit[2]) if hit[0] is not None else None})')
BL = np.array(hit[0])
h0 = HT - HD * 0.12
L = float(np.linalg.norm(BL - h0))
def cyl(p0, p1, r, nseg=10):
    ax_ = p1 - p0; ln = np.linalg.norm(ax_); ax_ /= ln
    a = np.cross(ax_, (0, 0, 1.0)); a /= np.linalg.norm(a); b = np.cross(ax_, a)
    vs = []; fs = []
    for k, c in enumerate((p0, p1)):
        for j in range(nseg):
            ph = 2 * math.pi * j / nseg; vs.append(c + r * (math.cos(ph) * a + math.sin(ph) * b))
    for j in range(nseg):
        fs.append((j, (j + 1) % nseg, nseg + (j + 1) % nseg, nseg + j))
    fs.append(tuple(range(nseg - 1, -1, -1))); fs.append(tuple(range(nseg, 2 * nseg)))
    return vs, fs
hv, hf = cyl(h0, BL - HD * 0.02, P['HOE_R'])
# blade: plate perpendicular to the handle, across = horizontal perpendicular to the handle's horizontal heading
hh = np.array((HD[0], HD[1], 0.0)); hh /= np.linalg.norm(hh)
across = np.array((-hh[1], hh[0], 0.0))
up_b = np.cross(across, HD); up_b /= np.linalg.norm(up_b)
if up_b[2] < 0: up_b = -up_b
bc_ = BL + up_b * (P['BLADE_H'] * 0.5 - 0.06)
bvs = []; bfs = []
for sx in (-1, 1):
    for sy in (-1, 1):
        for sz in (-1, 1):
            bvs.append(bc_ + across * sx * P['BLADE_W'] / 2 + up_b * sy * P['BLADE_H'] / 2 + HD * sz * P['BLADE_T'] / 2)
bfs = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 2, 6, 4), (1, 5, 7, 3), (0, 4, 5, 1), (2, 3, 7, 6)]
off = len(hv)
hoe = make_mesh_obj('C2_hoe', np.array(hv + bvs), hf + [tuple(i + off for i in f) for f in bfs],
                    [MAT['RC.v12.c2_darkwood'], MAT['RC.v12.c2_iron']], [0] * len(hf) + [1] * len(bfs), '45_CORE_SCENES')
for p_ in hoe.data.polygons:
    p_.use_smooth = False
report['hoe'] = {'hit_material': face_mat(hit[2]), 'top': r_(h0), 'blade_centre': r_(bc_), 'length': round(L, 3), 'blade_pt': r_(pt(bc_), 2)}

# ---------------------------------------------------------------- heat marks (screen-designed, overlay pass)
HEAT_SRC = [need(f'D2_heat{i}') for i in range(3)]
cam = sc.camera
cam_right = np.array(cam.matrix_world.col[0].xyz.normalized())
cam_back = np.array(cam.matrix_world.col[2].xyz.normalized())      # from scene toward the camera
cr = np.array((cam_right[0], cam_right[1], 0.0)); cr /= np.linalg.norm(cr)
cn = np.array((cam_back[0], cam_back[1], 0.0)); cn /= np.linalg.norm(cn)


def heat_local(src):
    v = np.empty(len(src.data.vertices) * 3); src.data.vertices.foreach_get('co', v); v = v.reshape(-1, 3)
    return v


def ray_plane_z(pt_xy, zp):
    o_, dvec = S.ray(pt_xy)
    o_ = np.array(o_); dvec = np.array(dvec)
    t = (zp - o_[2]) / dvec[2]
    return o_ + t * dvec


def heat_matrix(src_local, bottom_pt, h_pt, zp):
    """world matrix for a heat mark mesh (local verts) so its bottom centre projects to bottom_pt and it is h_pt tall,
    upright on screen (camera is shift-lens: world verticals stay vertical) and facing the camera."""
    lo = src_local
    ext = lo.max(0) - lo.min(0)
    up_i = int(np.argmax(ext)); thin_i = int(np.argmin(ext)); wid_i = 3 - up_i - thin_i
    bot = np.array([(lo[:, k].min() + lo[:, k].max()) / 2 for k in range(3)]); bot[up_i] = lo[:, up_i].min()
    W0 = ray_plane_z(bottom_pt, zp)
    s_w = h_pt / (pt(W0 + np.array((0, 0, 1.0)))[1] * -1 + pt(W0)[1])        # world per local height unit
    s_w = h_pt / abs(pt(W0)[1] - pt(W0 + np.array((0, 0, 1.0)))[1]) / ext[up_i]
    B = np.zeros((3, 3)); B[:, up_i] = (0, 0, 1.0); B[:, wid_i] = cr; B[:, thin_i] = cn
    if np.linalg.det(B) < 0: B[:, thin_i] = -cn
    M = np.eye(4); M[:3, :3] = B * s_w; M[:3, 3] = W0 - (B * s_w) @ bot
    return Matrix(M.tolist())


wet_pt = pt(LAND_P)
c2_heats = []
for i, dx in enumerate(P['HEAT_C2_DX_PT']):
    src = HEAT_SRC[i]
    me_h = src.data.copy(); me_h.name = f'C2_heat{i}'
    ob = bpy.data.objects.new(f'C2_heat{i}', me_h)
    bpy.data.collections['81_NOSHADOW'].objects.link(ob)
    ob.matrix_world = heat_matrix(heat_local(src), (wet_pt[0] + dx, wet_pt[1] - P['HEAT_C2_LIFT_PT']), P['HEAT_C2_H_PT'], float(LAND_P[2]))
    c2_heats.append(ob)

# ---------------------------------------------------------------- D2 dice: seat, grains, heat marks
DM = need('D2_making'); CUBE = need('D2_cube')
bpy.context.view_layer.update()
Mc = np.array(CUBE.matrix_world)
cv = np.empty(len(CUBE.data.vertices) * 3); CUBE.data.vertices.foreach_get('co', cv); cv = cv.reshape(-1, 3) @ Mc[:3, :3].T + Mc[:3, 3]
zb = cv[:, 2].min()
xs = np.linspace(cv[:, 0].min() + 0.05, cv[:, 0].max() - 0.05, 9); ys = np.linspace(cv[:, 1].min() + 0.05, cv[:, 1].max() - 0.05, 9)
gzc = np.array([ground_z(x, y) for x in xs for y in ys])
dz_d2 = float(gzc.max() - zb) - 0.004          # bottom 0.004 below the highest ground point under it
DM.location.z += dz_d2
bpy.context.view_layer.update()
report['d2'] = {'seat_dz': round(dz_d2, 4), 'ground_range_under_cube': round(float(gzc.max() - gzc.min()), 4)}
# grains: irregular lumps, sizes per face (world diameter), centres kept
EDGE = float(cv[:, 0].max() - cv[:, 0].min())
faces_of = {'top': [0, 3, 6, 9, 12, 15], 'px': [1, 4, 7, 10, 13], 'ny': [2, 5, 8, 11, 14]}
grain_rep = {}
for face, ids in faces_of.items():
    for k, gi in enumerate(ids):
        o = need(f'D2_lime{gi:02d}')
        dia = P['GRAIN_D'][face][k]
        ws = np.array(o.matrix_world.to_scale())
        bmg = bmesh.new()
        bmesh.ops.create_icosphere(bmg, subdivisions=3, radius=1.0)
        rng = np.random.default_rng(1000 + gi)
        lobes = rng.normal(size=(4, 3)); lobes /= np.linalg.norm(lobes, axis=1)[:, None]
        amp = rng.uniform(0.10, 0.20, 4)
        el = 1.0 + rng.uniform(0.15, 0.35)
        for v in bmg.verts:
            n = np.array(v.co)
            f = 1.0 + sum(a * max(0.0, float(n @ l)) ** 3 for a, l in zip(amp, lobes)) - 0.10 * float(np.sin(3 * n[0] + 2 * n[1]) * np.cos(2 * n[2]))
            p = n * f; p[0] *= el
            v.co = Vector(p)
        # scale so the largest world extent equals dia
        co = np.array([v.co for v in bmg.verts]) * ws
        ext = (co.max(0) - co.min(0)).max()
        sfac = dia / ext
        cen_l = (np.array([v.co for v in bmg.verts]).max(0) + np.array([v.co for v in bmg.verts]).min(0)) / 2
        for v in bmg.verts:
            v.co = Vector((np.array(v.co) - cen_l) * sfac)
        bmg.to_mesh(o.data); bmg.free(); o.data.update()
        grain_rep[o.name] = round(dia, 3)
report['d2']['grain_diameters'] = grain_rep
report['d2']['cube_edge'] = round(EDGE, 3)
# heat marks above the dice top face (screen design): bottom just above the back edges
bpy.context.view_layer.update()
Mc = np.array(CUBE.matrix_world)
cv = np.empty(len(CUBE.data.vertices) * 3); CUBE.data.vertices.foreach_get('co', cv); cv = cv.reshape(-1, 3) @ Mc[:3, :3].T + Mc[:3, 3]
ztop = float(cv[:, 2].max())
top_c = cv[cv[:, 2] > ztop - 1e-4]
tp = S.project(top_c)                       # 4 corners of the top face on screen
back = tp[np.argsort(tp[:, 1])[:3]]         # top vertex + left + right corners (smallest y = highest on screen)
def back_edge_y(x):
    k = back[np.argsort(back[:, 0])]
    tv = back[np.argmin(back[:, 1])]
    lv = k[0]; rv = k[-1]
    if x <= tv[0]:
        return lv[1] + (tv[1] - lv[1]) * (x - lv[0]) / (tv[0] - lv[0])
    return tv[1] + (rv[1] - tv[1]) * (x - tv[0]) / (rv[0] - tv[0])
d2_rep = []
for i, x in enumerate(P['HEAT_D2_X_PT']):
    o = HEAT_SRC[i]
    o.matrix_world = heat_matrix(heat_local(o), (x, back_edge_y(x) - P['HEAT_D2_GAP_PT']), P['HEAT_D2_H_PT'], ztop)
    d2_rep.append({'x': x, 'bottom_y': round(back_edge_y(x) - P['HEAT_D2_GAP_PT'], 2)})
report['d2']['heat'] = d2_rep

# ---------------------------------------------------------------- leader dot
DOT = need('S_lead_dot2')
dv = np.empty(len(DOT.data.vertices) * 3); DOT.data.vertices.foreach_get('co', dv); dv = dv.reshape(-1, 3)
dc = dv.mean(0)
dv = dc + (dv - dc) * P['LEAD_DOT_SCALE']
DOT.data.vertices.foreach_set('co', dv.ravel()); DOT.data.update()
bpy.context.view_layer.update()
report['leader'] = {'dot_centre_pt': r_(pt(np.array(DOT.matrix_world) [:3, :3] @ dc + np.array(DOT.matrix_world)[:3, 3]), 2),
                    'lime04_centre_pt': r_(pt(np.array(need('D2_lime04').matrix_world.translation)), 2)}

# ---------------------------------------------------------------- invariance + save
FP_AFTER = scene_fp(set(OWNED) | set(NEW_OBJS))
changed = sorted(n for n in FP_AFTER if FP_BEFORE.get(n) != FP_AFTER[n])
added = sorted(set(FP_AFTER) - set(FP_BEFORE)); removed = sorted(set(FP_BEFORE) - set(FP_AFTER))
if changed or added or removed:
    raise RuntimeError(f'objects outside WB ownership changed: changed={changed} added={added} removed={removed}')
missing = [n for n in OWNED + NEW_OBJS if O.get(n) is None]
if missing:
    raise RuntimeError(f'missing owned objects {missing}')
report['invariance'] = {'objects_compared': len(FP_AFTER), 'changed_outside_ownership': 0}
report['new_tokens'] = TOK
sc[MARK] = json.dumps(prev)
report['seconds'] = round(time.time() - T0, 1)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT), copy=True)
report['saved'] = str(OUT)
if PREFIX is not None:
    H = runpy.run_path(str(NB / 'scripts' / 'integrate_assets.py'), run_name='helpers')
    report['render'] = H['render_two_pass'](PREFIX.with_suffix('.png'))
    PREFIX.with_name(PREFIX.name + '_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=1, default=float))
print('REPORT ' + json.dumps(report, ensure_ascii=False, default=float))
