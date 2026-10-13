"""ladder.py <render_prefix> <mask.png>: L*/Oklch of paving, kerb, paper right outside the kerbs (ring 3..10 px outside
road masks), and Colosseum wall (high-chroma pixels in a box on the Colosseum arcade)."""
import sys, json, numpy as np
from PIL import Image, ImageFilter
pre, mp = sys.argv[1:3]
ovp = Image.open(pre + '_overlay_pass.png').convert('RGBA')
A = np.asarray(Image.alpha_composite(Image.open(pre + '_map_pass.png').convert('RGBA'), ovp).convert('RGB')).astype(float) / 255
ov = np.asarray(ovp)[..., 3] > 0; M = np.asarray(Image.open(mp).convert('RGB')).astype(int); s = A.shape[1] / 1191
road = (M.sum(-1) > 128)
def grow(m, r): return np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * r + 1))) > 0
def lin(c): return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def Ls(c):
    y = lin(c) @ np.array([0.2126729, 0.7151522, 0.0721750]); return np.where(y > 216 / 24389, 116 * np.cbrt(y) - 16, 24389 / 27 * y)
def okC(c):
    l = lin(c); M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929], [0.2119034982, 0.6806995451, 0.1073969566], [0.0883024619, 0.2817188376, 0.6299787005]])
    M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468], [1.9779984951, -2.4285922050, 0.4505937099], [0.0259040371, 0.7827717662, -0.8086757660]])
    o = np.cbrt(l @ M1.T) @ M2.T; return np.hypot(o[..., 1], o[..., 2]), np.degrees(np.arctan2(o[..., 2], o[..., 1])) % 360
ring = grow(road, 10) & ~grow(road, 3) & ~ov & (M.sum(-1) == 0)
paper = A[ring]; C, h = okC(paper); keep = C < 0.05                 # drop river / other coloured stuff in the ring
out = {'paper_next_to_road': {'n': int(keep.sum()), 'Lstar_p50': round(float(np.median(Ls(paper[keep]))), 1), 'oklchC_p50': round(float(np.median(C[keep])), 3)}}
x0, x1, y0, y1 = [int(v * s) for v in (660, 900, 800, 880)]               # Colosseum outer arcade (south face)
box = A[y0:y1, x0:x1].reshape(-1, 3); Cb, hb = okC(box); k = Cb > 0.05
out['colosseum_arcade_box_660-900_800-880'] = {'n': int(k.sum()), 'Lstar_p50': round(float(np.median(Ls(box[k]))), 1), 'oklchC_p50': round(float(np.median(Cb[k])), 3), 'hue_p50': round(float(np.median(hb[k])), 1)}
print(json.dumps(out))
