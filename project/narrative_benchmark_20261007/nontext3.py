import sys
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/colorjudge_r9')
import numpy as np
from PIL import Image
from colorlib import *
R = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
im = np.array(Image.open(R + 'r9/poster_2x.png').convert('RGB')).astype(float)
def h(c): return '#%02X%02X%02X' % tuple(np.round(c).astype(int))
def win(name, x0, y0, x1, y1):
    w = im[int(y0*2):int(y1*2), int(x0*2):int(x1*2)].reshape(-1, 3)
    Y = rel_lum(w)
    dark = w[Y <= np.percentile(Y, 3)].mean(0); med = np.median(w, 0)
    print(f'{name:28s} pt({x0},{y0})-({x1},{y1}) dark3% {h(dark)} median {h(med)} WCAG {float(wcag(dark, med)):.2f}')
    return float(wcag(dark, med))
win('L 가벼운 벽돌', 314.5, 1228, 320, 1234)
win('L 중간 돌', 316, 1254.5, 328, 1262)
win('L 무거운 돌', 316, 1283, 324.5, 1290)
win('L 기초 12m+', 318.5, 1304, 323.5, 1311)
# number discs: window 2x disc diameter centred on numeral
for n, (x, y) in {'1': (538.5, 395.5), '2': (68, 757.5), '3': (419, 1041.6), '4': (649, 1041.6), '5': (993, 826.5)}.items():
    w = im[int((y-15)*2):int((y+15)*2), int((x-15)*2):int((x+15)*2)].reshape(-1, 3)
    Yw = rel_lum(w)
    disc = w[(Yw < 0.25)]
    print(f'disc {n}: disc median {h(np.median(disc,0))} n {len(disc)} window median {h(np.median(w,0))} dark3% {h(w[Yw<=np.percentile(Yw,3)].mean(0))} WCAG(dark3 vs med) {float(wcag(w[Yw<=np.percentile(Yw,3)].mean(0), np.median(w,0))):.2f} WCAG(disc med vs win med) {float(wcag(np.median(disc,0), np.median(w,0))):.2f}')
