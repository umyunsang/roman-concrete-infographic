import bpy, bmesh, sys, json, numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts, Terrain
S = Screen()
o = bpy.data.objects['L05_aqua_claudia']
me = o.data
bm = bmesh.new(); bm.from_mesh(me)
bm.verts.ensure_lookup_table()
# islands
seen = set(); islands = []
for v in bm.verts:
    if v.index in seen: continue
    st = [v]; comp = []
    seen.add(v.index)
    while st:
        a = st.pop(); comp.append(a.index)
        for e in a.link_edges:
            b = e.other_vert(a)
            if b.index not in seen:
                seen.add(b.index); st.append(b)
    islands.append(comp)
W = world_verts(o)
print('islands', len(islands))
info = []
for comp in islands:
    P = W[comp]
    info.append((len(comp), P.min(0).round(2).tolist(), P.max(0).round(2).tolist()))
info.sort(key=lambda t: t[1][1])
sizes = {}
for n, mn, mx in info:
    key = (n, round(mx[2] - mn[2], 2))
    sizes[key] = sizes.get(key, 0) + 1
print('island size classes', sorted(sizes.items(), key=lambda t: -t[1])[:20])
for t in info[:12]: print(t)
for t in info[-6:]: print(t)
# vertex z histogram
print('z hist', np.histogram(W[:, 2], bins=20))
T = Terrain(bpy.data.objects['T_land'])
mi = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', mi)
print('mat idx counts', np.bincount(mi))
# plinth faces (slot 1) islands
json.dump({'islands': info}, open('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/WD1/aq_islands.json', 'w'))
