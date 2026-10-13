"""Verify the print master + screen PDF of one tag; writes out/print/check_<tag>/verify_<tag>.json and inspection crops.

Run: uv run --no-project --with pillow --with numpy --with pypdf python -I verify_print_master.py <tag> [--prev-tag v8_12] [--figma-only]

--figma-only : only check that figma_export_<tag>.pdf carries this tag's tiles (guards the manual Figma upload step).
Checks: page boxes, Ghostscript (nullpage + -dPDFX=4 re-run) and poppler messages, fonts, image colour spaces / SMask /
transparency, OutputIntent ICC, tile placement + 600 ppi seam strips, dE00 of the trim-area image against the render
(transicc, PSO Coated v3, relative colorimetric, no BPC), TAC, JPEG quantisation, outermost vector ink (safe area).
"""
import sys, re, json, zlib, hashlib, subprocess, tempfile, io
from pathlib import Path
import numpy as np
from PIL import Image
from pypdf import PdfReader, PdfWriter

Image.MAX_IMAGE_PIXELS = None
ROOT = Path(__file__).resolve().parents[1]
args = sys.argv[1:]
tag = args[0]
prev = args[args.index('--prev-tag') + 1] if '--prev-tag' in args else None
P = ROOT / 'out/print'
PRINT = P / '로마콘크리트_A2_재단3mm_인쇄원고_PDFX4_CMYK.pdf'
SCREEN = P / '로마콘크리트_A2_재단3mm_화면용_RGB.pdf'
FIGMA = P / f'figma_export_{tag}.pdf'
BLEED = P / f'{tag}_map_print_bleed_5033x7087.png'
ICC, PDFX_DEF = P / 'PSOcoated_v3.icc', P / 'PDFX_def_PSOv3.ps'
GS = '/opt/homebrew/bin/gs'
OUT = P / f'check_{tag}'; OUT.mkdir(exist_ok=True)
XS, YS = [0, 2517, 5033], [0, 3544, 7087]
MEDIA, TRIM = [0, 0, 1208, 1701], [8.5, 8.5, 1199.5, 1692.5]
MM = 25.4 / 72
checks = []

def check(name, ok, evidence):
    checks.append({'check': name, 'pass': bool(ok), 'evidence': evidence})
    print(('PASS ' if ok else 'FAIL ') + name + ' :: ' + json.dumps(evidence, ensure_ascii=False)[:600], flush=True)

def run(cmd, **kw):
    return subprocess.run([str(c) for c in cmd], capture_output=True, **kw)

def tile_of(w, h):
    return {(XS[c + 1] - XS[c], YS[r + 1] - YS[r]): (r, c) for r in range(2) for c in range(2)}[(w, h)]

def pdf_images(path):
    """{(r,c): (xobject, PIL image)} for the 4 background tiles, decoded from the raw stream."""
    pg = PdfReader(path).pages[0]; res = {}
    for name, ref in pg['/Resources']['/XObject'].items():
        o = ref.get_object()
        if o.get('/Subtype') != '/Image': continue
        raw = o._data
        filt = o.get('/Filter')
        if filt == '/DCTDecode': im = Image.open(io.BytesIO(raw)); im.load()
        elif filt == '/FlateDecode':
            mode = {'/DeviceRGB': 'RGB', '/DeviceCMYK': 'CMYK'}.get(str(o['/ColorSpace']), 'RGB')
            im = Image.frombytes(mode, (int(o['/Width']), int(o['/Height'])), zlib.decompress(raw))
        else: raise ValueError(filt)
        res[tile_of(int(o['/Width']), int(o['/Height']))] = (name, o, im)
    return res

# ---------------------------------------------------------------- 0. Figma export carries this tag's tiles
full_rgb = np.asarray(Image.open(BLEED).convert('RGB'))
assert full_rgb.shape[:2] == (7087, 5033)
fig = pdf_images(FIGMA)
diffs = {}
for (r, c), (_, _, im) in sorted(fig.items()):
    ref = full_rgb[YS[r]:YS[r + 1], XS[c]:XS[c + 1]].astype(np.int16)
    diffs[f'r{r}c{c}'] = round(float(np.abs(np.asarray(im.convert('RGB'), np.int16) - ref).mean()), 2)
check('figma_export_has_this_tag_tiles', len(fig) == 4 and max(diffs.values()) < 3.0,
      {'mean_abs_diff_vs_local_tiles_0_255': diffs, 'limit': 3.0, 'note': 'Figma re-encodes tiles as 4:2:0 JPEG; a stale tile from another tag gives > 3'})
if '--figma-only' in args:
    sys.exit(0 if checks[-1]['pass'] else 1)

# ---------------------------------------------------------------- 1. page boxes
def boxes(path):
    out = run(['pdfinfo', '-box', path], text=True).stdout
    b = {m.group(1): [float(v) for v in m.group(2).split()] for m in re.finditer(r'^(\w+Box):\s+(.+)$', out, re.M)}
    info = {k.strip(): v.strip() for k, v in (l.split(':', 1) for l in out.splitlines() if ':' in l)}
    return b, info
bp, ip = boxes(PRINT); bs, is_ = boxes(SCREEN)
check('print_boxes', bp['MediaBox'] == MEDIA and bp['BleedBox'] == MEDIA and bp['TrimBox'] == TRIM and bp['CropBox'] == MEDIA,
      {k: bp[k] for k in ('MediaBox', 'CropBox', 'BleedBox', 'TrimBox', 'ArtBox')} | {'trim_mm': [round((TRIM[2] - TRIM[0]) * MM, 2), round((TRIM[3] - TRIM[1]) * MM, 2)], 'pdf_version': ip.get('PDF version'), 'pdf_subtype': ip.get('PDF subtype')})
check('screen_boxes', bs['CropBox'] == TRIM and bs['TrimBox'] == TRIM and bs['MediaBox'] == MEDIA and bs['BleedBox'] == MEDIA,
      {k: bs[k] for k in ('MediaBox', 'CropBox', 'BleedBox', 'TrimBox', 'ArtBox')} | {'page_size': is_.get('Page size')})

# ---------------------------------------------------------------- 2. Ghostscript and poppler messages
def gs_msgs(cmd):
    p = run(cmd, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()
rc1, m1 = gs_msgs([GS, '-q', '-dNOPAUSE', '-dBATCH', '-dSAFER', '-sDEVICE=nullpage', PRINT])
with tempfile.TemporaryDirectory() as td:
    rc2, m2 = gs_msgs([GS, '-q', '-dNOPAUSE', '-dBATCH', '-dSAFER', f'--permit-file-read={P}/', '-sDEVICE=pdfwrite', '-dPDFX=4',
                       '-dCompatibilityLevel=1.6', '-sColorConversionStrategy=CMYK', f'-sOutputICCProfile={ICC}', '-dRenderIntent=1',
                       '-dBlackPtComp=0', f'-sOutputFile={td}/x.pdf', PDFX_DEF, PRINT])
rc3, m3 = gs_msgs([GS, '-q', '-dNOPAUSE', '-dBATCH', '-dSAFER', '-sDEVICE=nullpage', SCREEN])
check('ghostscript_no_messages', rc1 == rc2 == rc3 == 0 and not (m1 or m2 or m3),
      {'print_nullpage': [rc1, m1[:300]], 'print_pdfx4_rerun': [rc2, m2[:300]], 'screen_nullpage': [rc3, m3[:300]], 'gs': run([GS, '--version'], text=True).stdout.strip()})
with tempfile.TemporaryDirectory() as td:
    pp = run(['pdftoppm', '-r', 72, '-png', PRINT, f'{td}/p'], text=True)
    ps = run(['pdftoppm', '-r', 72, '-png', SCREEN, f'{td}/s'], text=True)
    sz_s = Image.open(next(Path(td).glob('s*.png'))).size; sz_p = Image.open(next(Path(td).glob('p*.png'))).size
check('poppler_no_messages', pp.returncode == ps.returncode == 0 and not (pp.stderr.strip() or ps.stderr.strip()),
      {'print_stderr': pp.stderr.strip()[:300], 'screen_stderr': ps.stderr.strip()[:300], 'print_72dpi_px': sz_p, 'screen_72dpi_px': sz_s,
       'poppler': run(['pdftoppm', '-v'], text=True).stderr.splitlines()[0]})

# ---------------------------------------------------------------- 3. fonts, colour spaces, transparency, OutputIntent
def fonts(path):
    return [l for l in run(['pdffonts', path], text=True).stdout.splitlines()[2:] if l.strip()]
fp, fs = fonts(PRINT), fonts(SCREEN)
check('print_fonts_zero', len(fp) == 0, {'print_fonts': len(fp), 'screen_fonts_type3_search_layer': len(fs)})
rd = PdfReader(PRINT); pg = rd.pages[0]
xo = {k: v.get_object() for k, v in pg['/Resources']['/XObject'].items()}
img_info = {k: {'cs': str(o.get('/ColorSpace')), 'filter': str(o.get('/Filter')), 'smask': '/SMask' in o, 'mask': '/Mask' in o,
                'decode': [float(x) for x in o['/Decode']] if '/Decode' in o else None, 'wh': [int(o['/Width']), int(o['/Height'])]}
            for k, o in xo.items() if o.get('/Subtype') == '/Image'}
egs = pg['/Resources'].get('/ExtGState'); egs = {k: dict(v.get_object()) for k, v in egs.items()} if egs else {}
transp = [k for k, v in egs.items() if any(x in v for x in ('/SMask', '/BM')) and str(v.get('/SMask', '/None')) != '/None'
          or float(v.get('/CA', 1)) < 1 or float(v.get('/ca', 1)) < 1]
lst = run(['pdfimages', '-list', PRINT], text=True).stdout.splitlines()[2:]
check('print_images_cmyk_no_smask_no_transparency',
      all(v['cs'] == '/DeviceCMYK' and not v['smask'] and not v['mask'] for v in img_info.values()) and len(img_info) == 4
      and '/Group' not in pg and not transp and not any(' smask ' in l or ' rgb ' in l for l in lst),
      {'images': img_info, 'page_group': '/Group' in pg, 'transparent_extgstate': transp,
       'pdfimages_list': [' '.join(l.split()[3:14]) for l in lst]})
oi = rd.trailer['/Root'].get('/OutputIntents')
oi0 = oi[0].get_object() if oi else {}
prof = oi0.get('/DestOutputProfile').get_object().get_data() if oi else b''
check('output_intent', bool(oi) and oi0.get('/S') == '/GTS_PDFX' and hashlib.md5(prof).hexdigest() == hashlib.md5(ICC.read_bytes()).hexdigest(),
      {'S': str(oi0.get('/S')), 'OutputConditionIdentifier': str(oi0.get('/OutputConditionIdentifier')),
       'OutputCondition': str(oi0.get('/OutputCondition')), 'profile_md5_equals_icc_file': hashlib.md5(prof).hexdigest() == hashlib.md5(ICC.read_bytes()).hexdigest(),
       'profile_bytes': len(prof), 'GTS_PDFXVersion': str(rd.trailer['/Info'].get('/GTS_PDFXVersion'))})

# ---------------------------------------------------------------- 4. tile placement (exact) + 600 ppi seam strips
cs = pg.get_contents().get_data().decode('latin1').split('\n')
place = []
for i, ln in enumerate(cs):
    m = re.match(r'q ([-\d.]+) 0 0 ([-\d.]+) ([-\d.]+) ([-\d.]+) cm$', ln)
    if m and i + 1 < len(cs) and cs[i + 1].endswith(' Do'):
        pts = []
        j = i - 1
        while not cs[j].startswith('q') or cs[j] != 'q':
            mm = re.match(r'([-\d.]+) ([-\d.]+) [ml]$', cs[j])
            if mm: pts.append((float(mm.group(1)), float(mm.group(2))))
            j -= 1
        a, d, e, f = map(float, m.groups())
        xs_, ys_ = [p[0] for p in pts], [p[1] for p in pts]
        place.append({'xobj': cs[i + 1].split()[0], 'clip_pt': [min(xs_) / 10, min(ys_) / 10, max(xs_) / 10, max(ys_) / 10],
                      'img_pt': [e / 10, f / 10, (e + a) / 10, (f + d) / 10]})
cover = all(p['img_pt'][0] <= p['clip_pt'][0] + 1e-3 and p['img_pt'][1] <= p['clip_pt'][1] + 1e-3 and
            p['img_pt'][2] >= p['clip_pt'][2] - 1e-3 and p['img_pt'][3] >= p['clip_pt'][3] - 1e-3 for p in place)
cx = sorted({p['clip_pt'][k] for p in place for k in (0, 2)}); cy = sorted({p['clip_pt'][k] for p in place for k in (1, 3)})
abut = len(cx) == 3 and len(cy) == 3 and cx[0] == 0 and cx[-1] == 1208 and cy[0] == 0 and cy[-1] == 1701
seam_x_pt, seam_y_pt = cx[1], 1701 - cy[1]                         # seam y measured from the top
R = 600; k = R / 72
def strip(x, y, w, h, name):
    pre = OUT / name
    run(['pdftoppm', '-r', R, '-x', x, '-y', y, '-W', w, '-H', h, '-png', '-singlefile', PRINT, pre], check=True)
    return np.asarray(Image.open(f'{pre}.png').convert('L'), np.float32)
x0 = int(seam_x_pt * k) - 40
V = strip(x0, 0, 80, int(1701 * k), 'seam600_vertical_strip')        # full height, 80 px around the vertical seam
y0 = int(seam_y_pt * k) - 40
H = strip(0, y0, int(1208 * k), 80, 'seam600_horizontal_strip').T    # full width, transposed -> columns = rows
def seam_stats(S, at):
    d = np.abs(np.diff(S, axis=1)).mean(0)                     # mean |step| between neighbouring columns
    j = int(at)                                                # step index that crosses the seam (+-1)
    near = np.r_[d[:j - 2], d[j + 3:]]
    col = S.mean(0); nb = np.r_[col[j - 8:j - 2], col[j + 3:j + 9]].mean()
    bright = ((S[:, j] - np.maximum(S[:, j - 2], S[:, j + 2])) > 12).mean()
    return {'step_at_seam': round(float(d[j - 1:j + 2].max()), 2), 'step_median_elsewhere': round(float(np.median(near)), 2),
            'step_p99_elsewhere': round(float(np.percentile(near, 99)), 2),
            'seam_col_mean_minus_neighbours': round(float(col[j - 1:j + 2].mean() - nb), 2),
            'rows_with_light_hairline_pct': round(float(bright * 100), 3)}
sv = seam_stats(V, seam_x_pt * k - x0); sh = seam_stats(H, seam_y_pt * k - y0)
ok_seam = cover and abut and all(s['step_at_seam'] <= s['step_p99_elsewhere'] and abs(s['seam_col_mean_minus_neighbours']) < 2
                                 and s['rows_with_light_hairline_pct'] < 0.5 for s in (sv, sh))
Image.fromarray(V[int(850 * k) - 300:int(850 * k) + 300].astype(np.uint8)).save(OUT / 'seam600_vertical_strip_mid.png')
crop = run(['pdftoppm', '-r', R, '-x', int(seam_x_pt * k) - 300, '-y', int(seam_y_pt * k) - 300, '-W', 600, '-H', 600, '-png', '-singlefile', PRINT, OUT / 'seam600_intersection'])
check('tile_seams', ok_seam, {'placements': place, 'images_cover_their_clip': cover, 'clips_tile_page_exactly': abut,
                              'seam_pt': {'x': seam_x_pt, 'y_from_top': round(seam_y_pt, 2)}, 'vertical_seam_600ppi': sv, 'horizontal_seam_600ppi': sh})

# ---------------------------------------------------------------- 5. image in the print PDF vs the render (dE00)
pim = pdf_images(PRINT)
cmyk = np.zeros((7087, 5033, 4), np.uint8); qt = []
for (r, c), (_, o, im) in pim.items():
    assert im.mode == 'CMYK', im.mode
    cmyk[YS[r]:YS[r + 1], XS[c]:XS[c + 1]] = np.asarray(im)
    q = getattr(im, 'quantization', None) or {}
    qt += [float(np.mean(t)) for t in q.values()]
    qt_max = max([max(t) for t in q.values()] + [0])
tac = cmyk.astype(np.uint16).sum(2) * (100 / 255)
rng = np.random.default_rng(0); N = 1_000_000
ys = rng.integers(36, 7051, N); xs = rng.integers(36, 4997, N)      # integer pixels fully inside the trim (35.5 px)

def transicc(src, dst, arr, fmt):
    inp = '\n'.join(' '.join(fmt % v for v in row) for row in arr) + '\n'
    p = subprocess.run(['transicc', '-t1', '-n', '-i', src, '-o', dst], input=inp.encode(), capture_output=True, check=True)
    out = np.array(p.stdout.split(), dtype=np.float64)
    return out.reshape(len(arr), -1)
def de00(L1, L2):
    l1, a1, b1 = L1.T; l2, a2, b2 = L2.T
    C1, C2 = np.hypot(a1, b1), np.hypot(a2, b2); Cm = (C1 + C2) / 2
    G = 0.5 * (1 - np.sqrt(Cm ** 7 / (Cm ** 7 + 25 ** 7)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = np.hypot(a1p, b1), np.hypot(a2p, b2)
    h1p, h2p = np.degrees(np.arctan2(b1, a1p)) % 360, np.degrees(np.arctan2(b2, a2p)) % 360
    dL, dC = l2 - l1, C2p - C1p
    dh = h2p - h1p; dh = np.where(dh > 180, dh - 360, np.where(dh < -180, dh + 360, dh)); dh = np.where(C1p * C2p == 0, 0, dh)
    dH = 2 * np.sqrt(C1p * C2p) * np.sin(np.radians(dh / 2))
    Lm, Cmp = (l1 + l2) / 2, (C1p + C2p) / 2
    hs = h1p + h2p
    hm = np.where(C1p * C2p == 0, hs, np.where(np.abs(h1p - h2p) <= 180, hs / 2, np.where(hs < 360, (hs + 360) / 2, (hs - 360) / 2)))
    T = 1 - 0.17 * np.cos(np.radians(hm - 30)) + 0.24 * np.cos(np.radians(2 * hm)) + 0.32 * np.cos(np.radians(3 * hm + 6)) - 0.20 * np.cos(np.radians(4 * hm - 63))
    SL = 1 + 0.015 * (Lm - 50) ** 2 / np.sqrt(20 + (Lm - 50) ** 2); SC = 1 + 0.045 * Cmp; SH = 1 + 0.015 * Cmp * T
    RT = -2 * np.sqrt(Cmp ** 7 / (Cmp ** 7 + 25 ** 7)) * np.sin(np.radians(60 * np.exp(-((hm - 275) / 25) ** 2)))
    return np.sqrt((dL / SL) ** 2 + (dC / SC) ** 2 + (dH / SH) ** 2 + RT * (dC / SC) * (dH / SH))
def dist(d):
    return {'median': round(float(np.median(d)), 3), 'p95': round(float(np.percentile(d, 95)), 3), 'p99': round(float(np.percentile(d, 99)), 3),
            'p99_9': round(float(np.percentile(d, 99.9)), 3), 'max_in_sample': round(float(d.max()), 3), 'mean': round(float(d.mean()), 3)}
rgb_s = full_rgb[ys, xs].astype(np.float64)
pdf_c = cmyk[ys, xs].astype(np.float64) * (100 / 255)
lab_ref = transicc('*sRGB', '*Lab', rgb_s, '%.0f')
lab_pdf = transicc(str(ICC), '*Lab', pdf_c, '%.4f')
cmyk_ref = transicc('*sRGB', str(ICC), rgb_s, '%.0f')          # same separation recipe: relative, no BPC
lab_ref_sep = transicc(str(ICC), '*Lab', cmyk_ref, '%.4f')
d_total, d_enc = de00(lab_ref, lab_pdf), de00(lab_ref_sep, lab_pdf)
d_gamut = de00(lab_ref, lab_ref_sep)
plate_err = np.abs(cmyk_ref - pdf_c)
# polarity / identity probe through Ghostscript's own decoder (guards against a CMYK JPEG inversion slip)
with tempfile.TemporaryDirectory() as td:
    run([GS, '-q', '-dNOPAUSE', '-dBATCH', '-dSAFER', '-sDEVICE=tiff32nc', '-r30', f'-sOutputFile={td}/g.tif', PRINT], check=True)
    g = np.asarray(Image.open(f'{td}/g.tif')).astype(np.float64)
    small = np.asarray(Image.fromarray(cmyk[:, :, 3]).resize(g.shape[1::-1], Image.BOX), np.float64)
    k_corr = float(np.corrcoef(g[:, :, 3].ravel(), small.ravel())[0, 1])
res = {'n_pixels_sampled_inside_trim': N, 'dE00_pdf_vs_render_total': dist(d_total),
       'dE00_pdf_vs_render_separated_same_recipe(JPEG+gs only)': dist(d_enc),
       'dE00_gamut_mapping_only(render_vs_its_own_separation)': dist(d_gamut),
       'plate_abs_err_pct_vs_same_recipe': {'median': round(float(np.median(plate_err)), 2), 'p99': round(float(np.percentile(plate_err, 99)), 2)},
       'K_plate_corr_with_gs_render_30dpi': round(k_corr, 4)}
ok_de = np.percentile(d_enc, 99) < 2.0 and np.median(d_enc) < 0.6 and k_corr > 0.98
if prev and (P / f'{prev}_map_print_bleed_5033x7087.png').exists():
    old = np.asarray(Image.open(P / f'{prev}_map_print_bleed_5033x7087.png').convert('RGB'))
    ch = (np.abs(old.astype(np.int16) - full_rgb).max(2) > 24)
    ch[:36] = ch[7051:] = False; ch[:, :36] = ch[:, 4997:] = False
    cy_, cx_ = np.nonzero(ch); sel = rng.choice(len(cy_), min(100_000, len(cy_)), replace=False) if len(cy_) else np.array([], int)
    if len(sel):
        cy_, cx_ = cy_[sel], cx_[sel]
        lp = transicc(str(ICC), '*Lab', cmyk[cy_, cx_].astype(np.float64) * (100 / 255), '%.4f')
        sep_new = transicc(str(ICC), '*Lab', transicc('*sRGB', str(ICC), full_rgb[cy_, cx_].astype(np.float64), '%.0f'), '%.4f')
        sep_old = transicc(str(ICC), '*Lab', transicc('*sRGB', str(ICC), old[cy_, cx_].astype(np.float64), '%.0f'), '%.4f')
        dn, do = de00(sep_new, lp), de00(sep_old, lp)
        res[f'changed_pixels_{prev}_to_{tag}_inside_trim'] = int(ch.sum())
        res[f'on_changed_pixels_median_dE00_vs_{tag}'] = round(float(np.median(dn)), 3)
        res[f'on_changed_pixels_median_dE00_vs_{prev}'] = round(float(np.median(do)), 3)
        ok_de = ok_de and np.median(dn) < 1.0 < np.median(do)
dr = ROOT / f'renders/narrative_{tag}_map_pass.png'
if dr.exists():                                                 # same camera framing as the screen design render?
    m = Image.open(dr).convert('RGBA'); o = Image.open(ROOT / f'renders/narrative_{tag}_overlay_pass.png').convert('RGBA')
    des = np.asarray(Image.alpha_composite(m, o).convert('RGB'), np.int16)
    trim_ds = np.asarray(Image.fromarray(full_rgb).resize(des.shape[1::-1], Image.LANCZOS, box=(35.5, 35.5, 4997.5, 7051.5)), np.int16)
    dd = np.abs(trim_ds - des).max(2)
    res[f'trim_area_vs_design_render_narrative_{tag}'] = {'design_px': list(des.shape[1::-1]), 'mean_abs_0_255': round(float(np.abs(trim_ds - des).mean()), 2),
                                                          'p99_max_channel': int(np.percentile(dd, 99))}
check('trim_image_equals_render', ok_de, res)
check('tac_max_le_300pct', tac.max() <= 300.5, {'tac_max_pct': round(float(tac.max()), 1), 'tac_p999_pct': round(float(np.percentile(tac, 99.9)), 1),
                                                 'jpeg_quant_mean': round(float(np.mean(qt)), 2) if qt else None, 'jpeg_quant_max': qt_max})

# ---------------------------------------------------------------- 6. safe area: outermost vector ink (images + paper fill removed)
wr = PdfWriter(clone_from=PdfReader(PRINT)); p2 = wr.pages[0]
c2 = p2.get_contents(); lines = c2.get_data().split(b'\n')
lines = [b'' if l.endswith(b' Do') else l for l in lines]
first_k = next(i for i, l in enumerate(lines) if l.endswith(b' k'))
paper = lines[first_k].decode(); lines[first_k] = b'0 0 0 0 k'      # frame background -> paper white
c2.set_data(b'\n'.join(lines)); p2.replace_contents(c2)
ink_pdf = OUT / '_vector_ink_only.pdf'
with open(ink_pdf, 'wb') as f: wr.write(f)
R2 = 300
run(['pdftoppm', '-r', R2, '-gray', '-png', '-singlefile', ink_pdf, OUT / 'vector_ink_only_300'], check=True)
ink = np.asarray(Image.open(OUT / 'vector_ink_only_300.png')) < 250
yy, xx = np.nonzero(ink); s = 72 / R2
sides = {'left': (xx.min() * s - TRIM[0]), 'right': (TRIM[2] - (xx.max() + 1) * s),
         'top': (yy.min() * s - (1701 - TRIM[3])), 'bottom': ((1701 - TRIM[1]) - (yy.max() + 1) * s)}
where = {'left': (xx.min(), yy[xx == xx.min()].mean()), 'right': (xx.max(), yy[xx == xx.max()].mean()),
         'top': (xx[yy == yy.min()].mean(), yy.min()), 'bottom': (xx[yy == yy.max()].mean(), yy.max())}
words = []
bb = run(['pdftotext', '-bbox', FIGMA, '-'], text=True).stdout
for m_ in re.finditer(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>', bb):
    words.append((*map(float, m_.groups()[:4]), m_.group(5)))
def near_word(px, py):
    x, y = px * s, py * s
    return min(words, key=lambda w: max(w[0] - x, 0, x - w[2]) + max(w[1] - y, 0, y - w[3]))[4] if words else None
safe = {side: {'mm': round(v * MM, 2), 'pt': round(v, 2), 'at_pt': [round(where[side][0] * s, 1), round(where[side][1] * s, 1)],
               'nearest_search_word': near_word(*where[side])} for side, v in sides.items()}
check('safe_area_ge_6_35mm', min(v['mm'] for v in safe.values()) >= 6.35, {'outermost_vector_ink_from_trim': safe, 'removed_paper_fill': paper,
                                                                          'ink_threshold': 'gray < 250 at 300 ppi (incl. anti-alias fringe)'})
ink_pdf.unlink()

# ---------------------------------------------------------------- 7. screen PDF: searchable text
txt = run(['pdftotext', '-nopgbrk', SCREEN, '-'], text=True).stdout
check('screen_pdf_searchable', '로마 콘크리트' in txt.replace('\n', ' ') or '로마' in txt, {'chars': len(txt), 'sample': txt.strip()[:60]})

summary = {'tag': tag, 'pass': all(c['pass'] for c in checks), 'checks': checks,
           'print_pdf': {'path': str(PRINT), 'bytes': PRINT.stat().st_size, 'sha1': hashlib.sha1(PRINT.read_bytes()).hexdigest()},
           'screen_pdf': {'path': str(SCREEN), 'bytes': SCREEN.stat().st_size, 'sha1': hashlib.sha1(SCREEN.read_bytes()).hexdigest()}}
(OUT / f'verify_{tag}.json').write_text(json.dumps(summary, ensure_ascii=False, indent=1))
print('ALL PASS' if summary['pass'] else 'SOME CHECKS FAILED', OUT / f'verify_{tag}.json')
sys.exit(0 if summary['pass'] else 1)
