"""before/after crop rows: python ba.py <before_prefix> <after_prefix> <out.png> x0,x1,y0,y1,zoom ..."""
import sys
from PIL import Image, ImageDraw
bp, ap, out = sys.argv[1:4]; boxes = [tuple(map(float, b.split(','))) for b in sys.argv[4:]]
def comp(pre):
    m = Image.open(pre + '_map_pass.png').convert('RGBA'); o = Image.open(pre + '_overlay_pass.png').convert('RGBA')
    return Image.alpha_composite(m, o).convert('RGB')
B, A = comp(bp), comp(ap); s = B.width / 1191
rows = []
for x0, x1, y0, y1, z in boxes:
    tiles = []
    for im, lab in ((B, 'before'), (A, 'after')):
        c = im.crop((round(x0 * s), round(y0 * s), round(x1 * s), round(y1 * s)))
        c = c.resize((round(c.width * z / s), round(c.height * z / s)), Image.Resampling.LANCZOS)
        d = ImageDraw.Draw(c); d.rectangle((0, 0, 200, 14), fill='white'); d.text((3, 2), f'{lab} x{x0:.0f}-{x1:.0f} y{y0:.0f}-{y1:.0f} x{z:g}', fill='black')
        tiles.append(c)
    rows.append(tiles)
W = max(t[0].width + t[1].width + 10 for t in rows); H = sum(t[0].height for t in rows) + 10 * (len(rows) - 1)
S = Image.new('RGB', (W, H), 'white'); y = 0
for b, a in rows:
    S.paste(b, (0, y)); S.paste(a, (b.width + 10, y)); y += b.height + 10
S.save(out); print(out, S.size)
