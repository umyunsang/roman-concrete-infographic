import sys, json; sys.path.insert(0, sys.argv[1])
from wf_common import *
inv, objs, name2id, final, pxpt, f2, assets = load_ids()
po, mo, paper, ink, txt = load_maps(sys.argv[1] + '/poster_2x_after.png')
spec = {t[0]: t for t in json.load(open(RL + '/text_spec_r12.json'))['texts']}
lum = np.array([0.299, 0.587, 0.114]); pL = paper @ lum
for tid in ('790:103', '797:80', '790:193'):
    g = glyph_pts(txt, spec[tid][1], 1.0)
    # ground pixels flagged by the pixel rule within 4pt of the glyphs
    m = np.zeros(ink.shape, bool); m[g[:, 1], g[:, 0]] = True
    from scipy.ndimage import binary_dilation
    ring = binary_dilation(m, iterations=8) & ~m
    sel = ring & ink & ~txt
    ids = f2[sel]; L = (mo[sel] @ lum) - pL
    names = {}
    for i in np.unique(ids): names[objs[i - 1] if i else 'none'] = int((ids == i).sum())
    print(tid, 'px-rule ink within 4pt:', int(sel.sum()), 'by id', names, 'dLuma pct', np.percentile(L, [0, 50, 100]).round(1).tolist() if len(L) else None)
