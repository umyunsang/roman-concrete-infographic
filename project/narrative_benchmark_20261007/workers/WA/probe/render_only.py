import bpy, sys, runpy
from pathlib import Path
ROOT = Path('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work')
argv = sys.argv[sys.argv.index('--') + 1:]
H = runpy.run_path(str(ROOT / 'scripts/integrate_assets.py'), run_name='helpers')
print('RENDER', H['render_two_pass'](Path(argv[0]).resolve().with_suffix('.png')))
