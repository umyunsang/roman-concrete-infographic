"""lwin.py - terrain-only L* statistics of poster windows in a map-pass PNG (read-only).

Blender -b <blend> --factory-startup --python lwin.py -- <map_pass.png> <out.json> name:x0,x1,y0,y1 [...] [--ring c5]
For every pixel centre in a window, a camera ray against the map-visible objects decides whether the pixel shows
T_land; L* (D65, sRGB) statistics are taken over those pixels only. '--ring c5' adds the 0.5-4 pt band around the
C5_researchers silhouette (RO-2): share of band samples whose L* deviates >= 3 from the median ground L* of the
20-30 pt ring.
"""
import bpy, sys, json, math
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'workers/layout'))
sys.path.insert(0, str(HERE))
from common import Screen, map_visible_objects   # noqa: E402
from mathutils.bvhtree import BVHTree

argv = sys.argv[sys.argv.index('--') + 1:]
png, outp = argv[0], argv[1]
specs = [a for a in argv[2:] if ':' in a]
S = Screen()
img = bpy.data.images.load(png, check_existing=False)
w, h = img.size
px = np.empty(w * h * 4, np.float32); img.pixels.foreach_get(px)
px = px.reshape(h, w, 4)[::-1, :, :3]          # top-left origin, linear? -> images load as sRGB-encoded floats
cs = img.colorspace_settings.name
s = w / 1191.0


def lstar_from_float(rgb):
    # bpy image pixels of an sRGB png are display-encoded values in 0..1 (the colour space is applied at view time)
    c = np.clip(rgb, 0, 1)
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    Y = lin @ np.array([0.2126, 0.7152, 0.0722])
    f = np.where(Y > 216 / 24389, np.cbrt(Y), (24389 / 27 * Y + 16) / 116)
    return 116 * f - 16


dg = bpy.context.evaluated_depsgraph_get()
verts, polys, owner, names = [], [], [], []
for o in map_visible_objects():
    ev = o.evaluated_get(dg); me = ev.to_mesh()
    if len(me.vertices) == 0:
        ev.to_mesh_clear(); continue
    co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    Wv = (np.c_[co, np.ones(len(co))] @ np.array(o.matrix_world).T)[:, :3]
    k = len(names); names.append(o.name)
    b = len(verts); verts.extend(map(tuple, Wv))
    for p in me.polygons:
        polys.append([b + i for i in p.vertices]); owner.append(k)
    ev.to_mesh_clear()
bvh = BVHTree.FromPolygons(verts, polys); owner = np.array(owner)


def first(pt):
    o, d = S.ray(pt)
    r = bvh.ray_cast(o, d)
    return names[owner[r[2]]] if r[2] is not None else None


res = {'png': png, 'colorspace': cs, 'px_per_pt': round(s, 3)}
for sp in specs:
    n, b = sp.split(':'); x0, x1, y0, y1 = map(float, b.split(','))
    vals = []
    for py in range(int(round(y0 * s)), int(round(y1 * s))):
        for pxx in range(int(round(x0 * s)), int(round(x1 * s))):
            pt = ((pxx + 0.5) / s, (py + 0.5) / s)
            if first(pt) == 'T_land':
                vals.append(px[py, pxx])
    L = lstar_from_float(np.array(vals))
    res[n] = {'box': [x0, x1, y0, y1], 'n': int(len(L)), 'mean': round(float(L.mean()), 2), 'p50': round(float(np.median(L)), 2),
              'p99': round(float(np.percentile(L, 99)), 2), 'share_ge95': round(float((L >= 95).mean()), 4)}
if '--ring' in argv:
    c5 = bpy.data.objects['C5_researchers']
    from common import screen_tris, sample_tris
    P, T = screen_tris(c5, S)
    box = (P[:, 0].min() - 35, P[:, 0].max() + 35, P[:, 1].min() - 35, P[:, 1].max() + 35)
    step = 1.0 / s
    xs = np.arange(box[0], box[1], step); ys = np.arange(box[2], box[3], step)
    sil = np.zeros((len(ys), len(xs)), bool); terr = np.zeros_like(sil); Lm = np.zeros(sil.shape)
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            nm = first((x, y))
            sil[j, i] = nm == 'C5_researchers'
            terr[j, i] = nm == 'T_land'
            pxx, py = int(x * s), int(y * s)
            if 0 <= py < h and 0 <= pxx < w:
                Lm[j, i] = lstar_from_float(px[py, pxx][None])[0]
    # distance (pt) to silhouette by brute dilation steps
    dist = np.full(sil.shape, np.inf); cur = sil.copy(); d = 0.0
    rr = int(math.ceil(30 / step))
    from itertools import product
    ksz = 1
    for kstep in range(1, rr + 1):
        nxt = cur.copy()
        nxt[1:, :] |= cur[:-1, :]; nxt[:-1, :] |= cur[1:, :]; nxt[:, 1:] |= cur[:, :-1]; nxt[:, :-1] |= cur[:, 1:]
        newm = nxt & ~cur
        dist[newm] = kstep * step
        cur = nxt
    band = terr & (dist >= 0.5) & (dist <= 4.0)
    ring = terr & (dist >= 20) & (dist <= 30)
    g = float(np.median(Lm[ring])) if ring.any() else float('nan')
    dev = np.abs(Lm[band] - g)
    res['c5_band'] = {'ground_g': round(g, 2), 'band_samples': int(band.sum()), 'share_dev_ge3': round(float((dev >= 3).mean()), 3),
                      'band_mean': round(float(Lm[band].mean()), 2)}
Path(outp).write_text(json.dumps(res, indent=1))
print('LWIN ' + json.dumps(res))
