import sys
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/colorjudge_r9')
import numpy as np
from PIL import Image
from colorlib import *
R = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
im = np.array(Image.open(R + 'r9/poster_1x.png').convert('RGB')).astype(float)
mp = np.array(Image.open(R + 'r9/map_only_2x.png').convert('RGB')).astype(float)[::2, ::2]
def h(c): return '#%02X%02X%02X' % tuple(np.round(c).astype(int))
def lch(c): return rgb2oklch(np.asarray(c, float))
def hdiff(a, b): return abs((a - b + 180) % 360 - 180)
print('== CL-07 concept text colours vs step pictures (map-only, 1x)')
steps = {'step1 물이 스밈': (622, 1150, 686, 1255), 'step2 칼슘 이동': (700, 1150, 765, 1255), 'step3 결정이 메움': (778, 1150, 845, 1255)}
for lname, hx in (('water #1B5760', '1B5760'), ('calcium #8A5427', '8A5427')):
    t = lch(hex2rgb(hx)); print(f'  {lname}: OkLCh {np.round(t,3)}')
    for sname, (x0, y0, x1, y1) in steps.items():
        sub = mp[y0:y1, x0:x1]
        L, C, hh = np.moveaxis(rgb2oklch(sub), -1, 0)
        m = (C >= 0.04) & (hdiff(hh, t[2]) <= 20)
        print(f'      {sname}: {m.sum():5d} px same hue group' + (f' median {h(np.median(sub[m],0))}' if m.sum() else ''))
print('== CL-08 era coding (map-only medians of object pixels, C>=0.015 & not paper)')
paper = hex2rgb('EDE1CB')
objs = {
 'CORE① RC frame (modern)': (705, 380, 890, 525),
 '오늘의 연구 drum+lens (modern)': (975, 55, 1035, 132),
 '실험실 plate only (modern)': (985, 715, 1160, 755),
 '실험실 cylinders (specimen material)': (1012, 668, 1130, 712),
 '유적 관찰 tripod (modern tool)': (918, 1175, 932, 1205),
 '해수 tank rim (concept apparatus)': (35, 1590, 125, 1660),
 'colosseum': (360, 600, 800, 900),
 'pantheon': (425, 465, 495, 545),
 'aqueduct': (830, 340, 1170, 610),
 'kiln': (85, 640, 200, 725),
 'pompeii': (775, 1385, 905, 1525),
 'lighthouse': (40, 1385, 105, 1520),
 'books 로마 때 기록': (873, 52, 905, 138),
 'struct tower': (262, 1185, 330, 1320),
 'milestone columns': (460, 395, 500, 455),
 'mountains': (240, 260, 470, 400),
 'volcano': (910, 1250, 1170, 1520),
}
for name, (x0, y0, x1, y1) in objs.items():
    sub = mp[y0:y1, x0:x1].reshape(-1, 3)
    d = de76(rgb2lab(sub), rgb2lab(paper))
    o = sub[d > 8]
    med = np.median(o, 0); c = lch(med)
    print(f'  {name:36s} n {len(o):6d} median {h(med)} OkL {c[0]:.3f} C {c[1]:.3f} h {c[2]:6.1f}')
print('== CL-09/10 water')
water = np.load('water_mask_1x.npy')
yy, xx = np.mgrid[0:im.shape[0], 0:im.shape[1]]
L, C, hh = np.moveaxis(rgb2oklch(mp), -1, 0)
clean = water & (C >= 0.02) & (L > 0.6)
river = clean & (yy < 1300) & (xx < 400)
sea = clean & (yy > 1500) & (xx > 450)
rv, se = np.median(mp[river], 0), np.median(mp[sea], 0)
print(f'  river median {h(rv)} OkLCh {np.round(lch(rv),3)} | sea median {h(se)} OkLCh {np.round(lch(se),3)} | dE00 {float(de00(rgb2lab(rv), rgb2lab(se))):.2f}')
for name, (x0, y0, x1, y1) in {'④ drops+crack water (step1)': (640, 1150, 670, 1215), '⑤ puddle (no-lime cylinder)': (1085, 735, 1125, 760), '해수 tank water': (35, 1590, 125, 1660)}.items():
    sub = mp[y0:y1, x0:x1]
    Ls, Cs, hs = np.moveaxis(rgb2oklch(sub), -1, 0)
    m = (Cs >= 0.04) & (hs >= 170) & (hs <= 240)
    med = np.median(sub[m], 0)
    print(f'  {name:30s} n {m.sum():4d} median {h(med)} OkLCh {np.round(lch(med),3)}')
print('== CL-20 rendered paper mode')
q = (im // 2).astype(int)
key = q[..., 0] * 65536 + q[..., 1] * 256 + q[..., 2]
vals, cnts = np.unique(key, return_counts=True)
top = vals[np.argsort(-cnts)[:5]]
for v, c in zip(top, np.sort(cnts)[::-1][:5]):
    rgb = np.array([v // 65536, (v // 256) % 256, v % 256]) * 2 + 0.5
    print(f'  mode bin {h(rgb)} count {c} ({c/key.size*100:.2f}%) dE00 vs #F3E8D4 {float(de00(rgb2lab(rgb), rgb2lab(hex2rgb("F3E8D4")))):.2f}')
