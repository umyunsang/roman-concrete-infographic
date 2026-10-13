"""Print master render: A2 at 300 ppi with 3 mm bleed on every side (no scene edits are saved).

The design frame (4962x7016 px = 420x594 mm) is kept pixel-identical in scale and position; the canvas grows by
35.5 px (3 mm) per side -> 5033x7087 px. Pixel scale is preserved by lens *= H/H', and the principal-point offset
by shift *= H/H' (Blender shift is a fraction of the larger image side).
Run: blender -b out/<file>.blend --factory-startup --python scripts/render_print_bleed.py -- <tag>
"""
import bpy, runpy, sys, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
tag = sys.argv[sys.argv.index('--') + 1]
sc = bpy.context.scene; cam = sc.camera.data; r = sc.render
W0, H0 = r.resolution_x, r.resolution_y
assert (W0, H0) == (4962, 7016), (W0, H0)
W1, H1 = W0 + 71, H0 + 71
k = H0 / H1
r.resolution_x, r.resolution_y = W1, H1
cam.lens *= k; cam.shift_x *= k; cam.shift_y *= k
H = runpy.run_path(str(ROOT / 'scripts/integrate_assets.py'), run_name='helpers')
res = H['render_two_pass'](ROOT / f'renders/{tag}_print_bleed.png', resolution_percentage=100)
print('RENDER ' + json.dumps(res))
