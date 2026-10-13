"""Measure rendered colours per field material: ID pass masks x the real two-pass render.
usage: python analyze.py <id.png> <ids.json> <render_prefix> <out.json>"""
import sys, json
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parent))
from colorlib import srgb_to_lin, oklch, lstar, lin_to_srgb, srgb_to_hex
idp, idsj, pre, outj = sys.argv[1:5]
ids = json.loads(Path(idsj).read_text())
I = np.asarray(Image.open(idp).convert('RGBA')).astype(int)
m = Image.open(pre + '_map_pass.png').convert('RGBA'); o = Image.open(pre + '_overlay_pass.png').convert('RGBA')
comp = np.asarray(Image.alpha_composite(m, o).convert('RGB')).astype(float) / 255
ov = np.asarray(o)[..., 3] > 0
assert I.shape[:2] == comp.shape[:2], (I.shape, comp.shape)
def erode(M):
    E = M.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            E &= np.roll(np.roll(M, dy, 0), dx, 1)
    return E
res = {}
for name, rgb in ids.items():
    M = (np.abs(I[..., :3] - np.array(rgb)).max(-1) <= 4) & (I[..., 3] == 255) & ~ov
    E = erode(M); used = 'eroded'
    if E.sum() < 200: E = M; used = 'raw'
    if E.sum() == 0: continue
    px = srgb_to_lin(comp[E]); lch = oklch(px); Ls = lstar(px)
    med = np.median(px, 0); mlch = oklch(med)
    hh = lch[:, 2]
    res[name] = dict(pixels=int(E.sum()), mask=used, median_hex=srgb_to_hex(lin_to_srgb(med)),
                     L_star_median=round(float(lstar(med)), 1), L_star_p10=round(float(np.percentile(Ls, 10)), 1),
                     L_star_p90=round(float(np.percentile(Ls, 90)), 1),
                     ok_L_median=round(float(mlch[0]), 3), C_median=round(float(mlch[1]), 3), C_p90=round(float(np.percentile(lch[:, 1], 90)), 3),
                     h_median=round(float(mlch[2]), 1), h_p10=round(float(np.percentile(hh, 10)), 1), h_p90=round(float(np.percentile(hh, 90)), 1))
    r = res[name]
    r['pass'] = bool(62 <= r['L_star_median'] <= 84 and r['C_median'] <= 0.09 and 60 <= r['h_median'] <= 130)
Path(outj).write_text(json.dumps(res, indent=1, ensure_ascii=False))
print(f"{'material':38s} {'px':>6s} {'hex':8s} {'L*med':>6s} {'L*p10':>6s} {'L*p90':>6s} {'C':>6s} {'Cp90':>6s} {'h':>6s} {'hp10':>6s} {'hp90':>6s} pass")
for k, r in res.items():
    print(f"{k:38s} {r['pixels']:6d} {r['median_hex']:8s} {r['L_star_median']:6.1f} {r['L_star_p10']:6.1f} {r['L_star_p90']:6.1f} {r['C_median']:6.3f} {r['C_p90']:6.3f} {r['h_median']:6.1f} {r['h_p10']:6.1f} {r['h_p90']:6.1f} {r['pass']}")
