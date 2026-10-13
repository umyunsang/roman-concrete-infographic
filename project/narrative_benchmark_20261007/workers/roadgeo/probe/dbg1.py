import bpy, runpy, numpy as np, sys
G = runpy.run_path('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/roadgeo/step.py', run_name='lib')
ost = G['need']('R_via_ostiensis'); core = G['need']('R_core_road')
W = G['world_verts'](ost)
beds = []
for vs, fs in G['islands'](ost):
    if len(vs) != 8 or len(fs) != 5: continue
    w = W[vs]; top = w[w[:, 2] > w[:, 2].min() + 0.03]
    if len(top) != 4: continue
    e = np.linalg.norm(np.roll(top[:, :2], 1, 0) - top[:, :2], axis=1)
    if e.max() > 1.8: beds.append((w.mean(0), vs, top))
print('beds', len(beds))
CW = G['world_verts'](core); C = np.array([b[0][:2] for b in beds]); best = None
for vs, fs in G['islands'](core):
    if len(fs) < 40: continue
    d = np.array([np.linalg.norm(CW[vs, :2] - c[None], axis=1).min() for c in C])
    print('kerb', len(fs), 'min d', d.min().round(3), 'bed', d.argmin(), C[d.argmin()].round(2))
    if best is None or d.min() < best[0]: best = (float(d.min()), vs, fs, d)
_, kv, kf, dist = best; order = np.argsort(dist)
b0, b1 = beds[order[0]], beds[order[1]]
print('b0', b0[0].round(2), 'b1', b1[0].round(2))
t = (b1[0][:2] - b0[0][:2]); t /= np.linalg.norm(t); print('t', t.round(3))
top = b0[2]; north = top[np.argsort(top[:, :2] @ t)[:2]]; print('north', north.round(3))
polys = G['kerb_footprint'](core, kf); print('kerb polys', len(polys))
P = np.concatenate(polys); print('kerb poly xy range', P.min(0).round(2), P.max(0).round(2))
# nearest kerb poly to north[0]
dd = [np.linalg.norm(p.mean(0) - north[0][:2]) for p in polys]; i = int(np.argmin(dd)); print('nearest poly', polys[i].round(3), dd[i])
