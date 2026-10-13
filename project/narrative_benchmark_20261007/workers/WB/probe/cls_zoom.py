import bpy, sys
import numpy as np
from mathutils import Vector
args = sys.argv[sys.argv.index('--') + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=args[0])
o = [o for o in bpy.data.objects if o.type == 'MESH'][0]; me = o.data
cls = np.load(args[1]); comp = np.load(args[2]) if len(args) > 5 else None
cols = [(0.58, 0.33, 0.19), (0.33, 0.29, 0.20), (0.37, 0.20, 0.13), (0.05, 0.04, 0.03), (0.0, 0.3, 0.8)]
me.materials.clear()
for i, c in enumerate(cols):
    m = bpy.data.materials.new(f'c{i}'); m.diffuse_color = (*c, 1); me.materials.append(m)
me.polygons.foreach_set('material_index', cls.astype(np.int32))
sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'; sc.display.shading.light = 'FLAT'; sc.display.shading.color_type = 'MATERIAL'
sc.render.resolution_x = 500; sc.render.resolution_y = 500
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = 'ORTHO'; cam.data.ortho_scale = float(args[4])
tgt = Vector([float(v) for v in args[5 if len(args) > 6 else 5 - 0].split(',')]) if False else Vector([float(v) for v in args[5].split(',')])
for name, dd in [('ny', (0, -1, 0)), ('nx', (-1, 0, 0)), ('px', (1, 0, 0))]:
    v = Vector(dd); cam.location = tgt + v * 5
    cam.rotation_euler = (-v).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = args[3] + f'_{name}.png'; bpy.ops.render.render(write_still=True)
