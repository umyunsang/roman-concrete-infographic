import bpy, sys, numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, Terrain, world_verts, need
from mathutils import Vector
S = Screen(); T = Terrain(need('T_land'))
P = world_verts(need('R8_pantheon')); zmin = P[:, 2].min(); foot = P[P[:, 2] < zmin + 0.05]
print('foot z', zmin, 'n', len(foot), 'xy box', foot[:, 0].min(), foot[:, 0].max(), foot[:, 1].min(), foot[:, 1].max())
c = P[:, :2].mean(0); print('centre', c, 'model bbox', P.min(0), P.max(0))
xs = np.linspace(P[:, 0].min() - 3, P[:, 0].max() + 3, 13); ys = np.linspace(P[:, 1].min() - 3, P[:, 1].max() + 3, 13)
np.set_printoptions(linewidth=220, precision=2, suppress=True)
G = np.array([[T.z(x, y) - zmin for x in xs] for y in ys[::-1]]); print('terrain - foot z (rows: y high->low, cols x low->high)'); print('xs', xs.round(1)); print('ys', ys[::-1].round(1)); print(G)
# plane fit of terrain under footprint
F = np.array([(x, y, T.z(x, y)) for x, y in foot[::5, :2]]); A = np.c_[F[:, :2], np.ones(len(F))]; coef = np.linalg.lstsq(A, F[:, 2], rcond=None)[0]
print('terrain slope under foot dz/dx %.3f dz/dy %.3f  (rise %.2f over footprint)' % (coef[0], coef[1], F[:, 2].max() - F[:, 2].min()))
# terrain verts within footprint+3
L_ = world_verts(need('T_land')); m = (L_[:, 0] > P[:, 0].min() - 3) & (L_[:, 0] < P[:, 0].max() + 3) & (L_[:, 1] > P[:, 1].min() - 3) & (L_[:, 1] < P[:, 1].max() + 3)
print('terrain verts near', m.sum())
for n in ['MS1_core1_to_2', 'R_core_road', 'F_centuriatio', 'R1_road_landing1']:
    W = world_verts(need(n)); d = np.min(np.linalg.norm(W[:, None, :2][::max(1, len(W)//3000)] - foot[None, ::10, :2], axis=2))
    print('ground distance foot ->', n, round(float(d), 2))
