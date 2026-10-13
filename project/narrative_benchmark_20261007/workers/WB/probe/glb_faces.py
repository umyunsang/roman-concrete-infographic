import bpy, sys
import numpy as np
args = sys.argv[sys.argv.index('--') + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=args[0])
o = [o for o in bpy.data.objects if o.type == 'MESH'][0]
me = o.data
img = bpy.data.images[0]; w, h = img.size
px = np.empty(w * h * 4, np.float32); img.pixels.foreach_get(px); px = px.reshape(h, w, 4)
nl = len(me.loops); uv = np.empty(nl * 2, np.float32); me.uv_layers[0].data.foreach_get('uv', uv); uv = uv.reshape(-1, 2)
nf = len(me.polygons)
ls = np.empty(nf, np.int32); me.polygons.foreach_get('loop_start', ls)
lt = np.empty(nf, np.int32); me.polygons.foreach_get('loop_total', lt)
assert (lt == 3).all()
fuv = uv.reshape(-1, 3, 2).mean(1)
ix = np.clip((fuv[:, 0] * w).astype(int), 0, w - 1); iy = np.clip((fuv[:, 1] * h).astype(int), 0, h - 1)
col = px[iy, ix, :3]   # image pixels are bottom-up like uv v
cen = np.empty(nf * 3, np.float32); me.polygons.foreach_get('center', cen); cen = cen.reshape(-1, 3)
area = np.empty(nf, np.float32); me.polygons.foreach_get('area', area)
co = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get('co', co)
fv = np.empty(nf * 3, np.int32); me.polygons.foreach_get('vertices', fv)
np.savez_compressed(args[1], col=col, cen=cen, area=area, co=co.reshape(-1, 3), fv=fv.reshape(-1, 3), cs=img.colorspace_settings.name)
print('saved', nf, img.colorspace_settings.name)
