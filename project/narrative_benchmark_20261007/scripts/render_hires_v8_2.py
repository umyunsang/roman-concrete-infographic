"""Print-resolution passes (100% = 4962x7016, ~300 ppi at A2) of the current Blender file, no scene edits."""
import bpy, runpy, sys, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
H = runpy.run_path(str(ROOT / 'scripts/integrate_assets.py'), run_name='helpers')
tag = sys.argv[sys.argv.index('--') + 1]
res = H['render_two_pass'](ROOT / f'renders/{tag}_print.png', resolution_percentage=100)
print('RENDER ' + json.dumps(res))
