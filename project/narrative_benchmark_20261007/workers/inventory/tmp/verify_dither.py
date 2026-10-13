import bpy, runpy, sys
from pathlib import Path
W = Path('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/inventory')
H = runpy.run_path(str(W.parents[1] / 'scripts/integrate_assets.py'), run_name='lib')
R = runpy.run_path(str(W / 'render_assets.py'), run_name='lib')
bpy.context.scene.render.dither_intensity = 0.0
H['render_two_pass'](W / 'tmp/dither0/full.png', resolution_percentage=72)
for nm, box in [('pantheon', (1131, 1414, 1320, 1638)), ('basic_recipe', (33, 1022, 207, 447)), ('cubes', (1836, 2558, 3455, 3787))]:
    R['border_two_pass'](W / f'tmp/dither0/{nm}.png', box, 72, set(H['OVERLAY_COLLECTIONS']), map_transparent=True)
