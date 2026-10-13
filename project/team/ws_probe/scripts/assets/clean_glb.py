"""(백그라운드 Blender) Meshy GLB → 복셀 재구성(깨끗한 겉면) → 목표 삼각형 → 평면 합치기 → GLB 저장.
blender -b --factory-startup --python clean_glb.py -- <in.glb> <out.glb> <복셀 비율> <목표 tris>
"""
import math
import sys
import bpy

src, dst, vr, tgt = sys.argv[sys.argv.index('--') + 1:][:4]
vr = float(vr); tgt = int(tgt)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
ms = [o for o in bpy.context.scene.objects if o.type == 'MESH']
bpy.ops.object.select_all(action='DESELECT')
for o in ms:
    o.select_set(True)
bpy.context.view_layer.objects.active = ms[0]
if len(ms) > 1:
    bpy.ops.object.join()
ob = bpy.context.view_layer.objects.active
ob.data.materials.clear()
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
dim = max(ob.dimensions)


def apply(m):
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
        bpy.ops.object.modifier_apply(modifier=m.name)


def ntri():
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


n0 = ntri()
m = ob.modifiers.new('rm', 'REMESH'); m.mode = 'VOXEL'; m.voxel_size = dim * vr; apply(m)
n1 = ntri()
if n1 > tgt:
    m = ob.modifiers.new('d', 'DECIMATE'); m.ratio = tgt / n1; apply(m)
m = ob.modifiers.new('p', 'DECIMATE'); m.decimate_type = 'DISSOLVE'; m.angle_limit = math.radians(3.0); apply(m)
for o in list(bpy.context.scene.objects):
    if o != ob:
        bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_materials='NONE')
print('CLEAN', src.split('/')[-1], n0, '-> remesh', n1, '->', ntri())
