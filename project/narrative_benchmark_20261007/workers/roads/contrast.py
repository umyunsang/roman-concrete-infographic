"""contrast.py <render_prefix> <mask.png> <out.json>
Plate (red mask) vs the road pixels right around it (paving = green mask, kerb = blue mask), measured on the real
composite (map + overlay). Ring = 2..14 px (1..7 pt) outside the plate, pixels covered by the overlay pass skipped.
Plate colour = median of the plate interior (mask eroded 1 px). WCAG 2 contrast with sRGB relative luminance."""
import sys, json
import numpy as np
from PIL import Image, ImageFilter
pre, mp, outp = sys.argv[1:4]
mp_ = Image.open(pre + '_map_pass.png').convert('RGBA'); ovp = Image.open(pre + '_overlay_pass.png').convert('RGBA')
A = np.asarray(Image.alpha_composite(mp_, ovp).convert('RGB')).astype(float) / 255
ov = np.asarray(ovp)[..., 3] > 0
M = np.asarray(Image.open(mp).convert('RGB')).astype(int)
assert M.shape[:2] == A.shape[:2], (M.shape, A.shape)
red = (M[..., 0] > 128) & (M[..., 1] < 100) & (M[..., 2] < 100)
pave = (M[..., 1] > 128) & (M[..., 0] < 100) & (M[..., 2] < 100)
kerb = (M[..., 2] > 128) & (M[..., 0] < 100) & (M[..., 1] < 100)
def lin(c): return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def Y(c): return lin(c) @ np.array([0.2126, 0.7152, 0.0722])
def Ls(y): return float(116 * np.cbrt(y) - 16) if y > 216 / 24389 else float(24389 / 27 * y)
def cr(a, b): return round((max(a, b) + 0.05) / (min(a, b) + 0.05), 2)
def hexs(c): return '#%02X%02X%02X' % tuple(int(round(v * 255)) for v in c)
def grow(m, r):
    im = Image.fromarray((m * 255).astype(np.uint8)); return np.asarray(im.filter(ImageFilter.MaxFilter(2 * r + 1))) > 0
def shrink(m, r):
    im = Image.fromarray((m * 255).astype(np.uint8)); return np.asarray(im.filter(ImageFilter.MinFilter(2 * r + 1))) > 0
s = A.shape[1] / 1191
# split plates by screen region (three milestones far apart): label by connected bbox clusters on a coarse grid
ys, xs = np.nonzero(red); R = {'render': pre, 'mask': mp, 'px_per_pt': round(s, 3), 'plates': {}}
pts = np.stack([xs, ys], 1) / s
clusters = []
for p in pts[::50]:
    for c in clusters:
        if np.linalg.norm(c['c'] - p) < 120: c['n'] += 1; c['c'] += (p - c['c']) / c['n']; break
    else: clusters.append({'c': p.copy(), 'n': 1})
for c in clusters:
    cx, cy = c['c']; x0, x1 = int((cx - 90) * s), int((cx + 90) * s); y0, y1 = int((cy - 90) * s), int((cy + 90) * s)
    sub = np.zeros_like(red); sub[max(y0, 0):y1, max(x0, 0):x1] = True
    plate = red & sub; inner = shrink(plate, 1) & ~ov
    ring = grow(plate, 14) & ~grow(plate, 2) & ~ov
    e = {'centre_pt': [round(float(cx), 1), round(float(cy), 1)], 'plate_px': int(plate.sum())}
    if inner.sum() < 20: R['plates'][str(e['centre_pt'])] = e; continue
    yp = Y(A[inner]); e['plate_median'] = hexs(np.median(A[inner], 0)); e['plate_Y_p50'] = round(float(np.median(yp)), 4)
    e['plate_Y_p90'] = round(float(np.percentile(yp, 90)), 4); e['plate_Lstar_p50'] = round(Ls(np.median(yp)), 1)
    for nm, m in (('paving', pave), ('kerb', kerb)):
        rr = ring & m
        if rr.sum() < 10: e[nm] = {'ring_px': int(rr.sum())}; continue
        yr = Y(A[rr])
        e[nm] = {'ring_px': int(rr.sum()), 'median': hexs(np.median(A[rr], 0)), 'Y_p50': round(float(np.median(yr)), 4),
                 'Lstar_p50': round(Ls(np.median(yr)), 1), 'Lstar_p10': round(Ls(np.percentile(yr, 10)), 1),
                 'contrast_p50_vs_plate_p50': cr(np.median(yr), np.median(yp)),
                 'contrast_road_p10_vs_plate_p50': cr(np.percentile(yr, 10), np.median(yp)),
                 'contrast_road_p50_vs_plate_p90': cr(np.median(yr), np.percentile(yp, 90)),
                 'frac_ring_px_ge_3to1_vs_plate_p50': round(float(((yr + 0.05) / (np.median(yp) + 0.05) >= 3).mean()), 3)}
    R['plates'][str(e['centre_pt'])] = e
open(outp, 'w').write(json.dumps(R, indent=1)); print(json.dumps(R, indent=1))
