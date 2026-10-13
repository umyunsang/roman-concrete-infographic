import bpy, sys, numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, bvh_of, map_visible_objects
S = Screen(); B, own = bvh_of(map_visible_objects())
pts = [tuple(map(float, a.split(','))) for a in sys.argv[sys.argv.index('--') + 1:]]
for p in pts:
    res = []
    for dx in (-0.5, 0, 0.5):
        for dy in (-0.5, 0, 0.5):
            o, d = S.ray(np.array((p[0] + dx, p[1] + dy)))
            h = B.ray_cast(o, d)
            res.append(own[h[2]] if h[0] is not None else None)
    o, d = S.ray(np.array(p)); h = B.ray_cast(o, d)
    print('HIT', p, sorted(set(res)), 'centre', own[h[2]] if h[0] else None, 'normal', tuple(round(x, 2) for x in h[1]) if h[0] else None, 'mat_index', bpy.data.objects[own[h[2]]].data.polygons[0].material_index if False else '')
