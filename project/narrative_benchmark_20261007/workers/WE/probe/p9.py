import bpy, sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from welib import *
S = Screen(); L = Land()
np.set_printoptions(suppress=True, precision=3, linewidth=220)
for name in ['R_core_road', 'R_via_appia']:
    o = bpy.data.objects[name]
    W, lab, flab, ls, lt, lv = face_islands(o)
    n = lab.max() + 1
    nf = np.bincount(flab, minlength=n)
    zt = np.array([W[lab == k, 2].max() for k in range(n)]); zb = np.array([W[lab == k, 2].min() for k in range(n)])
    cen = np.array([W[lab == k].mean(0) for k in range(n)])
    pav = nf < 40
    print(name, 'islands', n, 'paving', pav.sum(), 'kerb', (~pav).sum(), 'nf hist', np.unique(nf[pav], return_counts=True))
    h = zt[pav] - zb[pav]
    print(' paver height pct', np.percentile(h, [1, 10, 50, 90, 99]).round(3))
    # sample 300 pavers: terrain below center vs bottom
    idx = np.nonzero(pav)[0][::max(1, pav.sum() // 600)]
    tz = L.zs(cen[idx, :2])
    gap = zb[idx] - tz
    print(' paver bottom - terrain pct', np.nanpercentile(gap, [1, 5, 25, 50, 75, 95, 99]).round(3), 'nan', np.isnan(gap).sum())
    # kerb heights
    kz = [(W[lab == k, 2].max() - W[lab == k, 2].min()) for k in np.nonzero(~pav)[0]]
    print(' kerb islands nf', nf[~pav].tolist())
    # joint width estimate: nearest-neighbour distance between paver centers vs paver extent
    k5 = np.nonzero(pav & (nf == 5))[0][:400]
    ext = np.array([np.ptp(W[lab == k, :2], axis=0) for k in k5])
    print(' 5-face paver xy extent pct', np.percentile(ext, [10, 50, 90], axis=0).round(3))
    # first 5-face paver: vertices
    k = k5[0]; print(' sample paver verts', W[lab == k].round(3))
