import numpy as np, sys
from scipy import ndimage as ndi
d = np.load(sys.argv[1]); names = list(d['names']); mats = list(d['mats']); sp = float(d['sp'][0]); ox, oy = d['origin_px']
om, oo, mm = d['obj_map'], d['obj_ovl'], d['mat_map']
c2 = names.index('C2_hot_mixing')
disc = (om == c2) & np.isin(mm, [mats.index(m) for m in ['RC.v12.roman_stone', 'RC.v12.basin', 'RC.v12.mixture']])
disc = ndi.binary_closing(disc, iterations=3)
field = om == names.index('F_centuriatio')
ms2 = np.isin(om, [i for i, n in enumerate(names) if n.startswith('MS2')])
cube = np.isin(om, [i for i, n in enumerate(names) if n == 'D2_cube' or (n.startswith('D2_lime') and n != 'D2_lime_kiln')])
road = np.isin(om, [i for i, n in enumerate(names) if n.startswith(('R_', 'R1_', 'R4_bridge', 'B_pons'))])
H, Wd = om.shape
yy, xx = np.mgrid[0:H, 0:Wd]; Xpt = (xx + ox) / sp; Ypt = (yy + oy) / sp
print('disc bbox', Xpt[disc].min(), Xpt[disc].max(), Ypt[disc].min(), Ypt[disc].max())
dt = {k: ndi.distance_transform_edt(~m) / sp for k, m in [('field', field), ('ms2', ms2), ('cube', cube), ('road', road)]}
# bottom edge profile of disc
for x in [95, 100, 105, 110, 115, 120, 125, 130, 140]:
    col = disc[:, int(round(x * sp - ox))]
    ys = np.nonzero(col)[0]
    print('x', x, 'disc y range', round((ys.min() + oy) / sp, 1), round((ys.max() + oy) / sp, 1))
for dxp, dyp in [(0, 0), (0, -5), (0, -8), (0, -10), (0, -12), (2, -10), (3, -12), (4, -14), (0, -15)]:
    sh = np.roll(np.roll(disc, int(round(dyp * sp)), 0), int(round(dxp * sp)), 1)
    out = {k: round(float(v[sh].min()), 2) for k, v in dt.items()}
    print('shift', dxp, dyp, out, 'top y', round(Ypt[sh].min(), 1))
