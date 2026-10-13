import bpy
U = bpy.data.texts['asset_utils.py'].as_module()
tot = 0; big = []
for o in bpy.data.objects:
    if o.type != 'MESH' or o.hide_render:
        continue
    if any(c.hide_render for c in o.users_collection):
        continue
    n = U.tri_count(o); tot += n; big.append((n, o.name))
big.sort(reverse=True)
print('TRIS total', tot, 'top', big[:8])
