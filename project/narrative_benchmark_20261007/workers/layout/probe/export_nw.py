import bpy, sys, numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, Terrain, world_verts, need, sample_tris, screen_tris
from mathutils import Vector
S = Screen(); TER = Terrain(need('T_land'))
def ground(pt):
    h = TER.bvh.ray_cast(*S.ray(pt))[0]; return np.array((h.x, h.y, h.z))
ROI = (260, 620, 430, 720)
out = {'M': S.M}
for n in ['COL_ruined', 'R8_pantheon', 'F_centuriatio', 'MS1_core1_to_2', 'L02_tiber', 'W_water_marks', 'R1_road_landing1', 'B_pons1', 'B_pons1_parapet0', 'B_pons1_parapet1', 'L01_gennaro', 'R3_colosseum_podium']:
    P, T = screen_tris(need(n), S); pts = sample_tris(P, T, ROI, 0.5)
    out['obs_' + n] = pts.astype(np.float32)
corners = np.array([ground(np.array(p, float)) for p in [(260, 430), (620, 430), (260, 720), (620, 720)]])
x0, x1 = corners[:, 0].min() - 2, corners[:, 0].max() + 2; y0, y1 = corners[:, 1].min() - 2, corners[:, 1].max() + 2
xs = np.arange(x0, x1, 0.25); ys = np.arange(y0, y1, 0.25)
Z = np.array([[TER.z(x, y) for x in xs] for y in ys])
out['tx'] = xs; out['ty'] = ys; out['tz'] = Z
B = world_verts(need('B_pons1')); c = B[:, :2].mean(0); U, Sg, Vt = np.linalg.svd(B[:, :2] - c); ax = Vt[0]
if ax[1] < 0: ax = -ax
out['bridge_axis'] = ax; out['bridge_c'] = c; out['bridge_proj_max'] = ((B[:, :2] - c) @ ax).max()
out['p_start'] = ground(np.array((300, 658.0))); out['p_end'] = ground(np.array((540, 516.5)))
Lw = world_verts(need('R1_road_landing1')); out['landing_c'] = Lw.mean(0); out['landing_r'] = np.linalg.norm(Lw[:, :2] - Lw[:, :2].mean(0), axis=1).max()
np.savez('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout/probe/nw_data.npz', **out)
print('EXPORTED', {k: (v.shape if hasattr(v, 'shape') else v) for k, v in out.items()})
print('start', out['p_start'], 'end', out['p_end'], 'landing', out['landing_c'], out['landing_r'], 'axis', ax, 'bridge c', c, out['bridge_proj_max'])
print('end of bridge (ground)', c + ax * out['bridge_proj_max'], S.to_pt(Vector((*(c + ax * out['bridge_proj_max']), 0))))
