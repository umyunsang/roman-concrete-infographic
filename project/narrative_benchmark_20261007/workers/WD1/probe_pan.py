import bpy, sys, json, numpy as np, math
o = bpy.data.objects['R8_pantheon']
me = o.data
n = len(me.polygons)
cen = np.empty(n * 3); me.polygons.foreach_get('center', cen); cen = cen.reshape(-1, 3)
nrm = np.empty(n * 3); me.polygons.foreach_get('normal', nrm); nrm = nrm.reshape(-1, 3)
area = np.empty(n); me.polygons.foreach_get('area', area)
mi = np.empty(n, np.int32); me.polygons.foreach_get('material_index', mi)
co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
print('local bbox', co.min(0).round(3), co.max(0).round(3))
for k in range(3):
    s = mi == k
    print('mat', k, s.sum(), 'z range', cen[s, 2].min().round(3), cen[s, 2].max().round(3), 'y range', cen[s, 1].min().round(3), cen[s, 1].max().round(3))
# portico slopes: stone faces with y<-0.55 and normal ~ (+-0.43,0,0.90)
for sx in (1, -1):
    t = np.array([0.43 * sx, 0, 0.90]); t /= np.linalg.norm(t)
    ang = np.degrees(np.arccos(np.clip(nrm @ t, -1, 1)))
    d = cen @ t
    s = (cen[:, 1] < -0.55) & (ang < 12)
    print('slope', sx, 'faces', s.sum(), 'stone', (s & (mi == 0)).sum(), 'roof', (s & (mi == 1)).sum(), 'plane d pct', np.percentile(d[s], [5, 50, 95]).round(3) if s.any() else None)
    s2 = s & (np.abs(d - 0.156) < 0.02)
    print('   with |d-0.156|<0.02', s2.sum(), 'stone', (s2 & (mi == 0)).sum())
    # histogram of d for stone faces
    if s.any():
        h = np.histogram(d[s], bins=12); print('   d hist', h[0], h[1].round(3))
# middle block roof
up = np.degrees(np.arccos(np.clip(nrm[:, 2], -1, 1))) < 12
for z0 in np.arange(0.20, 0.40, 0.01):
    s = up & (np.abs(cen[:, 2] - z0) < 0.005)
    if s.sum() > 20:
        print('up faces z~%.2f' % z0, s.sum(), 'stone', (s & (mi == 0)).sum(), 'roof', (s & (mi == 1)).sum(), 'plinth', (s & (mi == 2)).sum(),
              'x', cen[s, 0].min().round(3), cen[s, 0].max().round(3), 'y', cen[s, 1].min().round(3), cen[s, 1].max().round(3))
# dome radial profile: vertices r vs z above drum
cx, cy = np.median(co[co[:, 2] > co[:, 2].max() - 0.05, 0]), np.median(co[co[:, 2] > co[:, 2].max() - 0.05, 1])
print('top center approx', cx, cy)
r = np.hypot(co[:, 0] - cx, co[:, 1] - cy)
zs = np.linspace(co[:, 2].min(), co[:, 2].max(), 60)
for i in range(len(zs) - 1):
    s = (co[:, 2] >= zs[i]) & (co[:, 2] < zs[i + 1])
    if s.any():
        print('z %.3f-%.3f n %5d r max %.3f p90 %.3f' % (zs[i], zs[i + 1], s.sum(), r[s].max(), np.percentile(r[s], 90)))
