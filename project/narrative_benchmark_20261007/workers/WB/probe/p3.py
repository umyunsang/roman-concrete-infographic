import bpy, sys, json
import numpy as np
from mathutils import Vector
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts
S = Screen(); O = bpy.data.objects
c5 = O['C5_researchers']; me = c5.data
mats = [s.material.name for s in c5.material_slots]
Wv = world_verts(c5)
pm = np.array([p.material_index for p in me.polygons])
ppl = set()
for p in me.polygons:
    if mats[p.material_index] in ('RC.v12.skin', 'RC.v12.linen', 'RC.v12.cloth'): ppl.update(p.vertices)
P = Wv[sorted(ppl)]
# grid clustering on xy
cell = 0.25
keys = {}
for i, (x, y, z) in enumerate(P):
    keys.setdefault((int(np.floor(x / cell)), int(np.floor(y / cell))), []).append(i)
lab = {}; cur = 0
for k in keys:
    if k in lab: continue
    stack = [k]; lab[k] = cur
    while stack:
        a = stack.pop()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                b = (a[0] + dx, a[1] + dy)
                if b in keys and b not in lab: lab[b] = cur; stack.append(b)
    cur += 1
for c in range(cur):
    idx = [i for k, v in keys.items() if lab[k] == c for i in v]
    Q = P[idx]
    if len(Q) < 200: continue
    foot = Q[:, 2].min(); top = Q[:, 2].max()
    base = Q[Q[:, 2] < foot + 0.05].mean(0)
    scr = np.linalg.norm(S.project(np.array([(base[0], base[1], top)]))[0] - S.project(np.array([(base[0], base[1], foot)]))[0])
    print('person', c, len(Q), 'xy', base[:2].round(2), 'h_world', round(top - foot, 3), 'screen_h_pt', round(float(scr), 2), 'pt/BU', round(1 / S.world_per_pt(Vector(base)), 2))
c2 = O['C2_hot_mixing']
print('C2 loc pt/BU', 1 / S.world_per_pt(c2.matrix_world.translation))
# vertical pt per world at C2
p = np.array(c2.matrix_world.translation)
print('vertical pt/world at C2', np.linalg.norm(S.project(np.array([p + np.array((0, 0, 1)]))[0]) - S.project(np.array([p]))[0]))
# screen derivative of ground translation at C2
for d in [(1, 0, 0), (0, 1, 0)]:
    print('d', d, S.project(np.array([p + np.array(d)]))[0] - S.project(np.array([p]))[0])
