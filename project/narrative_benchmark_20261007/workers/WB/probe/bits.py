import bpy, bmesh, sys
import numpy as np
from mathutils.kdtree import KDTree
o = bpy.data.objects['C2_hot_mixing']; me = o.data
slots = [s.material.name for s in o.material_slots]
M = np.array(o.matrix_world)
bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table()
PEOPLE = ('RC.v12.skin', 'RC.v12.linen', 'RC.v12.cloth', 'RC.v12.toolwood')
pv = [v.co.copy() for f in bm.faces if slots[f.material_index] in PEOPLE for v in f.verts]
kd = KDTree(len(pv))
for i, c in enumerate(pv): kd.insert(c, i)
kd.balance()
# welded adjacency among non-people faces
key = lambda c: (round(c.x, 5), round(c.y, 5), round(c.z, 5))
vf = {}
others = [f for f in bm.faces if slots[f.material_index] not in PEOPLE]
for f in others:
    for v in f.verts:
        vf.setdefault(key(v.co), []).append(f.index)
seed = set()
for f in others:
    if any(kd.find(v.co)[2] < 1e-4 for v in f.verts):
        seed.add(f.index)
print('seed faces touching people', len(seed))
def wz(f):
    return max((M @ np.append(np.array(v.co), 1))[2] for v in f.verts)
sel = set(); stack = list(seed)
while stack:
    i = stack.pop()
    if i in sel: continue
    f = bm.faces[i]
    if wz(f) < 0.18: continue          # stop at the platform surface
    sel.add(i)
    for v in f.verts:
        for j in vf[key(v.co)]:
            if j not in sel: stack.append(j)
from collections import Counter
print('selected', len(sel), Counter(slots[bm.faces[i].material_index] for i in sel))
P = np.array([(M @ np.append(np.array(v.co), 1))[:3] for i in sel for v in bm.faces[i].verts])
if len(P): print('bbox', P.min(0).round(2), P.max(0).round(2))
# clusters by xy
for c in [(-24.2, -38.1), (-19.5, -37.6)]:
    m = np.linalg.norm(P[:, :2] - np.array(c), axis=1) < 1.5
    print('near', c, m.sum())
np.save(sys.argv[sys.argv.index('--') + 1], np.array(sorted(sel)))
