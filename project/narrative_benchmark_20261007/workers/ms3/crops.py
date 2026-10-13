"""Before/after crops: python3 crops.py <before_prefix> <after_prefix> <out_png> <x0> <x1> <y0> <y1> <zoom> [grid]
Composite = map pass + overlay pass (alpha). Box in poster pt (1191 x 1684); zoom = output px per pt.
Left = before, right = after; optional 10pt grid with labels every 20pt."""
import sys
from PIL import Image, ImageDraw
bp, ap, outp = sys.argv[1:4]
x0, x1, y0, y1, z = map(float, sys.argv[4:9]); grid = len(sys.argv) > 9


def comp(pre):
    m = Image.open(pre + '_map_pass.png').convert('RGBA'); o = Image.open(pre + '_overlay_pass.png').convert('RGBA')
    return Image.alpha_composite(m, o).convert('RGB')


tiles = []
for pre, lab in ((bp, 'before'), (ap, 'after')):
    im = comp(pre); s = im.width / 1191
    c = im.crop((round(x0 * s), round(y0 * s), round(x1 * s), round(y1 * s)))
    c = c.resize((round((x1 - x0) * z), round((y1 - y0) * z)), Image.Resampling.LANCZOS)
    d = ImageDraw.Draw(c)
    if grid:
        for x in range(int(x0 // 10 * 10 + 10), int(x1), 10):
            d.line([((x - x0) * z, 0), ((x - x0) * z, c.height)], fill=(90, 140, 255) if x % 50 else (230, 0, 230), width=1)
            if x % 20 == 0: d.text(((x - x0) * z + 2, 2), str(x), fill=(0, 0, 160))
        for y in range(int(y0 // 10 * 10 + 10), int(y1), 10):
            d.line([(0, (y - y0) * z), (c.width, (y - y0) * z)], fill=(90, 140, 255) if y % 50 else (230, 0, 230), width=1)
            if y % 20 == 0: d.text((2, (y - y0) * z + 2), str(y), fill=(0, 0, 160))
    d.rectangle([0, 0, 60, 14], fill=(255, 255, 255)); d.text((3, 1), lab, fill=(0, 0, 0))
    tiles.append(c)
W = sum(t.width for t in tiles) + 12; H = max(t.height for t in tiles)
S = Image.new('RGB', (W, H), 'white'); S.paste(tiles[0], (0, 0)); S.paste(tiles[1], (tiles[0].width + 12, 0))
S.save(outp); print(outp, S.size)
