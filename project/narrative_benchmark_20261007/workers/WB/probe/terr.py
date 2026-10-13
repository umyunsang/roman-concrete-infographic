import bpy, sys
import numpy as np
from mathutils import Vector
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, bvh_of
S = Screen()
bvh, _ = bvh_of([bpy.data.objects['T_land']])
def gz(x, y):
    h = bvh.ray_cast(Vector((x, y, 500)), Vector((0, 0, -1)))[0]; return h.z if h else None
cx, cy = -21.731, -40.59
print('terrain grid around C2 (rows y from +6 to -6, cols x -6..+6) rel to C2 origin')
for dy in np.arange(6, -6.1, -1.5):
    print(' '.join(f'{gz(cx + dx, cy + dy):6.2f}' for dx in np.arange(-8, 6.1, 1.5)), f' dy={dy}')
for x, y in [(-23.9, -38.2)]:
    print('new centre approx', gz(x, y))
