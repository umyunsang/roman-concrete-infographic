"""measure.py <render_prefix> <samples.json> <out.json> [--old-hex #C0AF90]
Reads the composite (map + overlay pass), looks up each sample's pixel (3x3 median), skips pixels under the overlay,
and reports CIELAB L*, Oklch per category, outliers among pavers / kerbs, and WCAG contrast plate vs nearby road."""
import sys, json, math
import numpy as np
from PIL import Image
pre, sj, outp = sys.argv[1:4]
img = Image.alpha_composite(Image.open(pre + '_map_pass.png').convert('RGBA'), Image.open(pre + '_overlay_pass.png').convert('RGBA'))
ov = np.asarray(Image.open(pre + '_overlay_pass.png').convert('RGBA'))[..., 3]
A = np.asarray(img.convert('RGB')).astype(float) / 255; s = A.shape[1] / 1191
S = json.loads(open(sj).read())
def lin(c): return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def lab(rgb):
    l = lin(np.asarray(rgb)); M = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])
    X = l @ M.T / np.array([0.95047, 1.0, 1.08883]); f = np.where(X > 216 / 24389, np.cbrt(X), (24389 / 27 * X + 16) / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)
def oklch(rgb):
    l = lin(np.asarray(rgb))
    M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929], [0.2119034982, 0.6806995451, 0.1073969566], [0.0883024619, 0.2817188376, 0.6299787005]])
    M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468], [1.9779984951, -2.4285922050, 0.4505937099], [0.0259040371, 0.7827717662, -0.8086757660]])
    lms = np.cbrt(l @ M1.T); L, a, b = (lms @ M2.T).T if lms.ndim == 2 else lms @ M2.T
    return np.stack([L, np.hypot(a, b), np.degrees(np.arctan2(b, a)) % 360], -1)
def Y(rgb): return lin(np.asarray(rgb)) @ np.array([0.2126, 0.7152, 0.0722])
def hexs(rgb): return '#%02X%02X%02X' % tuple(int(round(v * 255)) for v in rgb)
def px(x, y, r=1):
    X, Yy = int(round(x * s)), int(round(y * s))
    if not (r <= X < A.shape[1] - r and r <= Yy < A.shape[0] - r): return None
    if ov[Yy - r:Yy + r + 1, X - r:X + r + 1].max() > 0: return None
    return np.median(A[Yy - r:Yy + r + 1, X - r:X + r + 1].reshape(-1, 3), 0)
R = {'render': pre, 'scale_px_per_pt': s, 'categories': {}}
vals = {}
for cat, pts in S.items():
    rad = 0 if cat in ('kerb', 'parapet') else 1
    got = [(p, px(p[0], p[1], rad)) for p in pts]; got = [(p, c) for p, c in got if c is not None]
    if not got: continue
    C = np.array([c for _, c in got]); vals[cat] = (got, C)
    med = np.median(C, 0); Lb = lab(C)[:, 0]; ok = oklch(C)
    R['categories'][cat] = {'n': len(got), 'median_srgb': hexs(med), 'median_Lstar': round(float(lab(med)[0]), 1),
        'Lstar_p10_p50_p90': np.percentile(Lb, [10, 50, 90]).round(1).tolist(),
        'oklch_median': [round(float(v), 3) for v in oklch(med)], 'oklch_C_p90': round(float(np.percentile(ok[:, 1], 90)), 4),
        'oklch_C_max': round(float(ok[:, 1].max()), 4)}
# outliers: paver/kerb pixels far from their category median (dE76 > 12) -> list with screen point
for cat in ('paver', 'kerb', 'bridge_deck', 'landing', 'bed', 'bridge_masonry', 'parapet'):
    if cat not in vals: continue
    got, C = vals[cat]; m = lab(np.median(C, 0)); d = np.linalg.norm(lab(C) - m, axis=1)
    ok = oklch(C)
    bad = [(round(float(dd), 1), p[:3], hexs(c), round(float(o[1]), 3)) for (p, c), dd, o in zip(got, d, ok) if dd > 12]
    R['categories'][cat]['dE_gt12'] = len(bad); R['categories'][cat]['dE_gt12_examples'] = sorted(bad, reverse=True)[:25]
    R['categories'][cat]['frac_dE_le6'] = round(float((d <= 6).mean()), 3)
# milestone plates vs nearby road: per milestone, plate median luminance vs paver/kerb median within 70pt of plate centre
if 'plate' in vals:
    got, C = vals['plate']; R['contrast'] = {}
    names = sorted({p[2] for p, _ in got})
    for n in names:
        sel = [(p, c) for p, c in got if p[2] == n]; Cp = np.array([c for _, c in sel]); P = np.array([p[:2] for p, _ in sel], float)
        ctr = P.mean(0); yp = float(np.median(Y(Cp)))
        # use the brighter (front/top) half of the plate as its face colour, plus the darkest decile for the worst case
        Yall = Y(Cp); y_face = float(np.percentile(Yall, 75)); y_p50 = float(np.median(Yall))
        e = {'plate_px': len(sel), 'plate_centre_pt': ctr.round(1).tolist(), 'plate_median_srgb': hexs(np.median(Cp, 0)),
             'plate_Y_p50': round(y_p50, 4), 'plate_Y_p75': round(y_face, 4), 'plate_Lstar_p50': round(float(lab(np.median(Cp, 0))[0]), 1)}
        for cat in ('paver', 'kerb', 'bridge_deck', 'parapet', 'bridge_masonry', 'landing', 'bed'):
            if cat not in vals: continue
            g2, C2 = vals[cat]; Q = np.array([p[:2] for p, _ in g2], float); m = np.linalg.norm(Q - ctr, axis=1) < 70
            if m.sum() < 5: continue
            yr = float(np.median(Y(C2[m]))); yr_lo = float(np.percentile(Y(C2[m]), 10))
            cr = lambda a, b: (max(a, b) + 0.05) / (min(a, b) + 0.05)
            e[cat] = {'n_within_70pt': int(m.sum()), 'Y_p50': round(yr, 4), 'Lstar_p50': round(float(lab(np.median(C2[m], 0))[0]), 1),
                      'contrast_vs_plate_p50': round(cr(yr, y_p50), 2), 'contrast_vs_plate_p75face': round(cr(yr, y_face), 2),
                      'contrast_worst_darkroad_p10_vs_plate_p75': round(cr(yr_lo, y_face), 2)}
        R['contrast'][n] = e
open(outp, 'w').write(json.dumps(R, ensure_ascii=False, indent=1))
for k, v in R['categories'].items(): print(k, {kk: vv for kk, vv in v.items() if kk != 'dE_gt12_examples'})
if 'contrast' in R: print(json.dumps(R['contrast'], indent=1))
