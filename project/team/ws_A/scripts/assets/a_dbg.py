import bpy, numpy as np
from mathutils import Vector
sc = bpy.context.scene; cam = sc.camera
dg = bpy.context.evaluated_depsgraph_get()
fr = [cam.matrix_world @ v for v in cam.data.view_frame(scene=sc)]
o = cam.matrix_world.translation
def ray(u, v):
    a = u / 1191.0; b = v / 1684.0
    top = fr[3].lerp(fr[0], a); bot = fr[2].lerp(fr[1], a)
    p = top.lerp(bot, b)
    d = (p - o).normalized()
    hit, loc, nrm, idx, ob, mat = sc.ray_cast(dg, o, d)
    return (ob.name if ob else None), (tuple(round(x, 2) for x in loc) if hit else None)
for (u, v) in [(27, 300), (26, 298), (28, 302), (25, 301), (115, 285), (50, 275)]:
    print('DBG', (u, v), ray(u, v))
