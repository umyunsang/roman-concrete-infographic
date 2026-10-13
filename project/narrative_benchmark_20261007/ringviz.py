import sys, json
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/colorjudge_r9')
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt
from colorlib import *
R = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
im = np.array(Image.open(R + 'r9/poster_2x.png').convert('RGB')).astype(float)
H, W = im.shape[:2]
spec = {t[0]: t for t in json.load(open(R + 'text_spec_r9.json'))['texts']}
tiles = []
for tid in sys.argv[1:]:
    _, box, rot, al, segs = spec[tid]
    x, y, w, h = box
    tc = hex2rgb(segs[0][5]); Yt = rel_lum(tc); labt = rgb2lab(tc)
    bx0, by0 = int(np.floor((x - 1) * 2)), int(np.floor((y - 1) * 2))
    bx1, by1 = int(np.ceil((x + w + 1) * 2)), int(np.ceil((y + h + 1) * 2))
    m = 12
    cx0, cy0, cx1, cy1 = max(0, bx0 - m), max(0, by0 - m), min(W, bx1 + m), min(H, by1 + m)
    crop = im[cy0:cy1, cx0:cx1]
    Y = rel_lum(crop)
    inbox = np.zeros(Y.shape, bool); inbox[by0 - cy0:by1 - cy0, bx0 - cx0:bx1 - cx0] = True
    Yb0 = np.percentile(Y[inbox], 80)
    mask = inbox & (np.abs(Y - Yt) < 0.5 * abs(Yb0 - Yt)) & (de76(rgb2lab(crop), labt) < 40)
    dist = distance_transform_edt(~mask); ring = (dist > 3) & (dist <= 9)
    lc = np.abs(apca_lc(np.broadcast_to(tc, crop.shape), crop))
    low = ring & (lc < 45)
    ov = crop.copy()
    ov[mask] = [255, 0, 255]
    ov[low] = [0, 200, 0]
    both = np.concatenate([crop, ov], 1).astype(np.uint8)
    Image.fromarray(both).resize((both.shape[1] * 2, both.shape[0] * 2), Image.NEAREST).save(f'ring_{tid.replace(":", "_")}.png')
    print(tid, 'ring', ring.sum(), 'low<45', low.sum(), f'{low.sum()/ring.sum()*100:.1f}%', 'p10', np.percentile(lc[ring], 10), 'p5', np.percentile(lc[ring], 5), 'p20', np.percentile(lc[ring], 20))
