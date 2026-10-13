import bpy, sys
import numpy as np
W='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work'
sys.path.insert(0, W+'/workers/layout')
from common import Screen, world_verts
S=Screen()
o=bpy.data.objects['S_pin_harbor']; P=S.project(world_verts(o))
for f in o.data.polygons: print(f.index, [tuple(np.round(P[v],2)) for v in f.vertices])
o=bpy.data.objects['S_pin_pompeii']; P=S.project(world_verts(o)); print('pompeii', len(o.data.polygons), np.round(P[:8],2))
b=bpy.data.objects['H_gate_body']; me=b.data
co=np.array([v.co[:] for v in me.vertices])
mask=np.abs(co[:,0])<0.02
print('x~0 verts', np.round(co[mask],3))
for m in bpy.data.materials:
    if m.name in ('RC.v12.base_badge_2','RC.v12.base_header_surface','RC.v12.linen'):
        print(m.name, m.use_nodes, tuple(round(c,4) for c in m.diffuse_color), m.roughness, m.metallic, [n.type for n in m.node_tree.nodes] if m.node_tree else None)
