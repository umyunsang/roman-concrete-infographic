"""v8.9: round-6 3D findings — leftover slivers/pegs/volcano strands, section heavy-stone value.

Run: blender -b out/roman_concrete_narrative_v8_8.blend --factory-startup --python scripts/review_r6_fixes_v8_9.py -- <test|final> [test_prefix]
"""
import bpy, bmesh, json, sys, runpy
from pathlib import Path
import numpy as np
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'out/roman_concrete_narrative_v8_8.blend'
OUT = ROOT / 'out/roman_concrete_narrative_v8_9.blend'
argv = sys.argv[sys.argv.index('--') + 1:]
MODE = argv[0]
assert Path(bpy.data.filepath).resolve() == SRC.resolve()
sc = bpy.context.scene; cam = sc.camera; O = bpy.data.objects
report = {}
def to_pt(p):
    v = world_to_camera_view(sc, cam, p); return np.array((v.x * 1191, (1 - v.y) * 1684))
def lin(h):
    return tuple(((int(h[i:i + 2], 16) / 255 + 0.055) / 1.055) ** 2.4 for i in (1, 3, 5))

def drop_islands(obj, boxes, max_faces):
    """delete face-connected islands smaller than max_faces whose screen centroid falls in a box"""
    if obj.data.users > 1: obj.data = obj.data.copy()
    bm = bmesh.new(); bm.from_mesh(obj.data); mw = obj.matrix_world; bm.faces.ensure_lookup_table()
    seen = set(); gone = []
    for f in bm.faces:
        if f.index in seen: continue
        st = [f]; seen.add(f.index); comp = []
        while st:
            a = st.pop(); comp.append(a)
            for e in a.edges:
                for g in e.link_faces:
                    if g.index not in seen: seen.add(g.index); st.append(g)
        if len(comp) < max_faces:
            ps = np.array([to_pt(mw @ x.calc_center_median()) for x in comp])
            cx, cy = ps[:, 0].mean(), ps[:, 1].mean()
            if any(x0 < cx < x1 and y0 < cy < y1 for (x0, x1, y0, y1) in boxes): gone += comp
    bmesh.ops.delete(bm, geom=gone, context='FACES')
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    bm.to_mesh(obj.data); bm.free(); return len(gone)

# 1. leftovers (3D F-01): grey sliver under the CORE 1 slab, 5 bare pegs, strands on Vesuvius' NW outline
report['frame_sliver'] = drop_islands(O['NB_modern_building'], [(744, 753, 535, 547)], 40)
report['pegs'] = drop_islands(O['F_centuriatio'], [(850, 868, 514, 534), (744, 752, 536, 547)], 400)
report['vesuvius_strands'] = drop_islands(O['L07_vesuvius'], [(930, 1000, 1278, 1350)], 300)
# the strands are the scan's ragged fringe on the main mesh: relax the NW outline band
ves = O['L07_vesuvius']
bm = bmesh.new(); bm.from_mesh(ves.data); vmw = ves.matrix_world
band = [v for v in bm.verts if (lambda p: 928 < p[0] < 1002 and 1276 < p[1] < 1352)(to_pt(vmw @ v.co))]
for _ in range(6):
    bmesh.ops.smooth_vert(bm, verts=band, factor=0.6, use_axis_x=True, use_axis_y=True, use_axis_z=True)
bm.to_mesh(ves.data); bm.free()
report['vesuvius_band_verts_smoothed'] = len(band)
# CORE 1 slab: the tiny grey sliver just below its front edge
nb = O['NB_modern_building']
bm = bmesh.new(); bm.from_mesh(nb.data); nmw = nb.matrix_world
gone = [f for f in bm.faces if (lambda p: 745 < p[0] < 751 and 538.5 < p[1] < 545)(to_pt(nmw @ f.calc_center_median()))]
bmesh.ops.delete(bm, geom=gone, context='FACES'); bm.to_mesh(nb.data); bm.free()
report['frame_sliver_faces'] = len(gone)

# 2. section column: heavy stone darker than middle stone, as in the tower (3D F-03)
m = bpy.data.materials.get('RC.v12_9.sect_heavy') or bpy.data.materials['RC.v12.base_road_foundation'].copy()
m.name = 'RC.v12_9.sect_heavy'; m.diffuse_color = (*lin('#726753'), 1)
for s in O['S_sect2'].material_slots: s.material = m

print('REPORT ' + json.dumps(report, ensure_ascii=False))
H = runpy.run_path(str(ROOT / 'scripts/integrate_assets.py'), run_name='helpers')
if MODE == 'test':
    print('RENDER ' + json.dumps(H['render_two_pass'](Path(argv[1]).with_suffix('.png'))))
else:
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT), copy=False)
    r = H['render_two_pass'](ROOT / 'renders/narrative_v8_9_r6.png'); report['render'] = r
    (ROOT / 'out/v8_9-review-r6-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print('RENDER ' + json.dumps(r))
