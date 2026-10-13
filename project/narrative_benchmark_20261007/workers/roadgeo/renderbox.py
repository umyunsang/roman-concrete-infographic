"""renderbox.py - read-only region renders for the roadgeo worker (before/after crops).

Blender -b <in.blend> --factory-startup --python renderbox.py -- <out_dir> <tag> <percent> name:x0,x1,y0,y1 [...]
  boxes in poster points (1191 x 1684, top-left origin). Each box is rendered with the same two-pass split as
  integrate_assets.render_two_pass (map pass with shadows + overlay pass), but only inside the box
  (inventory/render_assets.border_two_pass), at <percent> (48 -> 2 px/pt, 72 -> 3 px/pt, 144 -> 6 px/pt).
  The passes are alpha-composited with Pillow (uv) into <out_dir>/<tag>_<name>_x<px_per_pt>.png.
Never saves the blend (hash checked before/after).
"""
import bpy, sys, json, runpy, hashlib, subprocess, shutil, math
from pathlib import Path

HERE = Path(__file__).resolve().parent
NB = HERE.parents[1]
W_PT, H_PT = 1191, 1684


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


argv = sys.argv[sys.argv.index('--') + 1:]
out = Path(argv[0]).resolve(); out.mkdir(parents=True, exist_ok=True)
tag = argv[1]; pct = int(argv[2])
boxes = []
for a in argv[3:]:
    n, b = a.split(':'); boxes.append((n, [float(v) for v in b.split(',')]))
h0 = sha(bpy.data.filepath)
RA = runpy.run_path(str(NB / 'workers/inventory/render_assets.py'), run_name='ra_lib')
H = runpy.run_path(str(NB / 'scripts/integrate_assets.py'), run_name='ia_lib')
OVL = set(H['OVERLAY_COLLECTIONS'])
r = bpy.context.scene.render
winx = r.resolution_x * pct // 100; winy = r.resolution_y * pct // 100; s = winx / W_PT
jobs = []
for n, b in boxes:
    pxb = RA['px_box_for'](b, s, winx, winy, pad=0)
    res = RA['border_two_pass'](out / f'_pass_{tag}_{n}.png', pxb, pct, OVL)
    jobs.append({'name': n, 'box_pt': b, 'px_box': list(pxb), 'map': res['map_pass'], 'overlay': res['overlay_pass'],
                 'out': str(out / f'{tag}_{n}_x{round(s)}.png')})
spec = out / f'_jobs_{tag}.json'
spec.write_text(json.dumps(jobs))
code = r'''
import json, sys
from PIL import Image
for j in json.load(open(sys.argv[1])):
    m = Image.open(j['map']).convert('RGBA'); o = Image.open(j['overlay']).convert('RGBA')
    if o.size != m.size: o = o.resize(m.size)
    Image.alpha_composite(m, o).convert('RGB').save(j['out'])
    print(j['out'], m.size)
'''
uv = shutil.which('uv') or '/opt/homebrew/bin/uv'
cp = subprocess.run([uv, 'run', '-q', '--no-project', '--with', 'pillow', 'python', '-I', '-c', code, str(spec)],
                    capture_output=True, text=True)
print(cp.stdout, cp.stderr)
assert sha(bpy.data.filepath) == h0, 'input blend changed'
print('RENDERBOX', json.dumps({'tag': tag, 'pct': pct, 'px_per_pt': round(s, 4), 'n': len(jobs)}))
