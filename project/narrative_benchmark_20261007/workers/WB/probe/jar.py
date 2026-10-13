import numpy as np, sys
d = np.load(sys.argv[1]); lab = np.load(sys.argv[2]); cen = d['cen']; area = d['area']
orange = np.isin(lab, [0, 4]); cream = np.isin(lab, [2, 3]); dark = np.isin(lab, [1, 5])
# front view (x,z) occupancy maps for orange faces, ascii
def ascii(mask, ax0, ax1, r0, r1, n=60):
    H = np.zeros((n, n), int)
    a = cen[mask]
    i = ((a[:, ax0] - r0[0]) / (r0[1] - r0[0]) * n).astype(int); j = ((a[:, ax1] - r1[0]) / (r1[1] - r1[0]) * n).astype(int)
    ok = (i >= 0) & (i < n) & (j >= 0) & (j < n)
    np.add.at(H, (n - 1 - j[ok], i[ok]), 1)
    return H
for nm, m in [('orange', orange), ('cream', cream), ('dark', dark)]:
    print('==', nm, 'side view (y horizontal, z vertical)')
    H = ascii(m, 1, 2, (-0.5, 0.5), (-1, 1), 50)
    for row in H[::2]: print(''.join('#' if v > 20 else ('+' if v > 3 else ('.' if v > 0 else ' ')) for v in row))
