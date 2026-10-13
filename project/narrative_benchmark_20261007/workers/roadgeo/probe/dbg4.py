import bpy, numpy as np
from mathutils.kdtree import KDTree
me = bpy.data.objects['T_land'].data
co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
kd = KDTree(len(co))
for i, c in enumerate(co): kd.insert(c, i)
kd.balance()
for vi in (2445, 2453, 2455, 2460, 2470):
    print(vi, co[vi].round(3), [(j, round(d, 5)) for _, j, d in kd.find_range(co[vi], 0.05)])
    # faces using vi
    fs = [p.index for p in me.polygons if vi in p.vertices]
    for f in fs:
        p = me.polygons[f]; print('   face', f, list(p.vertices), [round(v, 2) for v in p.normal])
