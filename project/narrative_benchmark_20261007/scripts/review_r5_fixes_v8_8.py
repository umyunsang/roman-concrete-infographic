"""v8.8: apply verified round-5 critic findings to the Blender map.

Run: blender -b out/roman_concrete_narrative_v8_7.blend --factory-startup --python scripts/review_r5_fixes_v8_8.py -- <test|final> [test_prefix]
"""
import bpy, bmesh, math, json, sys, runpy
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'out/roman_concrete_narrative_v8_7.blend'
OUT = ROOT / 'out/roman_concrete_narrative_v8_8.blend'
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
dg = bpy.context.evaluated_depsgraph_get()
T = O['T_land']; ev = T.evaluated_get(dg); tm = ev.to_mesh()
TERRAIN = BVHTree.FromPolygons([T.matrix_world @ v.co for v in tm.vertices], [list(p.vertices) for p in tm.polygons])
def tz(x, y):
    h = TERRAIN.ray_cast(Vector((x, y, 500)), Vector((0, 0, -1)))[0]; return h.z if h else 0.0

# 1. milestone columns read against road and podium (3D I3-13): own darker travertine
ms_mat = new_mat('RC.v12_8.milestone_stone', '#A79375')
for me in {O[n].data for n in ('MS1_core1_to_2', 'MS2_core2_to_34', 'MS3_core34_to_5')}:
    me.materials[0] = ms_mat
report['milestone_column'] = '#A79375'

def drop_faces(obj, boxes, cond=lambda f, w: True):
    if obj.data.users > 1: obj.data = obj.data.copy()
    bm = bmesh.new(); bm.from_mesh(obj.data); mw = obj.matrix_world
    gone = []
    for f in bm.faces:
        w = mw @ f.calc_center_median(); p = to_pt(w)
        if any(x0 < p[0] < x1 and y0 < p[1] < y1 for (x0, x1, y0, y1) in boxes) and cond(f, w): gone.append(f)
    bmesh.ops.delete(bm, geom=gone, context='FACES')
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    bm.to_mesh(obj.data); bm.free(); return len(gone)

# 2. leftovers (3D I3-21): Colosseum sliver on the south podium, bare field pegs beside the CORE 1 frame, stub plate by the pine
report['col_sliver'] = drop_faces(O['COL_ruined'], [(549, 564, 970, 979)], lambda f, w: w.z < tz(w.x, w.y) + 2.0)
report['field_pegs'] = drop_faces(O['F_centuriatio'], [(700, 748, 508, 553), (774, 856, 508, 556), (858, 894, 1345, 1378)])
# the frame model's own ground pegs: small loose islands below its base line
b = O['NB_modern_building']
if b.data.users > 1: b.data = b.data.copy()
bm = bmesh.new(); bm.from_mesh(b.data); mw = b.matrix_world; bm.faces.ensure_lookup_table()
seen = set(); gone = []
for f in bm.faces:
    if f.index in seen: continue
    st = [f]; seen.add(f.index); comp = []
    while st:
        a = st.pop(); comp.append(a)
        for e in a.edges:
            for g in e.link_faces:
                if g.index not in seen: seen.add(g.index); st.append(g)
    if False and len(comp) < 40:  # frame model untouched (its small islands are part of the slab)
        ps = [to_pt(mw @ x.calc_center_median()) for x in comp]
        cx = sum(p[0] for p in ps) / len(ps); cy = sum(p[1] for p in ps) / len(ps)
        if (700 < cx < 750 and 528 < cy < 553) or (774 < cx < 856 and 528 < cy < 556): gone += comp
bmesh.ops.delete(bm, geom=gone, context='FACES')
bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
bm.to_mesh(b.data); bm.free()
report['frame_pegs'] = len(gone)

# 3. lime kiln: smooth clay surface instead of flat facets (3D I3-03 minor)
for p in O['D2_lime_kiln'].data.polygons: p.use_smooth = True

print('REPORT ' + json.dumps(report, ensure_ascii=False))
H = runpy.run_path(str(ROOT / 'scripts/integrate_assets.py'), run_name='helpers')
if MODE == 'test':
    print('RENDER ' + json.dumps(H['render_two_pass'](Path(argv[1]).with_suffix('.png'))))
else:
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT), copy=False)
    r = H['render_two_pass'](ROOT / 'renders/narrative_v8_8_r5.png'); report['render'] = r
    (ROOT / 'out/v8_8-review-r5-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print('RENDER ' + json.dumps(r))
