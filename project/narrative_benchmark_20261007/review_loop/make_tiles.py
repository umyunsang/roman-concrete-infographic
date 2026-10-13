"""Cut a round's 2x poster into overlapping labelled tiles (pt coordinates in names)."""
import sys
from pathlib import Path
from PIL import Image
d = Path(sys.argv[1]); im = Image.open(d / 'poster_2x.png').convert('RGB')
W, H = 1191, 1684; cols, rows, ov = 3, 4, 30
cw, rh = W / cols, H / rows
out = d / 'tiles'; out.mkdir(exist_ok=True)
for r in range(rows):
    for c in range(cols):
        x0, y0 = max(0, int(c * cw - ov)), max(0, int(r * rh - ov))
        x1, y1 = min(W, int((c + 1) * cw + ov)), min(H, int((r + 1) * rh + ov))
        im.crop((x0 * 2, y0 * 2, x1 * 2, y1 * 2)).save(out / f'tile_r{r+1}c{c+1}_x{x0}-{x1}_y{y0}-{y1}.png')
print(sorted(p.name for p in out.iterdir()))
