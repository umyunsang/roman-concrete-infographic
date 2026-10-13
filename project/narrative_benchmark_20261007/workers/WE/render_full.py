"""render_full.py - read-only full two-pass render (integrate_assets.render_two_pass) of the open blend.
Blender -b <blend> --factory-startup --python render_full.py -- <prefix> [percent]"""
import bpy, sys, runpy, hashlib, json
from pathlib import Path
HERE = Path(__file__).resolve().parent; NB = HERE.parents[1]
argv = sys.argv[sys.argv.index('--') + 1:]
def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()
h0 = sha(bpy.data.filepath)
H = runpy.run_path(str(NB / 'scripts/integrate_assets.py'), run_name='helpers')
pct = int(argv[1]) if len(argv) > 1 else 48
r = H['render_two_pass'](Path(argv[0]).with_suffix('.png'), pct)
assert sha(bpy.data.filepath) == h0
print('RENDER_FULL ' + json.dumps(r))
