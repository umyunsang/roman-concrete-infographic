"""Compose the 300 ppi + 3 mm bleed print map (5033x7087) and cut 2x2 tiles under Figma's 4096 px / 10 MB limits.

v2 (print critic F2): the outermost bleed rows/columns show the terrain's edge (top 12 rows grey, right 16 columns
shaded). They lie 2+ mm outside the trim, so they are replaced by a mirror of the adjacent bleed band.
"""
import sys, json
from pathlib import Path
import numpy as np
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
tag = sys.argv[1]
TOP, RIGHT = 12, 16
m = Image.open(ROOT / f'renders/{tag}_print_bleed_map_pass.png').convert('RGBA')
o = Image.open(ROOT / f'renders/{tag}_print_bleed_overlay_pass.png').convert('RGBA')
assert m.size == o.size == (5033, 7087)
a = np.array(Image.alpha_composite(m, o).convert('RGB'))
a[:TOP] = a[2 * TOP - 1:TOP - 1:-1]                      # row k <- row 2*TOP-1-k
a[:, -RIGHT:] = a[:, -RIGHT - 1:-2 * RIGHT - 1:-1]        # col -k <- col -(2*RIGHT+1-k)
full = Image.fromarray(a)
out = ROOT / 'out/print'; out.mkdir(parents=True, exist_ok=True)
full.save(out / f'{tag}_map_print_bleed_5033x7087.png', optimize=True)
xs, ys = [0, 2517, 5033], [0, 3544, 7087]
tiles = []
for r in range(2):
    for c in range(2):
        box = (xs[c], ys[r], xs[c + 1], ys[r + 1])
        p = out / f'{tag}_tile_r{r}c{c}.jpg'
        full.crop(box).save(p, quality=95, subsampling=0, dpi=(300, 300))
        tiles.append({'file': str(p), 'box_px': box, 'bytes': p.stat().st_size})
edge = {'top_rows_mean': [round(float(v), 1) for v in a[:TOP].reshape(-1, 3).mean(0)],
        'right_cols_mean': [round(float(v), 1) for v in a[:, -RIGHT:].reshape(-1, 3).mean(0)]}
receipt = {'tag': tag, 'size_px': full.size, 'ppi': 300, 'bleed_mm': 3, 'edge_mirror_px': {'top': TOP, 'right': RIGHT},
           'edge_after': edge, 'tiles': tiles, 'pt_per_px': 1208 / 5033}
(out / f'{tag}_print_tiles.json').write_text(json.dumps(receipt, indent=2))
print(json.dumps(receipt))
