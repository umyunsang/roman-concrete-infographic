import bpy, sys, runpy
from pathlib import Path
ROOT = Path('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work')
argv = sys.argv[sys.argv.index('--') + 1:]
ratio, sm_f, sm_n, out = float(argv[0]), float(argv[1]), int(argv[2]), argv[3]
col = bpy.data.objects['H_colosseum_mini']
m = col.modifiers.new('d', 'DECIMATE'); m.ratio = ratio
if sm_n:
    s = col.modifiers.new('s', 'SMOOTH'); s.factor = sm_f; s.iterations = sm_n
sc = bpy.context.scene; r = sc.render
r.use_border = True; r.use_crop_to_border = True
r.border_min_x = 1070/1191; r.border_max_x = 1165/1191; r.border_min_y = 1 - 145/1684; r.border_max_y = 1 - 80/1684
for c in bpy.data.collections:
    c.hide_render = c.name not in ('85_HEADER', 'Collection') and c.hide_render or c.name not in ('85_HEADER','Collection')
r.film_transparent = False; r.resolution_percentage = 72
r.filepath = str(Path(out).resolve()); bpy.ops.render.render(write_still=True)
