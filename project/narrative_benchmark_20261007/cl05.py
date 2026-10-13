import sys, json
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/colorjudge_r9')
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from colorlib import *
R = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
im = np.array(Image.open(R + 'r9/poster_1x.png').convert('RGB')).astype(float)
acc = np.load('acc_mask_1x.npy')
spec = {t[0]: t for t in json.load(open(R + 'text_spec_r9.json'))['texts']}
excl = np.zeros(acc.shape, bool)
def addbox(x0, y0, x1, y1):
    excl[max(0, int(np.floor(y0))):int(np.ceil(y1)), max(0, int(np.floor(x0))):int(np.ceil(x1))] = True
for tid in ('790:147', '790:153', '790:159', '790:165', '790:171'):
    x, y, w, h = spec[tid][1]
    addbox(x - 4, y - 4, x + w + 4, y + h + 4 + 6)  # line-2 box + underline below (+6) and +-4 margin
for tid in ('790:102', '790:105', '790:106', '790:110', '790:111'):
    x, y, w, h = spec[tid][1]
    cx, cy = x + w / 2, y + h / 2
    addbox(cx - 14.5, cy - 14.5, cx + 14.5, cy + 14.5)
out = acc & ~excl
lab, n = ndi.label(ndi.binary_dilation(out, iterations=2))
print('accent px total', acc.sum(), 'outside CORE text/disc/underline zones', out.sum())
comps = []
for i, sl in enumerate(ndi.find_objects(lab), 1):
    m = (lab[sl] == i) & out[sl]
    k = int(m.sum())
    if k == 0: continue
    ys, xs = sl
    med = np.median(im[sl][m], 0)
    comps.append((k, xs.start, ys.start, xs.stop, ys.stop, '#%02X%02X%02X' % tuple(med.astype(int))))
comps.sort(reverse=True)
for c in comps[:40]:
    print(f'{c[0]:6d} px  bbox x{c[1]}-{c[3]} y{c[2]}-{c[4]}  median {c[5]}')
print('n comps', len(comps), 'sum', sum(c[0] for c in comps))
