import sys
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/colorjudge_r9')
import numpy as np
from PIL import Image
from colorlib import *
R = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
im = np.array(Image.open(R + 'r9/poster_2x.png').convert('RGB')).astype(float)
Y = rel_lum(im)
def h(c): return '#%02X%02X%02X' % tuple(np.round(c).astype(int))
# for each left leader find the tower right edge: scan row yc, from x=300 to 330 (pt) find where luminance jumps to paper
for name, yc in (('가벼운 벽돌', 1231.9), ('중간 돌', 1258.5), ('무거운 돌', 1287), ('기초 12m+', 1308)):
    # rows of line: find darkest row in band x 318-322
    band = Y[int((yc-5)*2):int((yc+5)*2), int(318*2):int(323*2)].mean(1)
    r = int((yc-5)*2) + int(np.argmin(band))
    row = Y[r, 600:680]
    # print luminance profile along the line row and 3 px above (background)
    above = Y[r-5, 600:680]
    prof = ''.join('#' if v < 0.35 else ('+' if v < 0.6 else '.') for v in row)
    prof2 = ''.join('#' if v < 0.35 else ('+' if v < 0.6 else '.') for v in above)
    print(f'{name:10s} line row {r/2:.1f}pt  x300..340 row  {prof}')
    print(f'{"":10s} above-5px               {prof2}')
