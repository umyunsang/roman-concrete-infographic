import sys
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/colorjudge_r9')
import numpy as np
from PIL import Image
from colorlib import *
R = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
mp = np.array(Image.open(R + 'r9/map_only_2x.png').convert('RGB')).astype(float)
def h(c): return '#%02X%02X%02X' % tuple(np.round(c).astype(int))
def region(name, x0, y0, x1, y1, cond):
    sub = mp[int(y0*2):int(y1*2), int(x0*2):int(x1*2)].reshape(-1, 3)
    L, C, hh = np.moveaxis(rgb2oklch(sub), -1, 0)
    m = cond(L, C, hh)
    o = sub[m]; med = np.median(o, 0); c = rgb2oklch(med)
    Y = rel_lum(o); lit = o[(Y >= np.percentile(Y, 60)) & (Y <= np.percentile(Y, 90))].mean(0); cl = rgb2oklch(lit)
    print(f'{name:34s} n {m.sum():6d} median {h(med)} C {c[1]:.3f} h {c[2]:6.1f} | lit {h(lit)} C {cl[1]:.3f} h {cl[2]:6.1f}')
# frame: cool or neutral pixels (exclude warm paper/shadow)
region('CORE① RC frame', 705, 380, 890, 525, lambda L, C, h: ((h > 150) & (h < 300)) & (L < 0.8))
region('CORE① RC frame (all non-warm)', 705, 380, 890, 525, lambda L, C, h: ~((h > 30) & (h < 110) & (C > 0.012)) & (L < 0.85))
region('실험실 plate', 985, 715, 1160, 760, lambda L, C, h: (h > 150) & (h < 300) & (L < 0.9))
region('유적 관찰 tripod', 912, 1180, 930, 1215, lambda L, C, h: (h > 190) & (h < 270) & (C > 0.03))
region('lighthouse (non-water)', 40, 1385, 105, 1520, lambda L, C, h: (h > 20) & (h < 120) & (C > 0.015))
region('④→⑤ milestone column', 783, 940, 815, 1000, lambda L, C, h: (h > 40) & (h < 110) & (C > 0.015) & (L < 0.8))
