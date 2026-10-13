"""L* stats / heatmap of terrain windows from a map-pass PNG (full poster frame).
usage: lstar.py <map_pass.png> <out_prefix> name:x0,x1,y0,y1 ...  [--mask idmask.npz]"""
import sys, json
import numpy as np
from PIL import Image
def srgb2lin(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def lstar(rgb):
    lin = srgb2lin(rgb.astype(np.float64))
    Y = lin @ np.array([0.2126, 0.7152, 0.0722])
    f = np.where(Y > 216 / 24389, np.cbrt(Y), (24389 / 27 * Y + 16) / 116)
    return 116 * f - 16
args = [a for a in sys.argv[1:] if not a.startswith('--')]
im = Image.open(args[0]).convert('RGB'); A = np.asarray(im); s = im.width / 1191
mask = None
if '--mask' in sys.argv:
    mask = np.load(sys.argv[sys.argv.index('--mask') + 1])
out = {}
for spec in args[2:]:
    n, b = spec.split(':'); x0, x1, y0, y1 = map(float, b.split(','))
    c = A[round(y0 * s):round(y1 * s), round(x0 * s):round(x1 * s)]
    Lm = lstar(c)
    sel = np.ones(Lm.shape, bool)
    if mask is not None and n in mask:
        m = mask[n]
        if m.shape == Lm.shape: sel = m
    v = Lm[sel]
    out[n] = {'mean': round(float(v.mean()), 2), 'p50': round(float(np.percentile(v, 50)), 2), 'p99': round(float(np.percentile(v, 99)), 2),
              'frac_ge95': round(float((v >= 95).mean()), 4), 'n': int(v.size)}
    # heatmap: grey L*, red where >= 95
    g = np.clip((Lm - 80) / 20, 0, 1)
    rgb = np.stack([g, g, g], -1)
    rgb[Lm >= 95] = (1, 0, 0)
    rgb[~sel] = (0.2, 0.4, 0.8)
    Image.fromarray((rgb * 255).astype(np.uint8)).resize((c.shape[1] * 2, c.shape[0] * 2), Image.NEAREST).save(f'{args[1]}_{n}.png')
print(json.dumps(out))
