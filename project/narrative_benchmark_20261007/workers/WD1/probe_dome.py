import bpy, numpy as np
o = bpy.data.objects['R8_pantheon']; me = o.data
co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
n = len(me.polygons)
cen = np.empty(n * 3); me.polygons.foreach_get('center', cen); cen = cen.reshape(-1, 3)
nrm = np.empty(n * 3); me.polygons.foreach_get('normal', nrm); nrm = nrm.reshape(-1, 3)
mi = np.empty(n, np.int32); me.polygons.foreach_get('material_index', mi)
# fit centre from the oculus rim / dome verts z>0.5
top = co[co[:, 2] > 0.5]
cx, cy = (top[:, 0].max() + top[:, 0].min()) / 2, (top[:, 1].max() + top[:, 1].min()) / 2
print('centre', cx, cy)
r = np.hypot(co[:, 0] - cx, co[:, 1] - cy)
# restrict to back half (y > cy) so the portico/middle block do not interfere
for z0 in np.arange(0.25, 0.615, 0.005):
    s = (co[:, 2] >= z0) & (co[:, 2] < z0 + 0.005) & (co[:, 1] > cy + 0.05)
    if s.sum():
        print('z %.3f n %4d r max %.3f p50 %.3f min %.3f' % (z0, s.sum(), r[s].max(), np.median(r[s]), r[s].min()))
rc = np.hypot(cen[:, 0] - cx, cen[:, 1] - cy)
for lo, hi in [(0.28, 0.47), (0.29, 0.466), (0.466, 0.62)]:
    s = (cen[:, 2] > lo) & (cen[:, 2] < hi) & (rc < 0.66)
    print('faces z %.3f-%.3f r<0.66:' % (lo, hi), s.sum(), 'mats', np.bincount(mi[s], minlength=3))
# oculus inner wall
s = (cen[:, 2] > 0.55) & (rc < 0.2)
print('oculus faces', s.sum(), 'r range', rc[s].min() if s.any() else None, rc[s].max() if s.any() else None)
print('verts z max', co[:, 2].max(), 'min r at top', r[co[:, 2] > 0.6].min())
