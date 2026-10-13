import bpy, sys
import numpy as np
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=sys.argv[sys.argv.index('--') + 1])
for o in bpy.data.objects:
    print(o.name, o.type, o.parent.name if o.parent else None, list(o.location), list(o.rotation_euler), list(o.scale))
    if o.type == 'MESH':
        me = o.data
        co = np.array([o.matrix_world @ v.co for v in me.vertices])
        print(' verts', len(me.vertices), 'faces', len(me.polygons), 'uv', [u.name for u in me.uv_layers], 'mats', [m.name for m in me.materials])
        print(' bbox', co.min(0).round(3), co.max(0).round(3))
        # where is the jar? sample: vertices extremes along x and y
        for ax in range(3):
            i = co[:, ax].argmax(); j = co[:, ax].argmin(); print(' ax', ax, 'max at', co[i].round(3), 'min at', co[j].round(3))
for im in bpy.data.images: print('img', im.name, im.size[:])
