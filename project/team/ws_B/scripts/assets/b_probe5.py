import bpy, numpy as np
U = bpy.data.texts['asset_utils.py'].as_module()
for n in ('F_villa_walls', 'F_villa_roofs'):
    o = bpy.data.objects.get(n)
    print('PROBE', n, o is not None and [c.name for c in o.users_collection], o and o.hide_render, o and tuple(round(c, 2) for c in o.color), o and len(o.data.polygons))
    if o:
        P = U.eval_world_coords(o, 1); print('PROBE z', P[:, 2].min().round(2), P[:, 2].max().round(2), P[:8].round(2).tolist())
