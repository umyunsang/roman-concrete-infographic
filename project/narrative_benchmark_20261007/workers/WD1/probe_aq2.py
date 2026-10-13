import bpy, sys, json, numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/WD1')
import wd1lib as L
S = L.Screen()
T = L.Terrain(bpy.data.objects['T_land'])
o = bpy.data.objects['L05_aqua_claudia']; me = o.data
Wv = L.world_verts(o)
nv = len(me.vertices)
ed = np.empty(len(me.edges) * 2, np.int64); me.edges.foreach_get('vertices', ed); ed = ed.reshape(-1, 2)
par = np.arange(nv)
def find(a):
    while par[a] != a:
        par[a] = par[par[a]]; a = par[a]
    return a
for a, b in ed:
    ra, rb = find(a), find(b)
    if ra != rb: par[ra] = rb
roots = np.array([find(i) for i in range(nv)])
u, inv = np.unique(roots, return_inverse=True)
isl = [np.nonzero(inv == k)[0] for k in range(len(u))]
mi = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', mi)
pv = [list(p.vertices) for p in me.polygons]
vmat = np.zeros(nv, np.int32)
for f, vs in enumerate(pv):
    vmat[vs] = mi[f]
rows = []
for k, vs in enumerate(isl):
    P = Wv[vs]; mn, mx = P.min(0), P.max(0)
    rows.append(dict(k=k, n=len(vs), c=((mn + mx) / 2).tolist(), size=(mx - mn).tolist(), zmin=float(mn[2]), zmax=float(mx[2]), mat=int(vmat[vs[0]])))
# pier course blocks: footprint <= 1.0 x 1.0 (axis-aligned bbox, approx), height <= 0.6, top below 4.2
blocks = [r for r in rows if r['n'] == 8 and max(r['size'][0], r['size'][1]) < 1.0 and r['size'][2] < 0.6 and r['zmax'] < 4.15]
print('blocks', len(blocks), 'plinth-mat blocks', sum(r['mat'] == 1 for r in blocks))
# cluster by xy
cent = np.array([r['c'][:2] for r in blocks])
lab = -np.ones(len(blocks), int); nc = 0
for i in range(len(blocks)):
    if lab[i] >= 0: continue
    d = np.linalg.norm(cent - cent[i], axis=1)
    lab[(d < 0.25) & (lab < 0)] = nc; nc += 1
piers = []
for c in range(nc):
    idx = np.nonzero(lab == c)[0]
    bl = [blocks[i] for i in idx]
    xy = np.median(cent[idx], 0)
    zb = min(b['zmin'] for b in bl); zt = max(b['zmax'] for b in bl)
    bottom = min(bl, key=lambda b: b['zmin'])
    piers.append(dict(xy=xy.round(3).tolist(), n=len(bl), zb=round(zb, 3), zt=round(zt, 3), bottom_size=np.round(bottom['size'], 2).tolist(), bottom_mat=bottom['mat']))
piers.sort(key=lambda p: p['xy'][1])
print('piers', len(piers))
for p in piers:
    x, y = p['xy']
    hs = [T.z(x + dx, y + dy) for dx in (-0.45, 0, 0.45) for dy in (-0.45, 0, 0.45)]
    p['terr'] = [round(min(hs), 3), round(max(hs), 3)]
    p['pt'] = S.to_pt((x, y, p['zb'])).round(1).tolist()
    print(p)
json.dump(piers, open('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/WD1/aq_piers.json', 'w'))
# what else: non-block islands summary
other = [r for r in rows if r not in blocks]
cls = {}
for r in other:
    key = (r['n'], round(r['size'][2], 1), r['mat'])
    cls[key] = cls.get(key, 0) + 1
print('other classes', sorted(cls.items(), key=lambda t: -t[1])[:20])
