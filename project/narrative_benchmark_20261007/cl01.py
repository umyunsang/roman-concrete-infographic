import sys
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/colorjudge_r9')
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from colorlib import *
R = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
im = np.array(Image.open(R + 'r9/poster_1x.png').convert('RGB')).astype(float)
H, W = im.shape[:2]; N = H * W
L, C, hh = np.moveaxis(rgb2oklch(im), -1, 0)
# water: cyan hue, closed + filled, keep large comps
w0 = (hh >= 160) & (hh <= 230) & (C >= 0.02) & (L > 0.6)
w1 = ndi.binary_closing(w0, iterations=3)
lab, n = ndi.label(w1)
sizes = ndi.sum(w1, lab, range(1, n + 1))
keep = np.isin(lab, 1 + np.where(sizes > 3000)[0])
water = ndi.binary_fill_holes(keep)
print('water area %.2f%%' % (water.mean() * 100), 'comps kept', (sizes > 3000).sum())
sel = (C >= 0.015) & (C <= 0.05)
for name, m in (('all pixels (literal)', sel), ('excluding water region', sel & ~water)):
    hs = hh[m]
    print(f'{name:26s} n={m.sum():8d} hue p10 {np.percentile(hs,10):6.1f} p90 {np.percentile(hs,90):6.1f} width {np.percentile(hs,90)-np.percentile(hs,10):6.1f}')
# share of non-water low-chroma pixels outside 60-110
hs = hh[sel & ~water]
print('non-water low-C hue histogram (10deg bins, % of those px):')
b = np.bincount((hs // 10).astype(int), minlength=36) / len(hs) * 100
print('  ' + ' '.join(f'{i*10}:{v:.1f}' for i, v in enumerate(b) if v >= 0.3))
Image.fromarray((water * 255).astype(np.uint8)).save('water_mask_1x.png')
np.save('water_mask_1x.npy', water)
print('C<=0.05 frac excl water %.3f' % ((C[~water] <= 0.05).mean()))
