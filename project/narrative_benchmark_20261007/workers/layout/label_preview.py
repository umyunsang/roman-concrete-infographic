"""Paste the r10 glyphs of 797:79 and 802:78 at the proposed positions onto the new composite (preview only).
uv run -q --no-project --with pillow --with numpy python -I label_preview.py <render_prefix> <labels.json> <out.png>"""
import sys, json
import numpy as np
from PIL import Image
NB = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work'
pre, lab_p, out = sys.argv[1:4]; lab = json.load(open(lab_p))
S2 = 2.0; W2, H2 = 2382, 3368
m = Image.open(pre + '_map_pass.png').convert('RGBA'); o = Image.open(pre + '_overlay_pass.png').convert('RGBA')
C = np.array(Image.alpha_composite(m, o).convert('RGB').resize((W2, H2), Image.Resampling.LANCZOS)).astype(float)
po = np.array(Image.open(NB + '/review_loop/r10/poster_2x.png').convert('RGB')).astype(float)
mo = np.array(Image.open(NB + '/review_loop/r10/map_only_2x.png').convert('RGB')).astype(float)
def paste(box, new_xy):
    x, y, w, h = box; pad = 2
    x0, y0, x1, y1 = int((x - pad) * S2), int((y - pad) * S2), int((x + w + pad) * S2), int((y + h + pad) * S2)
    P, Mo = po[y0:y1, x0:x1], mo[y0:y1, x0:x1]
    a = np.clip(np.abs(P - Mo).max(2) / 120.0, 0, 1)[..., None]       # glyph coverage
    dx, dy = int(round((new_xy[0] - x) * S2)), int(round((new_xy[1] - y) * S2))
    tgt = C[y0 + dy:y1 + dy, x0 + dx:x1 + dx]
    ink = np.array((0x59, 0x52, 0x4A), float)
    C[y0 + dy:y1 + dy, x0 + dx:x1 + dx] = tgt * (1 - a) + ink * a
paste(lab['802:78']['box_r10'], lab['802:78']['new_box_xy'])
paste(lab['797:79']['box_r10'], lab['797:79']['candidates_keep_8pt_x'][0]['box_xy'])
im = Image.fromarray(C.clip(0, 255).astype(np.uint8))
a = im.crop((int(270 * S2), int(420 * S2), int(480 * S2), int(540 * S2))).resize((int(210 * 4), int(120 * 4)), Image.Resampling.LANCZOS)
b = im.crop((int(680 * S2), int(560 * S2), int(840 * S2), int(700 * S2))).resize((int(160 * 4), int(140 * 4)), Image.Resampling.LANCZOS)
S = Image.new('RGB', (a.width + b.width + 10, max(a.height, b.height)), 'white'); S.paste(a, (0, 0)); S.paste(b, (a.width + 10, 0)); S.save(out)
print(out, S.size)
