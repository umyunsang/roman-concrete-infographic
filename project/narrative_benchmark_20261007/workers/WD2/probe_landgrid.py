import bpy, sys, numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/WD2')
from wd2_lib import bvh_world, ray_down_z
out = sys.argv[sys.argv.index('--')+1]
land = bvh_world([bpy.data.objects['T_land']])
xs = np.arange(20, 70, 0.05); ys = np.arange(-100, -60, 0.05)
Z = np.full((len(ys), len(xs)), np.nan, np.float32)
for j, y in enumerate(ys):
    for i, x in enumerate(xs):
        z = ray_down_z(land, x, y)
        if z is not None: Z[j, i] = z
np.savez_compressed(out, Z=Z, xs=xs, ys=ys)
print('ok')
