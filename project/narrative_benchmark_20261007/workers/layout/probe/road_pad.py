import bpy, sys, numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import world_verts, need
P = world_verts(need('R8_pantheon')); fz = P[:, 2].min(); foot = P[P[:, 2] < fz + 0.05][:, :2]
R = world_verts(need('R_core_road'))
sel = (R[:, 0] > foot[:, 0].min() - 4) & (R[:, 0] < foot[:, 0].max() + 4) & (R[:, 1] > foot[:, 1].min() - 4) & (R[:, 1] < foot[:, 1].max() + 4)
Rs = R[sel, :2]
d = np.min(np.linalg.norm(Rs[:, None, :] - foot[None, ::3, :], axis=2), axis=1) if len(Rs) else np.array([99])
print('ROADPAD n near', len(Rs), 'min ground dist road->foot', d.min() if len(d) else None, 'n within 2.3', (d < 2.3).sum())
