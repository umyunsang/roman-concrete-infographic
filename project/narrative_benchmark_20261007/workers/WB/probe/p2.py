import bpy, sys, json, bmesh
import numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts
S = Screen()
o = bpy.data.objects['C2_hot_mixing']
me = o.data
bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
# union-find over vertices via edges
n = len(bm.verts); parent = np.arange(n)
def find(a):
    while parent[a] != a:
        parent[a] = parent[parent[a]]; a = parent[a]
    return a
for e in bm.edges:
    a, b = find(e.verts[0].index), find(e.verts[1].index)
    if a != b: parent[a] = b
roots = np.array([find(i) for i in range(n)])
Wv = world_verts(o); P = S.project(Wv)
mats = [s.material.name.replace('RC.v12.','') for s in o.material_slots]
comp = {}
for f in bm.faces:
    r = roots[f.verts[0].index]
    d = comp.setdefault(r, {'nf':0, 'mat':{}, 'v':set()})
    d['nf'] += 1; d['mat'][mats[f.material_index]] = d['mat'].get(mats[f.material_index],0)+1
    d['v'].update(v.index for v in f.verts)
print('components', len(comp))
rows = []
for r, d in comp.items():
    v = np.array(sorted(d['v']))
    w = Wv[v]; p = P[v]
    rows.append((d['nf'], d['mat'], [round(float(x),2) for x in (*w.min(0), *w.max(0))], [round(float(x),1) for x in (*p.min(0), *p.max(0))]))
rows.sort(key=lambda t: -t[0])
for row in rows[:60]:
    print(row)
print('local bbox', [round(x,3) for x in np.array([v.co for v in me.vertices]).min(0)], [round(x,3) for x in np.array([v.co for v in me.vertices]).max(0)])
# per material bbox
pm = np.array([f.material_index for f in me.polygons])
for k, m in enumerate(mats):
    fv = set()
    for f in me.polygons:
        if f.material_index == k: fv.update(f.vertices)
    v = np.array(sorted(fv))
    print(m, len(v), [round(float(x),2) for x in (*Wv[v].min(0), *Wv[v].max(0))], [round(float(x),1) for x in (*P[v].min(0), *P[v].max(0))])
print('world_per_pt at C2', S.world_per_pt(o.matrix_world.translation))
c5 = bpy.data.objects['C5_researchers']; print('world_per_pt at C5', S.world_per_pt(c5.matrix_world.translation), 'C5 mats', [s.material.name for s in c5.material_slots], 'loc', list(c5.location), 'scale', list(c5.scale))
