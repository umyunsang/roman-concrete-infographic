import bpy, sys, importlib
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/WD2')
import wd2_lib, harbor_build, render_box
from harbor_build import build_lighthouse_mesh, SEA_Z
out = sys.argv[sys.argv.index('--')+1]
lh = bpy.data.objects['L09_portus_lighthouse']
stone = bpy.data.materials['RC.v12.roman_stone']; plinth = bpy.data.materials['RC.v12.roman_plinth']
flame = wd2_lib.material_copy('RC.v12_wd2.lighthouse_flame', 'RC.v12.roman_stone', '#D7A64C')
me, ztop = build_lighthouse_mesh('L09_portus_lighthouse_wd2', {'stone': 0, 'plinth': 1, 'flame': 2})
me.materials.clear(); me.materials.append(stone); me.materials.append(plinth); me.materials.append(flame)
lh.data = me
lh.location = (35.25, -93.95, SEA_Z); lh.scale = (1, 1, 1); lh.rotation_euler = (0, 0, 0)
for n in ['L09_portus_mole', 'L12_harbor_pilae']:
    o = bpy.data.objects[n]; o.location.z -= 0.74
print('top z', ztop, 'faces', len(me.polygons))
render_box.render_box(out, 20, 260, 1360, 1560, pct=100)
