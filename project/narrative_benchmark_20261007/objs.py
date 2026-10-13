import sys
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/colorjudge_r9')
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from colorlib import *
R = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
im = np.array(Image.open(R + 'r9/map_only_2x.png').convert('RGB')).astype(float)[::2, ::2]  # 1x sampling of text-free map
L, C, hh = np.moveaxis(rgb2oklch(im), -1, 0)
m = (C >= 0.04) & (hh >= 15) & (hh <= 60) & (L < 0.75)
lab, n = ndi.label(ndi.binary_closing(m, iterations=1))
acc_lab = rgb2lab(hex2rgb('983821'))
rows = []
for i, sl in enumerate(ndi.find_objects(lab), 1):
    mm = (lab[sl] == i) & m[sl]
    k = mm.sum()
    if k < 150: continue
    px = im[sl][mm]
    med = np.median(px, 0)
    lch = rgb2oklch(med)
    d = float(de00(rgb2lab(med), acc_lab))
    ys, xs = sl
    rows.append((k, xs.start, xs.stop, ys.start, ys.stop, '#%02X%02X%02X' % tuple(med.astype(int)), lch[0], lch[1], lch[2], d))
rows.sort(key=lambda r: -r[0])
for r in rows[:40]:
    print(f'{r[0]:6d}px x{r[1]}-{r[2]} y{r[3]}-{r[4]} median {r[5]} OkL {r[6]:.3f} C {r[7]:.3f} h {r[8]:5.1f}  dE00 vs #983821 {r[9]:.1f}')
