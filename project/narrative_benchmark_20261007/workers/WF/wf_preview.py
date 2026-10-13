"""Preview: move a Figma label's glyphs by (dx, dy) pt on the r11 poster_2x (alpha re-estimated from the label colour), crop 3x.
Run: uv run ... python -I wf_preview.py <WF dir> <out.png> <crop x0 y0 x1 y1> <tid:dx:dy> [...]"""
import sys, json; sys.path.insert(0, sys.argv[1])
from wf_common import *
out = sys.argv[2]; cx0, cy0, cx1, cy1 = map(float, sys.argv[3:7]); moves = sys.argv[7:]
po, mo, paper, ink, txt = load_maps()
spec = {t[0]: t for t in json.load(open(RL + '/text_spec_r11.json'))['texts']}
img = po.copy()
for mv in moves:
    tid, dx, dy = mv.split(':'); dx, dy = float(dx), float(dy)
    x, y, w, h = spec[tid][1]; col = np.array([int(spec[tid][4][0][5][i:i + 2], 16) for i in (1, 3, 5)], float)
    x0, y0, x1, y1 = int((x - 2) * 2), int((y - 2) * 2), int((x + w + 2) * 2), int((y + h + 2) * 2)
    P = po[y0:y1, x0:x1]; M = mo[y0:y1, x0:x1]
    lum = np.array([0.299, 0.587, 0.114])
    a = ((M @ lum) - (P @ lum)) / np.maximum((M @ lum) - (col @ lum), 1e-3)
    a = np.clip(a, 0, 1); a[np.abs(P - M).max(2) <= 2] = 0
    img[y0:y1, x0:x1] = np.where(a[..., None] > 0, M, img[y0:y1, x0:x1])
    ox, oy = int(round(dx * 2)), int(round(dy * 2))
    T = img[y0 + oy:y1 + oy, x0 + ox:x1 + ox]
    img[y0 + oy:y1 + oy, x0 + ox:x1 + ox] = a[..., None] * col + (1 - a[..., None]) * T
c = Image.fromarray(img[int(cy0 * 2):int(cy1 * 2), int(cx0 * 2):int(cx1 * 2)].round().clip(0, 255).astype(np.uint8))
c = c.resize((int((cx1 - cx0) * 3), int((cy1 - cy0) * 3)), Image.Resampling.LANCZOS)
c.save(out); print(out, c.size)
