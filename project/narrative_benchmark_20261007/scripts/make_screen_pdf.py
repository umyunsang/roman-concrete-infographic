"""Screen / sharing PDF: Figma sRGB export of the print frame 810:78 -> A2 trim view, one seamless background (print review PR-m2).

Run: uv run --no-project --with pillow --with numpy --with pypdf python -I make_screen_pdf.py <figma.pdf> <out.pdf>

1. Page boxes. Figma exports every box as the full 1208x1701 pt page (A2 + 3 mm bleed), so viewers show the bleed.
     TrimBox = CropBox = [8.5 8.5 1199.5 1692.5]  (1191 x 1684 pt = design frame 790:78 = the print PDF's TrimBox)
     BleedBox = MediaBox = [0 0 1208 1701]          (bleed kept in the file, just not shown); ArtBox dropped (= CropBox)
2. Background. Figma draws the map as 2x2 tiles under four abutting clip paths; anti-aliasing viewers blend each clip
   edge with the paper fill and show a light hairline at x 604.12 pt (poppler 72 dpi: +8 grey levels). The four tiles
   are decoded, joined pixel-exactly into one 5033x7087 image (same ICC colour space) and re-encoded once as JPEG
   (q 94, 4:4:4); Figma's all-255 alpha masks are dropped after checking they are opaque.
Vector lettering and the invisible Type3 search layer are copied untouched, so text search and copy still work.
"""
import sys, io, re, json, subprocess
from pathlib import Path
import numpy as np
from PIL import Image
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, ArrayObject, FloatObject, NumberObject

src, out = map(Path, sys.argv[1:3])
MEDIA = (0, 0, 1208, 1701)
BLEED_PT = 8.5                                  # 3 mm; equals the 790:78 design frame offset inside 810:78
TRIM = (BLEED_PT, BLEED_PT, MEDIA[2] - BLEED_PT, MEDIA[3] - BLEED_PT)
XS, YS = [0, 2517, 5033], [0, 3544, 7087]
TILES = {(XS[c + 1] - XS[c], YS[r + 1] - YS[r]): (r, c) for r in range(2) for c in range(2)}
JPEG_Q = 94

rd = PdfReader(src)
assert len(rd.pages) == 1, len(rd.pages)
mb = [float(v) for v in rd.pages[0].mediabox]
assert all(abs(a - b) < 0.01 for a, b in zip(mb, MEDIA)), mb
wr = PdfWriter(clone_from=rd)
pg = wr.pages[0]

# --- 2. one seamless background image
xobjs = pg['/Resources']['/XObject']
imgs = sorted((name, ref.get_object()) for name, ref in xobjs.items() if ref.get_object().get('/Subtype') == '/Image')
full = np.zeros((7087, 5033, 3), np.uint8)
for name, o in imgs:
    w, h = int(o['/Width']), int(o['/Height']); r, c = TILES[(w, h)]
    assert o.get('/Filter') in ('/DCTDecode', ['/DCTDecode']), o.get('/Filter')
    im = Image.open(io.BytesIO(o._data)); im.load(); assert im.mode == 'RGB', im.mode
    full[YS[r]:YS[r + 1], XS[c]:XS[c + 1]] = np.asarray(im)
    if '/SMask' in o:
        sm = o['/SMask'].get_object().get_data()
        assert len(sm) == w * h and min(sm) == 255, 'tile alpha is not fully opaque'
assert sorted(TILES[(int(o['/Width']), int(o['/Height']))] for _, o in imgs) == sorted(TILES.values())
cs_ = pg.get_contents().get_data()
TILE_BLOCK = (rb'q\n1\.000000 0\.000000 -0\.000000 1\.000000 [\d.]+ [\d.]+ cm\n(?:[\d.]+ [\d.]+ [ml]\n)+h\nW\nn\n'
              rb'q\n[-\d. ]+ cm\n(/X\d+) Do\nQ\nn\nQ\n')
blocks = list(re.finditer(TILE_BLOCK, cs_))
assert sorted(m.group(1).decode() for m in blocks) == sorted(n for n, _ in imgs), [m.group(1) for m in blocks]
buf = io.BytesIO(); Image.fromarray(full).save(buf, 'JPEG', quality=JPEG_Q, subsampling=0)
keep_name, o = imgs[0]
o._data = buf.getvalue()
o[NameObject('/Width')], o[NameObject('/Height')] = NumberObject(5033), NumberObject(7087)
o[NameObject('/Filter')] = NameObject('/DCTDecode')
for k in ('/DecodeParms', '/SMask'):
    if k in o: del o[k]
for name, _ in imgs[1:]: del xobjs[name]
one = f'q\n1208 0 0 1701 0 0 cm\n{keep_name} Do\nQ\n'.encode()
cs_ = cs_[:blocks[0].start()] + one + b''.join(cs_[a.end():b.start()] for a, b in zip(blocks, blocks[1:])) + cs_[blocks[-1].end():]
c0 = pg.get_contents(); c0.set_data(cs_); pg.replace_contents(c0)

# --- 1. page boxes
box = lambda v: ArrayObject([FloatObject(x) for x in v])
pg[NameObject('/MediaBox')] = box(MEDIA)
pg[NameObject('/BleedBox')] = box(MEDIA)
pg[NameObject('/TrimBox')] = box(TRIM)
pg[NameObject('/CropBox')] = box(TRIM)
if '/ArtBox' in pg: del pg['/ArtBox']
pg.compress_content_streams()
with open(out, 'wb') as f: wr.write(f)

def text(p):
    return subprocess.run(['pdftotext', '-nopgbrk', '-raw', str(p), '-'], capture_output=True, check=True).stdout
t_src, t_out = text(src), text(out)
w, h = TRIM[2] - TRIM[0], TRIM[3] - TRIM[1]
print(json.dumps({'out': str(out), 'bytes': out.stat().st_size, 'trim_pt': TRIM, 'trim_mm': [round(w / 72 * 25.4, 2), round(h / 72 * 25.4, 2)],
                  'background': {'figma_tiles_joined': [n for n, _ in imgs], 'as': keep_name, 'px': [5033, 7087], 'jpeg_q': JPEG_Q, 'jpeg_bytes': len(buf.getvalue())},
                  'search_text_chars': len(t_out.decode()), 'search_text_same_as_figma': t_src == t_out}))
