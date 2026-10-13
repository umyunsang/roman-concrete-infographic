import bpy, sys
import numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts
S = Screen(); ks = bpy.data.objects['H_gate_keystone']; W = world_verts(ks); P = S.project(W)
for w, p in zip(W, P): print(np.round(w, 4), np.round(p, 2))
print([m.type for m in ks.modifiers], ks.data.users, ks.parent.name)
