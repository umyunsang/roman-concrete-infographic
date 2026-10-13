"""Compose the 300 ppi + 3 mm bleed print map (5033x7087) and cut 2x2 tiles under Figma's 4096 px / 10 MB limits."""
import sys, json, hashlib
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
tag = sys.argv[1]
m = Image.open(ROOT / f'renders/{tag}_print_bleed_map_pass.png').convert('RGBA')
o = Image.open(ROOT / f'renders/{tag}_print_bleed_overlay_pass.png').convert('RGBA')
assert m.size == o.size == (5033, 7087)
full = Image.alpha_composite(m, o).convert('RGB')
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
receipt = {'tag': tag, 'size_px': full.size, 'ppi': 300, 'bleed_mm': 3, 'tiles': tiles,
           'pt_per_px': 1208 / 5033}
(out / f'{tag}_print_tiles.json').write_text(json.dumps(receipt, indent=2))
print(json.dumps(receipt))
