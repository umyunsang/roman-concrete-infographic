import sys
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/colorjudge_r9')
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from colorlib import *
R = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
im = np.array(Image.open(R + 'r9/poster_2x.png').convert('RGB')).astype(float)
acc = hex2rgb('983821'); accLab = rgb2lab(acc); accH = rgb2oklch(acc)[2]
def h(c): return '#%02X%02X%02X' % tuple(np.round(c).astype(int))
for name, (x0, x1, y0, y1) in {'①→② (산기슭)': (455, 520, 365, 425), '②→③ (다리 앞)': (195, 260, 912, 980), '④→⑤ (아피아 가도)': (775, 850, 912, 976)}.items():
    sub = im[y0*2:y1*2, x0*2:x1*2]
    L, C, hh = np.moveaxis(rgb2oklch(sub), -1, 0)
    board = (C >= 0.06) & (hh >= 15) & (hh <= 50)
    px = sub[board]; Y = rel_lum(px)
    lo, hi = np.percentile(Y, 60), np.percentile(Y, 90)
    lit = px[(Y >= lo) & (Y <= hi)].mean(0)
    med = np.median(px, 0)
    dl = float(de00(rgb2lab(lit), accLab)); dh = abs((rgb2oklch(lit)[2] - accH + 180) % 360 - 180)
    print(f'{name:16s} board px {board.sum():5d} median {h(med)} lit(60-90%) {h(lit)} dE00 {dl:.2f} dHue {dh:.1f}  OkLCh {np.round(rgb2oklch(lit),3)}')
# discs at 2x
for n, (x, y) in {'1': (538.5, 395.5), '2': (68, 757.5), '3': (419, 1041.6), '4': (649, 1041.6), '5': (993, 826.5)}.items():
    w = im[int((y-10)*2):int((y+10)*2), int((x-10)*2):int((x+10)*2)].reshape(-1, 3)
    yy = np.mgrid[-20:20, -20:20]; r = np.hypot(yy[0]+0.5, yy[1]+0.5).reshape(-1)
    Yw = rel_lum(w)
    d = w[(r < 19) & (Yw < 0.25)]
    med = np.median(d, 0)
    print(f'disc {n} median {h(med)} dE00 {float(de00(rgb2lab(med), accLab)):.2f}')
