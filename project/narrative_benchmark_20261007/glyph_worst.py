import sys, json
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/colorjudge_r9')
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt, binary_dilation
from colorlib import *
R = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
im = np.array(Image.open(R + 'r9/poster_2x.png').convert('RGB')).astype(float)
mp = np.array(Image.open(R + 'r9/map_only_2x.png').convert('RGB')).astype(float)
H, W = im.shape[:2]
diff = np.abs(im - mp).max(-1)
# global alignment check on area with no text (sea bottom right)
print('diff median whole', np.median(diff), 'p99', np.percentile(diff, 99), 'frac>30', (diff > 30).mean())
spec = json.load(open(R + 'text_spec_r9.json'))['texts']
out = []
for tid, box, rot, al, segs in spec:
    x, y, w, h = box
    light = segs[0][5] == '#FFF4DD'
    cols = sorted({s[5] for s in segs}, key=lambda c: -rel_lum(hex2rgb(c)))
    tc = hex2rgb(cols[0]); Yt = rel_lum(tc); labt = rgb2lab(tc)
    bx0, by0 = int(np.floor((x - 1) * 2)), int(np.floor((y - 1) * 2))
    bx1, by1 = int(np.ceil((x + w + 1) * 2)), int(np.ceil((y + h + 1) * 2))
    m = 12
    cx0, cy0, cx1, cy1 = max(0, bx0 - m), max(0, by0 - m), min(W, bx1 + m), min(H, by1 + m)
    crop = im[cy0:cy1, cx0:cx1]; dcrop = diff[cy0:cy1, cx0:cx1]
    Y = rel_lum(crop)
    inbox = np.zeros(Y.shape, bool); inbox[by0 - cy0:by1 - cy0, bx0 - cx0:bx1 - cx0] = True
    Yb0 = np.percentile(Y[inbox], 15 if light else 80)
    mask = inbox & (np.abs(Y - Yt) < 0.5 * abs(Yb0 - Yt)) & (de76(rgb2lab(crop), labt) < 40)
    textlayer = binary_dilation(dcrop > 25, iterations=1)
    gm = mask & textlayer
    if gm.sum() == 0:
        out.append((tid, 'nomask')); continue
    dist = distance_transform_edt(~gm); ring = (dist > 3) & (dist <= 9)
    rp = crop[ring]
    if light: rp = rp[rel_lum(rp) < 0.25]
    lc = np.abs(apca_lc(np.broadcast_to(tc, rp.shape), rp))
    bg = np.median(rp, 0)
    out.append((tid, ''.join(s[0] for s in segs)[:14].replace('\n', '/'), int(mask.sum()), int(gm.sum()), float(np.percentile(lc, 10)), float(abs(apca_lc(tc, bg))), float(wcag(tc, bg)), float(np.percentile(lc, 2))))
out = [o for o in out if o[1] != 'nomask']
for o in sorted(out, key=lambda o: o[4])[:14]:
    print(f'{o[0]:8s} {o[1]:16s} mask {o[2]:5d} glyph {o[3]:5d} worst10 {o[4]:.1f}  median-bg Lc {o[5]:.1f} WCAG {o[6]:.2f} p2 {o[7]:.1f}')
print('n', len(out), 'min worst10', min(o[4] for o in out))
