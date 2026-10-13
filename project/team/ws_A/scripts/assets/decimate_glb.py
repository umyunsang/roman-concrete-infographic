"""백그라운드 Blender로 무거운 GLB를 줄여서 다시 저장 (메인 Blender 메모리 보호).
blender -b --factory-startup --python decimate_glb.py -- <in.glb> <out.glb> <목표 삼각형 수>
재질·텍스처는 버림(흑백 클레이). 메시는 하나로 합침.
"""
import sys
import bpy

src, dst, target = sys.argv[sys.argv.index('--') + 1:][:3]
target = int(target)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
bpy.ops.object.select_all(action='DESELECT')
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1:
    bpy.ops.object.join()
ob = bpy.context.view_layer.objects.active
ob.data.materials.clear()
n = sum(len(p.vertices) - 2 for p in ob.data.polygons)
ratio = min(1.0, target / max(1, n))
if ratio < 1.0:
    m = ob.modifiers.new('dec', 'DECIMATE')
    m.decimate_type = 'COLLAPSE'
    m.ratio = ratio
    m.use_collapse_triangulate = True
    bpy.ops.object.modifier_apply(modifier=m.name)
n2 = sum(len(p.vertices) - 2 for p in ob.data.polygons)
for o in list(bpy.context.scene.objects):
    if o != ob:
        bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_materials='NONE', use_selection=False)
print('DECIMATED', src, n, '->', n2)
