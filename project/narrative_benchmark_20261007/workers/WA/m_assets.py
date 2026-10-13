import sys, os, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from colorm import lab, oklch, de00, rgb2hex, hex2rgb
root = sys.argv[1]           # assets dir root containing assets/<id>/ and assets_index.json
idx = {a['id']: a for a in json.load(open(os.path.join(root, 'assets_index.json')))['assets']}
def load(aid):
    d = os.path.join(root, 'assets', aid)
    ctx = np.asarray(Image.open(os.path.join(d, 'context.png')).convert('RGB'), float) / 255
    iso = np.asarray(Image.open(os.path.join(d, 'isolated_rgba.png')).convert('RGBA'), float) / 255
    return ctx, iso, idx[aid]['crop_pt']
def to_px(cp, x, y, s=3): return (int(round((x - cp[0]) * s)), int(round((y - cp[2]) * s)))
R = {}
# ---- header gate: figure/ground value, contour coverage, lime-white clipping
ctx, iso, cp = load('header_gate'); a = iso[..., 3] > 0.5
L = lab(ctx)[..., 0]
din = ndi.distance_transform_edt(a) / 3; dout = ndi.distance_transform_edt(~a) / 3
inner = (din >= 2) & (din <= 10); outer = (dout >= 2) & (dout <= 10)
M = float(np.median(L[a & (din > 3)])); g = float(np.median(L[outer]))
R['gate_body_L_median'] = round(M, 2); R['gate_paper_L'] = round(g, 2); R['gate_dL_fg'] = round(g - M, 2)
R['gate_ring_in_out'] = [round(float(np.median(L[inner])), 2), round(float(np.median(L[outer])), 2)]
# contour coverage: boundary points every ~1pt, inner 1-3pt vs outer 1-3pt medians in a 4pt window
edge = a & ~ndi.binary_erosion(a)
ys, xs = np.nonzero(edge); sel = np.arange(0, len(ys), 3); ok = 0; lost = 0; n = 0
inb = (din >= 1) & (din <= 3); outb = (dout >= 1) & (dout <= 3)
Lab = lab(ctx)
for i in sel:
    y, x = ys[i], xs[i]; y0, y1, x0, x1 = max(0, y - 6), y + 7, max(0, x - 6), x + 7
    wi = inb[y0:y1, x0:x1]; wo = outb[y0:y1, x0:x1]
    if wi.sum() < 3 or wo.sum() < 3: continue
    li = np.median(Lab[y0:y1, x0:x1][wi], 0); lo = np.median(Lab[y0:y1, x0:x1][wo], 0)
    dl = abs(li[0] - lo[0]); de = de00(li, lo); n += 1
    ok += (dl >= 10 or de >= 10); lost += (dl < 5 and de < 5)
R['gate_contour_cover'] = round(ok / n, 3); R['gate_contour_lost'] = round(lost / n, 3); R['gate_contour_n'] = n
okl = oklch(ctx)
limewhite = a & (L >= 95) & (okl[1] <= 0.035) & (okl[2] >= 70) & (okl[2] <= 110)
lbl, nl = ndi.label(limewhite); sizes = ndi.sum(limewhite, lbl, range(1, nl + 1)) / 9 if nl else np.array([])
R['gate_limewhite_px'] = int(limewhite.sum()); R['gate_limewhite_blobs_ge1pt2'] = int((sizes >= 1).sum())
R['gate_clip254_px'] = int((a & (ctx.max(-1) >= 254 / 255)).sum())
# ---- recipe
ctx, iso, cp = load('basic_recipe'); a = iso[..., 3] > 0.5; L = lab(ctx)[..., 0]; okl = oklch(ctx)
def region(x0, x1, y0, y1):
    m = np.zeros_like(a); p0 = to_px(cp, x0, y0); p1 = to_px(cp, x1, y1); m[max(0,p0[1]):p1[1], max(0,p0[0]):p1[0]] = True; return m & a
lime = region(15, 85, 90, 140) & (L > 80)
R['lime_clip254_frac'] = round(float((ctx[lime].max(-1) >= 254 / 255).mean()), 3)
R['lime_p95_L'] = round(float(np.percentile(L[lime], 95)), 1)
def halves(m):
    ys, xs = np.nonzero(m); cx = np.median(xs)
    l = L[m & (np.arange(m.shape[1])[None, :] < cx)]; r = L[m & (np.arange(m.shape[1])[None, :] >= cx)]
    return round(float(np.median(l)), 1), round(float(np.median(r)), 1), round(float(np.percentile(l, 10) - np.percentile(r, 90)), 1)
R['lime_halves_LR_p10p90'] = halves(lime)
ash = region(90, 160, 90, 132) & (okl[1] < 0.03) & (L < 50)
R['ash_halves_LR_p10p90'] = halves(ash)
R['ash_lit'] = [round(float(np.percentile(L[ash], 90)), 1), round(float(np.median(okl[1][ash])), 3)]
board = region(15, 160, 120, 140) & (okl[1] > 0.04) & (L < 60) & (L > 30)
def lit(m):
    c = ctx[m]; Lm = lab(c)[:, 0]; top = c[Lm >= np.percentile(Lm, 70)].mean(0); o = oklch(top)
    return {'hex': rgb2hex(top), 'L': round(float(lab(top)[0]), 1), 'C': round(float(o[1]), 3), 'h': round(float(o[2]), 1), 'px': int(m.sum())}
R['board_lit'] = lit(board)
plank = region(245, 335, 100, 140) & (okl[1] > 0.035) & (okl[2] > 50) & (okl[2] < 90)
R['plank_lit'] = lit(plank)
stones = region(165, 230, 100, 135) & (okl[1] < 0.06) & (okl[2] > 60) & (L > 55)
R['stone_lit'] = lit(stones)
brick = region(165, 230, 100, 135) & (okl[2] < 60) & (okl[1] > 0.02)
R['brick_lit'] = lit(brick) if brick.sum() > 10 else None
# lime contour against paper (FORM-06): boundary of the lime+board vs outside
# ---- sources
ctx, iso, cp = load('basic_sources'); a = iso[..., 3] > 0.5; L = lab(ctx)[..., 0]; okl = oklch(ctx)
def regionS(x0, x1, y0, y1):
    m = np.zeros_like(a); p0 = to_px(cp, x0, y0); p1 = to_px(cp, x1, y1); m[max(0,p0[1]):p1[1], max(0,p0[0]):p1[0]] = True; return m & a
core = regionS(975, 1000, 60, 135) & (okl[2] > 20) & (okl[2] < 80) & (okl[1] > 0.02) & (L < 75)
R['core_lit'] = lit(core)
blue = a & (okl[2] > 180) & (okl[2] < 260) & (okl[1] > 0.02)
R['blue_px_frac'] = round(float(blue.sum() / a.sum()), 3)
scroll = regionS(855, 925, 95, 145) & (L > 70)
R['scroll_lit'] = lit(scroll)
R['scroll_bbox_pt'] = None
print(json.dumps(R, ensure_ascii=False, indent=0))
