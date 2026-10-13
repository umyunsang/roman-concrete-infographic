import sys
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/colorjudge_r9')
import numpy as np
from PIL import Image, ImageCms
from colorlib import *
R = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
im = np.array(Image.open(R + 'r9/poster_2x.png').convert('RGB')).astype(float)
mp = np.array(Image.open(R + 'r9/map_only_2x.png').convert('RGB')).astype(float)
def h(c): return '#%02X%02X%02X' % tuple(np.round(c).astype(int))
# underline under CORE line 2: search rows below each line-2 box
for tid, (x, y, w, hh) in {'147': (528, 406.5, 174, 24.5), '153': (57.5, 768.5, 160, 24.5), '159': (408.5, 1052.5, 190, 24.5), '165': (638.5, 1052.5, 178, 24.5), '171': (982.5, 837.5, 180, 24.5)}.items():
    y0 = int((y + hh) * 2); win = im[y0:y0 + 16, int((x + 20) * 2):int((x + 100) * 2)].reshape(-1, 3)
    Y = rel_lum(win); dark = win[Y <= np.percentile(Y, 3)].mean(0); med = np.median(win, 0)
    print(f'underline {tid}: dark3% {h(dark)} median {h(med)} WCAG {float(wcag(dark, med)):.2f}')
# reddish cloth on figures (non-CORE): pixels h 20-48, C>=0.06 in figure areas, map-only
acc = rgb2lab(hex2rgb('983821'))
for name, (x0, y0, x1, y1) in {'mixing-pit figures': (125, 860, 190, 905), 'ruin observation figures': (900, 1170, 950, 1215), 'pompeii site figure/props': (680, 1430, 760, 1500)}.items():
    sub = mp[y0*2:y1*2, x0*2:x1*2].reshape(-1, 3)
    L, C, hh = np.moveaxis(rgb2oklch(sub), -1, 0)
    m = (hh >= 20) & (hh <= 48) & (C >= 0.06)
    if m.sum() == 0: print(name, 'none'); continue
    md = np.median(sub[m], 0)
    print(f'{name:26s} n2x {m.sum():4d} median {h(md)} OkLCh {np.round(rgb2oklch(md),3)} dE00 vs #983821 {float(de00(rgb2lab(md), acc)):.1f}')
# TAC>300 pixel count (BPC off)
PSO = ImageCms.getOpenProfile('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/icc/pso/PSOcoated_v3.icc')
t = ImageCms.buildTransform(ImageCms.createProfile('sRGB'), PSO, 'RGB', 'CMYK', ImageCms.Intent.RELATIVE_COLORIMETRIC)
cm = np.array(ImageCms.applyTransform(Image.open(R + 'r9/poster_1x.png').convert('RGB'), t)).astype(int)
tac = cm.sum(-1)
print('BPC off: TAC codes max', tac.max(), '(765 = 300%)  px >765:', int((tac > 765).sum()), ' K code max', cm[..., 3].max(), '(244.8 = 96%) px K>245:', int((cm[..., 3] > 245).sum()))
pure = Image.fromarray(np.array([[[0, 0, 0]]], np.uint8))
print('sRGB #000000 -> CMYK codes (BPC off)', np.array(ImageCms.applyTransform(pure, t)).tolist())
