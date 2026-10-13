import bpy, numpy as np
o = bpy.data.objects['D2_lime_kiln']; me = o.data
mi = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', mi)
cen = np.empty(len(me.polygons)*3); me.polygons.foreach_get('center', cen); cen = cen.reshape(-1,3)
print('KILN mats', [m.name for m in me.materials], np.bincount(mi))
r = np.hypot(cen[:,0], cen[:,1])
s = (cen[:,2] > 2.6) & (r < 0.8)
print('KILN shaft faces', s.sum(), np.bincount(mi[s], minlength=2))
print('KILN soot faces z range', cen[mi==1,2].min(), cen[mi==1,2].max())
