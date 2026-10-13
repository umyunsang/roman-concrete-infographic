"""fins.py <raymask.npz> [out_prefix] - opening residuals (r = 1pt) of the object mask per box; prints components >= 1pt
and the faces under them; optional PNG with residuals in red."""
import sys, json, numpy as np
from scipy import ndimage as ndi
from PIL import Image
d = np.load(sys.argv[1])
pre = sys.argv[2] if len(sys.argv) > 2 else None
MODE = sys.argv[3] if len(sys.argv) > 3 else 'own'
nb = len([k for k in d.files if k.startswith('box')])
allfaces = {}
for b in range(nb):
    x0, x1, y0, y1, ppt = d[f'box{b}']
    m = d[f'own{b}' if MODE == 'own' else f'only{b}']; f = d[f'f{b}']
    r = int(round(ppt))
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]; disk = (xx ** 2 + yy ** 2) <= r * r
    opened = ndi.binary_opening(m, structure=disk)
    resid = m & ~opened
    lab, n = ndi.label(resid, structure=np.ones((3, 3)))
    comps = []
    for k in range(1, n + 1):
        ys, xs = np.nonzero(lab == k)
        # length = max extent (pt)
        pts = np.c_[xs, ys] / ppt
        L = float(np.max(np.linalg.norm(pts[:, None] - pts[None], axis=2))) if len(pts) < 3000 else float(np.ptp(pts, 0).max())
        if L >= 1.0:
            faces = sorted(set(f[ys, xs].tolist()) - {-1})
            comps.append({'len_pt': round(L, 2), 'px': int(len(xs)), 'at_pt': [round(x0 + xs.mean() / ppt, 1), round(y0 + ys.mean() / ppt, 1)],
                          'nfaces': len(faces), 'faces': faces[:60]})
    comps.sort(key=lambda c: -c['len_pt'])
    print('box', b, [x0, x1, y0, y1], 'mask px', int(m.sum()), 'resid comps>=1pt', len(comps), 'max', comps[0]['len_pt'] if comps else 0, '>=3pt', sum(c['len_pt'] >= 3 for c in comps))
    for c in comps[:12]:
        print('  ', {k: v for k, v in c.items() if k != 'faces'}, c['faces'][:30])
    # holes: background seen inside (own=False & only... ) -> terrain through the object: pixels where all-object hit is T_land but surrounded
    names = list(d[f'names{b}']); hit = d[f'hit{b}']
    if pre:
        img = np.zeros(m.shape + (3,), np.uint8); img[m] = (200, 170, 120); img[resid] = (255, 0, 0)
        if 'T_land' in names:
            tl = hit == names.index('T_land'); img[tl & ~m] = (60, 60, 200)
        Image.fromarray(img).save(f'{pre}_box{b}.png')
    allfaces[b] = sorted({fc for c in comps if c['len_pt'] >= 1.0 for fc in c['faces']})
json.dump({str(k): v for k, v in allfaces.items()}, open((pre or 'fins') + '_faces.json', 'w'))
