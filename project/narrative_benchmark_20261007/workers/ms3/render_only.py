"""Render the open blend with scripts/integrate_assets.render_two_pass (nothing saved).
Run: Blender -b <x.blend> --factory-startup --python render_only.py -- <render_prefix>"""
import sys, runpy
from pathlib import Path
pre = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
H = runpy.run_path('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/scripts/integrate_assets.py', run_name='helpers')
print('RENDER', H['render_two_pass'](pre.with_suffix('.png')))
