import bpy, sys, json, numpy as np, math
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts
S = Screen()
o = bpy.data.objects['COL_ruined']
me = o.data
nv = len(me.vertices)
ed = np.empty(len(me.edges) * 2, np.int64); me.edges.foreach_get('vertices', ed); ed = ed.reshape(-1, 2)
par = np.arange(nv)


def find(a):
    while par[a] != a:
        par[a] = par[par[a]]; a = par[a]
    return a


for a, b in ed:
    ra, rb = find(a), find(b)
    if ra != rb:
        par[ra] = rb
roots = np.array([find(i) for i in range(nv)])
u, inv, cnt = np.unique(roots, return_inverse=True, return_counts=True)
print('islands', len(u), 'largest', np.sort(cnt)[-5:])
W = world_verts(o)
P = S.project(W)
small = np.nonzero(cnt < 2000)[0]
print('small islands', len(small))
rows = []
for k in small:
    vid = np.nonzero(inv == k)[0]
    pp = P[vid]
    rows.append((int(cnt[k]), round(float(pp[:, 0].min()), 1), round(float(pp[:, 0].max()), 1), round(float(pp[:, 1].min()), 1), round(float(pp[:, 1].max()), 1),
                 W[vid].min(0).round(2).tolist(), W[vid].max(0).round(2).tolist()))
rows.sort(key=lambda r: -r[0])
for r in rows[:80]:
    print(r)
# islands touching regions
for nm, box in [('wfin', (380, 400, 845, 862)), ('efin', (740, 770, 893, 935)), ('hole', (696, 722, 926, 944))]:
    x0, x1, y0, y1 = box
    sel = [r for r in rows if r[1] < x1 and r[2] > x0 and r[3] < y1 and r[4] > y0]
    print('==', nm, sel[:20])
