"""Render a blend with integrate_assets.render_two_pass to renders/narrative_<tag>.png (map + overlay passes)."""
import sys, json, runpy
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
tag = sys.argv[sys.argv.index('--') + 1]
H = runpy.run_path(str(ROOT / 'scripts/integrate_assets.py'), run_name='helpers')
print('RENDER ' + json.dumps(H['render_two_pass'](ROOT / f'renders/narrative_{tag}.png')))
