"""v8.10: round-7 3D minors — detached slivers (Vesuvius NW, Pompeii scaffold) and section heavy-stone step.

Run: blender -b out/roman_concrete_narrative_v8_9.blend --factory-startup --python scripts/review_r7_fixes_v8_10.py -- <test|final> [test_prefix]
"""
import bpy, bmesh, json, sys, runpy
from pathlib import Path
import numpy as np
from bpy_extras.object_utils import world_to_camera_view
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'out/roman_concrete_narrative_v8_9.blend'
OUT = ROOT / 'out/roman_concrete_narrative_v8_10.blend'
argv = sys.argv[sys.argv.index('--') + 1:]
MODE = argv[0]
assert Path(bpy.data.filepath).resolve() == SRC.resolve()
sc = bpy.context.scene; cam = sc.camera; O = bpy.data.objects
report = {}
def to_pt(p):
    v = world_to_camera_view(sc, cam, p); return np.array((v.x * 1191, (1 - v.y) * 1684))
def lin(h):
    return tuple(((int(h[i:i + 2], 16) / 255 + 0.055) / 1.055) ** 2.4 for i in (1, 3, 5))
def drop_faces(obj, box):
    if obj.data.users > 1: obj.data = obj.data.copy()
    bm = bmesh.new(); bm.from_mesh(obj.data); mw = obj.matrix_world
    x0, x1, y0, y1 = box
    gone = [f for f in bm.faces if (lambda p: x0 < p[0] < x1 and y0 < p[1] < y1)(to_pt(mw @ f.calc_center_median()))]
    bmesh.ops.delete(bm, geom=gone, context='FACES')
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    bm.to_mesh(obj.data); bm.free(); return len(gone)
# silhouette starts at x≈1000 on these rows (critic I3-21-a); the sliver lies 3-5pt to its left
# deleting by box notches the flank (tested) -> relax the thin fringe instead
ves = O['L07_vesuvius']
bm = bmesh.new(); bm.from_mesh(ves.data); vmw = ves.matrix_world
band = [v for v in bm.verts if (lambda p: 978 < p[0] < 1004 and 1272 < p[1] < 1296)(to_pt(vmw @ v.co))]
for _ in range(15):
    bmesh.ops.smooth_vert(bm, verts=band, factor=0.7, use_axis_x=True, use_axis_y=True, use_axis_z=True)
bm.to_mesh(ves.data); bm.free()
report['vesuvius_band_smoothed'] = len(band)
report['pompeii_bar'] = drop_faces(O['L08_pompeii_site'], (691, 694.5, 1435, 1440))
m = bpy.data.materials['RC.v12_9.sect_heavy']; m.diffuse_color = (*lin('#897D69'), 1)
print('REPORT ' + json.dumps(report))
H = runpy.run_path(str(ROOT / 'scripts/integrate_assets.py'), run_name='helpers')
if MODE == 'test':
    print('RENDER ' + json.dumps(H['render_two_pass'](Path(argv[1]).with_suffix('.png'))))
else:
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT), copy=False)
    r = H['render_two_pass'](ROOT / 'renders/narrative_v8_10_r7.png'); report['render'] = r
    (ROOT / 'out/v8_10-review-r7-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('RENDER ' + json.dumps(r))
