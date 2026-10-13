import bpy, sys
import numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts, map_visible_objects, overlay_objects
S = Screen()
mv = {o.name for o in map_visible_objects()}; ov = {o.name for o in overlay_objects()}
for o in sorted(bpy.data.objects, key=lambda o: o.name):
    if o.type != 'MESH' or len(o.data.vertices) == 0: continue
    W = world_verts(o); P = S.project(W)
    b = [P[:,0].min(), P[:,0].max(), P[:,1].min(), P[:,1].max()]
    if b[1] < 600 or b[0] > 1100 or b[3] < 800 or b[2] > 1150: continue
    print(f"{o.name:40s} {'MAP' if o.name in mv else ('OVL' if o.name in ov else 'hid')} colls={[c.name for c in o.users_collection]} sbox={[round(float(v),1) for v in b]} nv={len(W)}")
