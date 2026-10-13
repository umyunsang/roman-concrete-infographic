import os
import sys, pickle
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/WC/meas/c')
from m import *
from parts import stats
OUT = os.environ.get('WC_OUT', '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/WC/meas/c/out')
# own pickles written by parts.py in this scratchpad (trusted)
def load(aid):
    return pickle.load(open(f'{OUT}/seg_{aid}.pkl', 'rb'))

def objmask(seg, names):
    return np.isin(seg['O'], names) & seg['mask']

def lit_of(seg, m, erode=True):
    s = seg['s']; rgb = seg['rgb']
    inner = ndi.binary_erosion(m, iterations=int(round(1.5 * s))) if erode else m
    if inner.sum() < 68: inner = ndi.binary_erosion(m, iterations=2)
    if inner.sum() < 10: inner = m
    px = rgb[inner]; Ls = lab(px)[:, 0]
    lo, hi = np.percentile(Ls, 60), np.percentile(Ls, 90)
    sel = (Ls >= lo) & (Ls <= hi)
    return px[sel].mean(0)

def pair(name, c1, c2, deg):
    l1, l2 = lab(c1), lab(c2)
    out = [f'{name}: {hx(c1)} vs {hx(c2)} dE00 {float(de00(l1, l2)):.1f} D({deg}) {Dsz(l1, l2, deg):.2f}']
    for k in ('protan', 'deutan', 'tritan'):
        out.append(f'{k[0]} {Dsz(lab(cvd(c1, k)), lab(cvd(c2, k)), deg):.2f}')
    print(' | '.join(out))

def part_lit(seg, key):
    j = [i for i, mn in enumerate(seg['mlist']) if key in mn][0]
    return lit_of(seg, seg['P'] == j)

def white_p95(seg, m):
    return float(np.percentile(lab(seg['rgb'][m])[:, 0], 95))

def darkest_face_median(seg, m):
    L = lab(seg['rgb'][m])[:, 0]
    # 3-means on L*
    c = np.percentile(L, [15, 50, 85])
    for _ in range(30):
        a = np.argmin(np.abs(L[:, None] - c[None]), 1)
        c = np.array([np.median(L[a == i]) if (a == i).any() else c[i] for i in range(3)])
    sizes = [(a == i).sum() for i in range(3)]
    return sorted(zip(c, sizes))

print('accent lab', ACCLAB)
