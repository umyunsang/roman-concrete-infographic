import bpy, sys, json
import numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts
S = Screen(); land = bpy.data.objects['T_land']; A = world_verts(land)
with bpy.data.libraries.load(sys.argv[sys.argv.index('--') + 1], link=False) as (src, dst):
    dst.meshes = [land.data.name]
co = np.empty(len(dst.meshes[0].vertices) * 3); dst.meshes[0].vertices.foreach_get('co', co); B = co.reshape(-1, 3)
dz = A[:, 2] - B[:, 2]; ch = np.nonzero(np.abs(dz) > 1e-6)[0]
pod = world_verts(bpy.data.objects['R3_colosseum_podium'])[:, :2]; ms3 = world_verts(bpy.data.objects['MS3_core34_to_5'])[:, :2][::5]
for name, ref in (('podium', pod), ('MS3', ms3)):
    d = np.sqrt(((B[ch][:, None, :2] - ref[None]) ** 2).sum(-1)).min(1)
    for r in (2, 3, 4, 6):
        m = d < r
        print(name, 'within', r, 'changed', int(m.sum()), 'max drop', round(float(-dz[ch][m].min()), 4) if m.any() else 0)
P = S.project(B[ch])
m = (P[:, 0] > 500) & (P[:, 0] < 740) & (P[:, 1] < 1004)
print('A north of road (y<1004): changed', int(m.sum()), 'max drop', round(float(-dz[ch][m].min()), 4) if m.any() else 0)
