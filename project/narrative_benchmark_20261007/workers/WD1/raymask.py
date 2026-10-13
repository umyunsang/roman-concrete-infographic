"""raymask.py - per-pixel camera ray cast against one object (and optionally all map objects) for screen boxes.
Blender -b <blend> --factory-startup --python raymask.py -- <out.npz> <obj> <ppt> x0 x1 y0 y1 [x0 x1 y0 y1 ...]
Saves for each box: own (bool: first hit among all map objects is <obj>), only (bool: hit <obj> when alone), face idx (own-only cast)."""
import bpy, sys, numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, bvh_of, map_visible_objects
argv = sys.argv[sys.argv.index('--') + 1:]
out, name, ppt = argv[0], argv[1], float(argv[2])
boxes = [tuple(map(float, argv[3 + 4 * i: 7 + 4 * i])) for i in range((len(argv) - 3) // 4)]
S = Screen()
o = bpy.data.objects[name]
own_bvh, _ = bvh_of([o])
all_bvh, owner = bvh_of(map_visible_objects())
res = {}
for bi, (x0, x1, y0, y1) in enumerate(boxes):
    xs = np.arange(x0, x1, 1 / ppt) + 0.5 / ppt; ys = np.arange(y0, y1, 1 / ppt) + 0.5 / ppt
    only = np.zeros((len(ys), len(xs)), bool); own = np.zeros_like(only); fidx = -np.ones(only.shape, np.int64)
    hitname = np.empty(only.shape, object)
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            org, d = S.ray((x, y))
            loc, n, idx, dist = own_bvh.ray_cast(org, d)
            if idx is not None:
                only[j, i] = True; fidx[j, i] = idx
            loc2, n2, idx2, dist2 = all_bvh.ray_cast(org, d)
            if idx2 is not None:
                hitname[j, i] = owner[idx2]
                own[j, i] = owner[idx2] == name
    res[f'only{bi}'] = only; res[f'own{bi}'] = own; res[f'f{bi}'] = fidx
    names = sorted({h for h in hitname.ravel() if h})
    res[f'names{bi}'] = np.array(names)
    res[f'hit{bi}'] = np.vectorize(lambda h: names.index(h) if h else -1)(hitname).astype(np.int32)
    res[f'box{bi}'] = np.array([x0, x1, y0, y1, ppt])
np.savez_compressed(out, **res)
print('RAYMASK done', len(boxes))
