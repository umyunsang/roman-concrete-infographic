import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from colorm import lab
pre = sys.argv[1]
ov = np.asarray(Image.open(pre + '_overlay_pass.png').convert('RGBA'), float) / 255; s = ov.shape[1] / 1191
a = ov[..., 3] > 0.5
band = a[int(45 * s):int(140 * s)]
cols = band.any(0); x = np.arange(len(cols)) / s
segs = []; inside = False
for i, c in enumerate(cols):
    if c and not inside: start = x[i]; inside = True
    if not c and inside: segs.append((round(start, 1), round(x[i], 1))); inside = False
segs = [g for g in segs if g[1] - g[0] > 2]
print('segments (pt):', segs)
gate = [g for g in segs if g[1] - g[0] > 300][0]
left = [g for g in segs if g[1] <= gate[0]]; right = [g for g in segs if g[0] >= gate[1]]
for name, grp, gout in (('recipe', left, gate[0] - left[-1][1]), ('sources', right, right[0][0] - gate[1])):
    gaps = [grp[i + 1][0] - grp[i][1] for i in range(len(grp) - 1)]
    gin = max(gaps); print(name, 'gaps', [round(g, 1) for g in gaps], 'g_in', round(gin, 1), 'g_out', round(gout, 1), 'ratio', round(gout / gin, 2))
