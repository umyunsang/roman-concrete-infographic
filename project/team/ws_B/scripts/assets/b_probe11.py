import bpy, numpy as np
U = bpy.data.texts['asset_utils.py'].as_module()
for o in bpy.data.objects:
    if o.type != 'MESH' or o.hide_render:
        continue
    cs = [c for c in o.users_collection]
    if any(c.hide_render for c in cs):
        continue
    try:
        q = U.project_pts(U.eval_world_coords(o, 4 if len(o.data.vertices) > 50000 else 1))
    except Exception:
        continue
    m = (q[:, 0] > 130) & (q[:, 0] < 170) & (q[:, 1] > 315) & (q[:, 1] < 345)
    if m.sum() > 0:
        print('PROBE', o.name, [c.name for c in cs], int(m.sum()))
