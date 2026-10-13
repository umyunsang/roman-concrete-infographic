"""WD2 probe: screen object-ID map by camera ray casting (map pass objects only; overlay separately).
Run: Blender -b in.blend --factory-startup --python probe_idmap.py -- out.npz [step_pt] [x0 x1 y0 y1]
Writes npz: ids (H,W) int32 (-1 = nothing), names, step, roi; plus hit z (world) map."""
import bpy, sys, json
import numpy as np
from mathutils import Vector
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, bvh_of, map_visible_objects, overlay_objects

argv = sys.argv[sys.argv.index('--') + 1:]
out = argv[0]
step = float(argv[1]) if len(argv) > 1 else 1.0
roi = [float(v) for v in argv[2:6]] if len(argv) > 5 else [0, 1191, 0, 1684]
S = Screen()
objs = map_visible_objects()
names = [o.name for o in objs]
bvh, owner = bvh_of(objs)
oidx = {n: i for i, n in enumerate(names)}
owner_i = np.array([oidx[n] for n in owner], np.int32)
ovl = overlay_objects()
bvh2, owner2 = bvh_of(ovl) if ovl else (None, [])
names2 = [o.name for o in ovl]
oidx2 = {n: i for i, n in enumerate(names2)}
owner2_i = np.array([oidx2[n] for n in owner2], np.int32) if ovl else None
xs = np.arange(roi[0] + step / 2, roi[1], step); ys = np.arange(roi[2] + step / 2, roi[3], step)
ids = np.full((len(ys), len(xs)), -1, np.int32); zs = np.full((len(ys), len(xs)), np.nan, np.float32)
ids2 = np.full((len(ys), len(xs)), -1, np.int32)
for j, y in enumerate(ys):
    for i, x in enumerate(xs):
        o, d = S.ray((x, y))
        loc, nor, fi, dist = bvh.ray_cast(o, d)
        if fi is not None:
            ids[j, i] = owner_i[fi]; zs[j, i] = loc.z
        if bvh2 is not None:
            loc, nor, fi, dist = bvh2.ray_cast(o, d)
            if fi is not None:
                ids2[j, i] = owner2_i[fi]
np.savez_compressed(out, ids=ids, z=zs, names=np.array(names), ids_ovl=ids2, names_ovl=np.array(names2),
                    step=step, roi=np.array(roi))
print('WROTE', out, ids.shape)
