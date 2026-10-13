import numpy as np, sys
d = np.load(sys.argv[1]); lab = np.load(sys.argv[2]); cen = d['cen']
orange = np.isin(lab, [0, 4])
sel = orange & (cen[:, 1] < -0.05) & (cen[:, 2] > -0.2) & (cen[:, 2] < 0.6)
a = cen[sel]
print('front orange faces', sel.sum())
# top view ascii x horizontal (-0.45..0.45), y vertical (-0.5..0.1) for z slices
for z0 in np.arange(-0.15, 0.55, 0.1):
    m = (a[:, 2] >= z0) & (a[:, 2] < z0 + 0.1)
    print(f'--- z {z0:.2f}..{z0+0.1:.2f}  n={m.sum()}  (x horiz -0.45..0.45, rows y from -0.5 top to 0.1 bottom)')
    n = 36; H = np.zeros((16, n), int)
    i = ((a[m, 0] + 0.45) / 0.9 * n).astype(int); j = ((a[m, 1] + 0.5) / 0.6 * 16).astype(int)
    ok = (i >= 0) & (i < n) & (j >= 0) & (j < 16); np.add.at(H, (j[ok], i[ok]), 1)
    for row in H: print(''.join('#' if v > 30 else ('+' if v > 5 else ('.' if v > 0 else ' ')) for v in row))
