"""Print PDF: Figma vector export -> lossless background swap -> PDF/X-4 CMYK (PSO Coated v3, relative, no BPC) -> trim/bleed boxes.

Run: uv run --no-project --with pypdf --with pillow --with numpy python -I make_print_pdfx.py <figma.pdf> <bleed_5033x7087.png> <icc> <pdfx_def.ps> <out.pdf>
Answers print critic F1 (CMYK separation inside the file, OutputIntent), F2 (TrimBox/BleedBox) and the 4:2:0 note in F3.
"""
import sys, zlib, re, subprocess, json
from pathlib import Path
import numpy as np
from PIL import Image
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, ArrayObject, FloatObject, NumberObject

src, bleed_png, icc, pdfx_def, out = map(Path, sys.argv[1:6])
work = out.parent / (out.stem + '_work'); work.mkdir(exist_ok=True)
Image.MAX_IMAGE_PIXELS = None
full = np.asarray(Image.open(bleed_png).convert('RGB'))
assert full.shape[:2] == (7087, 5033), full.shape
XS, YS = [0, 2517, 5033], [0, 3544, 7087]
tiles = {(XS[c + 1] - XS[c], YS[r + 1] - YS[r]): (r, c) for r in range(2) for c in range(2)}
assert len(tiles) == 4

# 1. Figma re-encodes the tiles as 4:2:0 JPEG; put the original pixels back (Flate, same ICC colour space)
rd = PdfReader(src); wr = PdfWriter(clone_from=rd)
pg = wr.pages[0]; swapped = []
for name, ref in pg['/Resources']['/XObject'].items():
    o = ref.get_object()
    if o.get('/Subtype') != '/Image': continue
    w, h = int(o['/Width']), int(o['/Height'])
    r, c = tiles[(w, h)]
    px = np.ascontiguousarray(full[YS[r]:YS[r + 1], XS[c]:XS[c + 1]])
    assert px.shape == (h, w, 3)
    o._data = zlib.compress(px.tobytes(), 9)
    o[NameObject('/Filter')] = NameObject('/FlateDecode')
    if '/DecodeParms' in o: del o['/DecodeParms']
    if '/SMask' in o: del o['/SMask']            # Figma's all-255 alpha: no transparency in the print file
    if '/SMask' in o: del o['/SMask']            # Figma's all-255 alpha: no transparency in the print file
    swapped.append({'xobj': name, 'tile': f'r{r}c{c}', 'px': [w, h]})
rgb_pdf = work / 'lossless_rgb.pdf'
with open(rgb_pdf, 'wb') as f: wr.write(f)

# 2. PDF/X-4 CMYK. Relative colorimetric without BPC = the separation the CMYK table in PRINT_SPEC was measured on.
x4 = work / 'pdfx4_raw.pdf'
cmd = ['/opt/homebrew/bin/gs', '-q', '-dBATCH', '-dNOPAUSE', '-dSAFER', f'--permit-file-read={icc.parent}/',
       '-sDEVICE=pdfwrite', '-dPDFX=4', '-dCompatibilityLevel=1.6', '-sColorConversionStrategy=CMYK',
       f'-sOutputICCProfile={icc}', '-dRenderIntent=1', '-dBlackPtComp=0',
       '-dAutoFilterColorImages=false', '-dColorImageFilter=/DCTEncode', '-dDownsampleColorImages=false',
       f'-sOutputFile={x4}', '-c',
       '<< /ColorImageDict << /QFactor 0.15 /Blend 1 /HSamples [1 1 1 1] /VSamples [1 1 1 1] >> >> setdistillerparams',
       '-f', str(pdfx_def), str(rgb_pdf)]
subprocess.run(cmd, check=True)

# 3. page boxes (A2 trim inside 3 mm = 8.5 pt bleed) + drop the redundant 'h h' closepaths gs writes
rd = PdfReader(x4); wr = PdfWriter(clone_from=rd); pg = wr.pages[0]
box = lambda *v: ArrayObject([FloatObject(x) for x in v])
pg[NameObject('/MediaBox')] = box(0, 0, 1208, 1701)
pg[NameObject('/BleedBox')] = box(0, 0, 1208, 1701)
pg[NameObject('/TrimBox')] = box(8.5, 8.5, 1199.5, 1692.5)
for k in ('/CropBox', '/ArtBox'):
    if k in pg: del pg[k]
cs = pg.get_contents(); lines = cs.get_data().split(b'\n')
PAINT = {b'f', b'f*', b'F', b'S', b's', b'B', b'B*', b'b', b'b*', b'n'}
keep, has_path, in_img, n_hh = [], False, False, 0
for ln in lines:                      # gs writes one operator per line; drop closepaths with no open subpath
    if ln.startswith(b'BI'): in_img = True
    if in_img:
        keep.append(ln); in_img = not ln.endswith(b'EI'); continue
    op = ln.rsplit(b' ', 1)[-1]
    if op in (b'm', b're'): has_path = True
    elif op in PAINT: has_path = False
    elif ln == b'h' and (not has_path or (keep and keep[-1] == b'h')):
        n_hh += 1; continue
    keep.append(ln)
data = b'\n'.join(keep)
# small dark lettering and leader lines: 4-colour rich black -> K-led 3-plate mixes (PSO Coated v3, dE00 <= 1)
K_LED = {(0.565, 0.624, 0.733, 0.91): (0, 0.30, 0.50, 1.00),    # #2E2A22  dE00 0.96, TAC 180%
         (0.549, 0.525, 0.592, 0.757): (0, 0.15, 0.30, 0.92),   # #3E3A31  dE00 0.60, TAC 137%
         (0.494, 0.478, 0.486, 0.561): (0, 0.15, 0.20, 0.82)}   # #59524A  dE00 0.90, TAC 117%
n_kled = 0
def _kled(m):
    global n_kled
    v = tuple(float(x) for x in m.group(1).split())
    for src, dst in K_LED.items():
        if max(abs(a - b) for a, b in zip(v, src)) < 0.004:
            n_kled += 1; return (' '.join(f'{x:g}' for x in dst) + ' ' + m.group(2).decode()).encode()
    return m.group(0)
data = re.sub(rb'((?:[\d.]+ ){3}[\d.]+) (k|K)\b', _kled, data)
# small dark lettering and leader lines: 4-colour rich black -> K-led 3-plate mixes (PSO Coated v3, dE00 <= 1)
K_LED = {(0.565, 0.624, 0.733, 0.91): (0, 0.30, 0.50, 1.00),    # #2E2A22  dE00 0.96, TAC 180%
         (0.549, 0.525, 0.592, 0.757): (0, 0.15, 0.30, 0.92),   # #3E3A31  dE00 0.60, TAC 137%
         (0.494, 0.478, 0.486, 0.561): (0, 0.15, 0.20, 0.82)}   # #59524A  dE00 0.90, TAC 117%
n_kled = 0
def _kled(m):
    global n_kled
    v = tuple(float(x) for x in m.group(1).split())
    for src, dst in K_LED.items():
        if max(abs(a - b) for a, b in zip(v, src)) < 0.004:
            n_kled += 1; return (' '.join(f'{x:g}' for x in dst) + ' ' + m.group(2).decode()).encode()
    return m.group(0)
data = re.sub(rb'((?:[\d.]+ ){3}[\d.]+) (k|K)\b', _kled, data)
# visible lettering is already filled outlines; the BT/ET runs are Figma's invisible search layer (Type3 glyphs that
# paint nothing, set in 4-colour black). A print master needs no fonts, so the layer and its fonts go.
n_text = len(re.findall(rb'BT\n.*?\nET', data, re.S))
data = re.sub(rb'BT\n.*?\nET', b'', data, flags=re.S)
cs.set_data(data); pg.replace_contents(cs)
if '/Font' in pg['/Resources']: del pg['/Resources']['/Font']
pg.compress_content_streams()
wr.pdf_header = b'%PDF-1.6'   # PDF/X-4 needs 1.6; pypdf would write 1.3
with open(out, 'wb') as f: wr.write(f)
print(json.dumps({'swapped': swapped, 'stray_closepath_removed': n_hh, 'invisible_text_runs_removed': n_text, 'k_led_colour_ops': n_kled, 'k_led_colour_ops': n_kled, 'out': str(out), 'bytes': out.stat().st_size}))
