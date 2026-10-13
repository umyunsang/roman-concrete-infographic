import bpy, sys
from mathutils import Vector
args = sys.argv[sys.argv.index('--') + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=args[0])
sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'; sc.display.shading.light = 'FLAT'; sc.display.shading.color_type = 'TEXTURE'
sc.render.resolution_x = 500; sc.render.resolution_y = 500
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = 'ORTHO'; cam.data.ortho_scale = float(args[2])
tgt = Vector([float(v) for v in args[3].split(',')])
for name, dd in [('ny', (0, -1, 0)), ('nx', (-1, 0, 0)), ('px', (1, 0, 0))]:
    v = Vector(dd); cam.location = tgt + v * 5
    cam.rotation_euler = (-v).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = args[1] + f'_{name}.png'; bpy.ops.render.render(write_still=True)
