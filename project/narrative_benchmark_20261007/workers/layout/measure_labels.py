"""Figma label moves for the layout step, measured on pixels.
Run: uv run -q --no-project --with pillow --with numpy --with scipy python -I measure_labels.py <render_prefix> <step_report.json> <gaps_masks.npz> <out.json>
- map ink = composite (map pass + overlay pass) pixels whose RGB distance to the paper colour exceeds 20
- label glyphs = r10 poster_2x minus map_only_2x (> 40 in any channel) inside each text box (text_spec_r10)
- 802:78 (Colosseum) moves by the screen shift of the NE wall point next to it (from the step report)
- 797:79 (Pantheon) candidate: glyph right edge 8pt left of the Pantheon silhouette, glyph centre on the Pantheon's
  vertical centre; if map ink or other text is closer than 4pt, the nearest position on a 0.5pt grid that clears it."""
import sys, json
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt

NB = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work'
pre, rep_p, masks_p, out_p = sys.argv[1:5]
rep = json.load(open(rep_p)); MK = np.load(masks_p)
spec = json.load(open(NB + '/review_loop/text_spec_r10.json'))['texts']
S2 = 2.0                                     # work grid: 2 px per pt, 1191 x 1684 pt
W2, H2 = int(1191 * S2), int(1684 * S2)
m = Image.open(pre + '_map_pass.png').convert('RGBA'); o = Image.open(pre + '_overlay_pass.png').convert('RGBA')
comp = Image.alpha_composite(m, o).convert('RGB').resize((W2, H2), Image.Resampling.LANCZOS)
C = np.array(comp).astype(float)
sub = C[::7, ::7].reshape(-1, 3).round().astype(int); v, c = np.unique(sub, axis=0, return_counts=True)
paper = v[np.argmax(c)].astype(float)
ink = np.linalg.norm(C - paper, axis=2) > 20
mo = np.array(Image.open(NB + '/review_loop/r10/map_only_2x.png').convert('RGB').resize((W2, H2), Image.Resampling.NEAREST)).astype(float)
po = np.array(Image.open(NB + '/review_loop/r10/poster_2x.png').convert('RGB').resize((W2, H2), Image.Resampling.NEAREST)).astype(float)
sub = mo[::7, ::7].reshape(-1, 3).round().astype(int); v, c = np.unique(sub, axis=0, return_counts=True)
paper_old = v[np.argmax(c)].astype(float)
ink_old = np.linalg.norm(mo - paper_old, axis=2) > 20
txt = np.abs(po - mo).max(2) > 40
d_ink = distance_transform_edt(~ink) / S2
d_ink_old = distance_transform_edt(~ink_old) / S2


def glyphs(box, pad=2):
    x, y, w, h = box
    x0, y0 = int((x - pad) * S2), int((y - pad) * S2); x1, y1 = int((x + w + pad) * S2), int((y + h + pad) * S2)
    ys, xs = np.nonzero(txt[y0:y1, x0:x1])
    return np.c_[(xs + x0 + 0.5) / S2, (ys + y0 + 0.5) / S2]


def min_d(D, G, shift=(0.0, 0.0)):
    q = np.round((G + shift) * S2 - 0.5).astype(int)
    ok = (q[:, 0] >= 0) & (q[:, 0] < W2) & (q[:, 1] >= 0) & (q[:, 1] < H2)
    return float(D[q[ok, 1], q[ok, 0]].min())


res = {'paper_rgb_new': paper.tolist(), 'paper_rgb_r10': paper_old.tolist(), 'ink_rule': 'RGB distance to paper > 20'}
boxes = {t[0]: t[1] for t in spec}
# ---- 802:78 Colosseum label
G = glyphs(boxes['802:78'])
sh = np.array(rep['colosseum']['screen_shift_at_label_wall'])
X0, Y0, S4 = MK['origin']
col = MK['COL']; dcol = distance_transform_edt(~col) / S4
def d_mask(Dm, G, shift):
    q = np.floor((G + shift - (X0, Y0)) * S4).astype(int)
    q[:, 0] = np.clip(q[:, 0], 0, Dm.shape[1] - 1); q[:, 1] = np.clip(q[:, 1], 0, Dm.shape[0] - 1)
    return float(Dm[q[:, 1], q[:, 0]].min())
b = boxes['802:78']
res['802:78'] = {'text': '콜로세움', 'box_r10': b, 'rotation': -30,
                 'move_by_pt': [round(float(sh[0]), 1), round(float(sh[1]), 1)],
                 'new_box_xy': [round(b[0] + sh[0], 1), round(b[1] + sh[1], 1)],
                 'ink_gap_to_map_r10_pt': round(min_d(d_ink_old, G), 2),
                 'ink_gap_to_map_if_not_moved_pt': round(min_d(d_ink, G), 2),
                 'ink_gap_to_map_after_move_pt': round(min_d(d_ink, G, sh), 2),
                 'ink_gap_to_colosseum_after_move_pt': round(d_mask(dcol, G, sh), 2)}
# ---- 797:79 Pantheon label
G = glyphs(boxes['797:79'])
gx0, gx1, gy0, gy1 = G[:, 0].min() - 0.25, G[:, 0].max() + 0.25, G[:, 1].min() - 0.25, G[:, 1].max() + 0.25
pan = MK['PAN']; ys, xs = np.nonzero(pan)
pxl = X0 + xs.min() / S4; pyt, pyb = Y0 + ys.min() / S4, Y0 + (ys.max() + 1) / S4
dpan = distance_transform_edt(~pan) / S4
others = np.zeros_like(txt)
for tid, bx in boxes.items():
    if tid in ('797:79', '802:78'): continue
    Gt = glyphs(bx, pad=0.5); q = np.round(Gt * S2 - 0.5).astype(int); others[q[:, 1], q[:, 0]] = True
Gc = glyphs(boxes['802:78']) + sh; q = np.round(Gc * S2 - 0.5).astype(int); others[q[:, 1], q[:, 0]] = True
d_txt = distance_transform_edt(~others) / S2
pan_ink = np.zeros_like(ink)
sel = np.round((np.c_[X0 + (xs + 0.5) / S4, Y0 + (ys + 0.5) / S4]) * S2 - 0.5).astype(int); pan_ink[sel[:, 1], sel[:, 0]] = True
d_nonpan = distance_transform_edt(~(ink & ~pan_ink)) / S2       # map ink other than the Pantheon itself
ideal = np.array((pxl - 8 - gx1, (pyt + pyb) / 2 - (gy0 + gy1) / 2))
def score(shift):
    return {'map_ink_other_than_pantheon': round(min_d(d_nonpan, G, shift), 2), 'map_ink_all': round(min_d(d_ink, G, shift), 2),
            'other_text': round(min_d(d_txt, G, shift), 2), 'pantheon': round(d_mask(dpan, G, shift), 2)}
cands = []
for dy in np.arange(-24, 24.01, 0.5):
    for dx in np.arange(-12, 6.01, 0.5):
        shf = ideal + (dx, dy)
        sc_ = score(shf)
        if sc_['map_ink_other_than_pantheon'] >= 4 and sc_['other_text'] >= 4 and 7.5 <= sc_['pantheon'] <= 12:
            cands.append((abs(dx) + abs(dy), dx, dy, sc_))
cands.sort(key=lambda c_: c_[0])
box = boxes['797:79']; goff = (box[0] - (gx0 + 0.25), box[1] - (gy0 + 0.25))
def as_box(shift):
    return [round(float(gx0 + 0.25 + shift[0] + goff[0]), 1), round(float(gy0 + 0.25 + shift[1] + goff[1]), 1)]
res['797:79'] = {'text': '판테온 · 철근 없는 돔', 'box_r10': box,
                 'pantheon_silhouette_pt': {'left': round(float(pxl), 2), 'top': round(float(pyt), 2), 'bottom': round(float(pyb), 2)},
                 'ideal_box_xy': as_box(ideal), 'ideal_scores': score(ideal),
                 'r10_position_scores_after_move': score(np.zeros(2)),
                 'candidates': [{'box_xy': as_box(ideal + (c_[1], c_[2])), 'offset_from_ideal': [c_[1], c_[2]], **c_[3]} for c_ in cands[:5]]}
# ---- every r10 text: gap to map ink before/after (flag the ones that got closer than 4pt)
flag = {}
for tid, bx in boxes.items():
    Gt = glyphs(bx, pad=0.5)
    if len(Gt) == 0: continue
    shift = sh if tid == '802:78' else np.zeros(2)
    a, b_ = min_d(d_ink_old, Gt), min_d(d_ink, Gt, shift)
    if b_ < a - 0.5 and b_ < 6:
        flag[tid] = {'text': ''.join(s_[0] for s_ in [t for t in spec if t[0] == tid][0][4])[:20], 'gap_r10': round(a, 2), 'gap_new': round(b_, 2)}
res['texts_closer_to_map_ink'] = flag
res['named_text_gaps'] = {}
for tid in ('790:103', '790:146', '790:147', '790:148', '797:80', '790:104', '790:110', '790:111', '790:158', '790:164'):
    Gt = glyphs(boxes[tid], pad=0.5)
    res['named_text_gaps'][tid] = {'text': ''.join(s_[0] for s_ in [t for t in spec if t[0] == tid][0][4])[:16],
                                   'gap_r10': round(min_d(d_ink_old, Gt), 2), 'gap_new': round(min_d(d_ink, Gt), 2)}
json.dump(res, open(out_p, 'w'), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False)[:3000])
