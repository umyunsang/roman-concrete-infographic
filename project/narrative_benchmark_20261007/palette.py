import sys, json
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/colorjudge_r9')
import numpy as np
from PIL import Image
from colorlib import *
R = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
im = np.array(Image.open(R + 'r9/poster_1x.png').convert('RGB')).astype(float)
H, W = im.shape[:2]
lch = rgb2oklch(im)
L, C, hh = lch[..., 0], lch[..., 1], lch[..., 2]
N = H * W
print('CL-01 C<=0.05 frac', (C <= 0.05).mean())
sel = (C >= 0.015) & (C <= 0.05)
hs = hh[sel]
# circular-safe: rotate so that the gap is at the wrap
p10, p90 = np.percentile(hs, 10), np.percentile(hs, 90)
print('   0.015<=C<=0.05 hue p10 %.1f p90 %.1f width %.1f  (n=%d)' % (p10, p90, p90 - p10, sel.sum()))
hs2 = (hs + 180) % 360
print('   rotated check width %.1f' % (np.percentile(hs2, 90) - np.percentile(hs2, 10)))
# CL-02 chromatic groups
chrom = C >= 0.05
bins = (hh[chrom] // 15).astype(int)
cnt = np.bincount(bins, minlength=24)
print('CL-02 C>=0.05 frac %.4f' % chrom.mean())
for i, c in enumerate(cnt):
    if c: print(f'   bin {i*15:3d}-{i*15+15:3d}: {c:7d} px {c/N*100:6.3f}%')
# merge adjacent nonzero bins into groups (circular)
occ = cnt > 0
groups = []
i = 0
visited = [False] * 24
for s in range(24):
    if occ[s] and not occ[(s - 1) % 24]:
        g = []; k = s
        while occ[k % 24] and not visited[k % 24]:
            visited[k % 24] = True; g.append(k % 24); k += 1
        groups.append(g)
if all(occ): groups = [list(range(24))]
for g in groups:
    a = sum(cnt[k] for k in g)
    print('   group hue %d-%d area %.3f%%' % (g[0]*15, g[-1]*15+15, a / N * 100))
print('CL-03 C>0.15 frac %.4f%%' % ((C > 0.15).mean() * 100))
acc = (hh >= 20) & (hh <= 48) & (C >= 0.10)
print('CL-04 accent-family frac %.4f%% (%d px)' % (acc.mean() * 100, acc.sum()))
np.save('acc_mask_1x.npy', acc)
