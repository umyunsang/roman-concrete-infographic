import bpy, sys, json
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/WD2')
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
import wd2_lib, harbor_fix, render_box
from common import Screen
argv = sys.argv[sys.argv.index('--')+1:]
S = Screen()
land = wd2_lib.bvh_world([bpy.data.objects['T_land']])
road = bpy.data.objects['R_via_ostiensis']; lh = bpy.data.objects['L09_portus_lighthouse']
pil = bpy.data.objects['L12_harbor_pilae']; mole = bpy.data.objects['L09_portus_mole']
stone = bpy.data.materials['RC.v12.roman_stone']; plinth = bpy.data.materials['RC.v12.roman_plinth']
flame = wd2_lib.material_copy('RC.v12_wd2.lighthouse_flame', 'RC.v12.roman_stone', '#D7A64C')
rep = {}
rep['level'] = harbor_fix.level_road(road, land)
rep['lh'] = harbor_fix.build_lighthouse(lh, (stone, plinth, flame))
bpy.context.view_layer.update()
rep['trim'] = harbor_fix.trim_road(road, lh, S.origin, rep['level'])
frame = dict(rep['level']); frame['road_end_s'] = rep['trim'].get('road_end_s', 7.5)
rep['causeway'] = harbor_fix.build_causeway(lh, road, frame)
mole.location.z = -0.74; pil.location.z = -0.74
print(json.dumps(rep))
render_box.render_box(argv[0], 20, 260, 1340, 1560, pct=100)
if len(argv) > 1:
    bpy.ops.wm.save_as_mainfile(filepath=argv[1], copy=True)
