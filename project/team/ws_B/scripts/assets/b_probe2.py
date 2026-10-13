import bpy, numpy as np
U = bpy.data.texts['asset_utils.py'].as_module()
for n in ('S_lab_island', 'L09_portus_lighthouse', 'L09_portus_mole', 'L12_harbor_pilae', 'L08_pompeii_site', 'L08_pompeii', 'L07_vesuvius'):
    o = bpy.data.objects[n]; P = U.eval_world_coords(o, 1)
    z = P[:, 2]
    print('PROBE', n, 'zmin %.3f zmax %.3f p2 %.3f' % (z.min(), z.max(), np.percentile(z, 2)), 'users', o.data.users, 'verts', len(P))
