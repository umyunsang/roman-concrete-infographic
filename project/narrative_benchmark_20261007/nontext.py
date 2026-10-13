import sys
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/colorjudge_r9')
import numpy as np
from PIL import Image
from colorlib import *
R = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
im = np.array(Image.open(R + 'r9/poster_2x.png').convert('RGB')).astype(float)
Yall = rel_lum(im)
def h(c): return '#%02X%02X%02X' % tuple(np.round(c).astype(int))
def win(name, x0, y0, x1, y1):
    w = im[int(y0*2):int(y1*2), int(x0*2):int(x1*2)].reshape(-1, 3)
    Y = rel_lum(w)
    dark = w[Y <= np.percentile(Y, 3)].mean(0)
    med = np.median(w, 0)
    print(f'{name:34s} win pt({x0},{y0})-({x1},{y1}) dark3% {h(dark)} median {h(med)} WCAG {float(wcag(dark, med)):.2f}')
# locate struct leader rows: dark rows in x 306..316
for x0, x1 in ((306, 316), (360, 372)):
    sub = Yall[int(1220*2):int(1315*2), int(x0*2):int(x1*2)].mean(1)
    rows = [1220 + i/2 for i in np.argsort(sub)[:12]]
    print('struct dark rows', x0, sorted(rows))
win('load arrows (shafts)', 279, 1187, 298, 1203)
win('seq arrow 1->2', 683, 1203, 701, 1217)
win('seq arrow 2->3', 761, 1200, 779, 1214)
win('grain leader', 128, 1003, 141, 1011)
win('harbor dashed leader (water)', 202, 1499, 220, 1516)
win('pompeii dashed leader land', 719, 1497, 727, 1512)
win('pompeii dashed leader water', 719, 1530, 727, 1545)
win('pompeii dashed leader coast', 719, 1512, 727, 1530)
