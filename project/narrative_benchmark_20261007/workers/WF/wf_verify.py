"""WF verification on the real Figma export (after) vs r11 (before), v8_14 map.
Run: uv run -q --no-project --with pillow --with numpy --with scipy python -I wf_verify.py <WF dir> <poster_after_2x> <out.json>
- glyphs = export vs map_only_2x differ by > 40 (any channel) inside the r12 text box (+1pt pad)
- map ink (search rule) = every visible object except the ground (ID pass) + ground darker than paper by > 20 luma (cast shadows);
  the old pixel rule (RGB distance to paper > 20, which also flags lit slopes) is reported as ink_px_rule
- d_own / d_other (named assets only: no fields, trees, core roads, 2D markers) / d_rev as in OBJ_INFO-25 and OBJ_PLACE-13
- 3x before/after crops of each moved label into <WF dir>/crops/"""
import sys, json
sys.path.insert(0, sys.argv[1])
from wf_common import *

WF, after_p, out_p = sys.argv[1:4]
inv, objs, name2id, final, pxpt, f2, assets = load_ids()
spec11 = {t[0]: t for t in json.load(open(RL + '/text_spec_r11.json'))['texts']}
spec12 = {t[0]: t for t in json.load(open(RL + '/text_spec_r12.json'))['texts']}
masks = {a: asset_mask(f2, name2id, assets, a) for a in assets}
masks['water_tiber'], masks['water_sea'] = water_masks(f2, name2id)
D = {a: dist(m) for a, m in masks.items() if m.any()}
NAMED = [a for a in assets if not (a.startswith('fields_') or a.startswith('tree') or a.startswith('road_core') or a.startswith('shape_')
                                   or a in ('ground_land', 'header_gate', 'road_ostiensis'))]


def state(poster_p, spec):
    po, mo, paper, ink, txt = load_maps(poster_p)
    ink_all, ink_obj, ink_sh = map_ink_obj(f2, name2id, mo, paper)
    G = {k: glyph_pts(txt, t[1], 1.0) for k, t in spec.items()}
    return dict(po=po, mo=mo, ink=ink, D_ink=dist(ink_all), D_px=dist(ink), G=G, txt=txt)


def text_D(S, skip):
    m = np.zeros_like(S['ink'])
    for k, g in S['G'].items():
        if k in skip or len(g) == 0: continue
        m[g[:, 1], g[:, 0]] = True
    return dist(m)


def label_report(S, tid, own, skip=()):
    g = S['G'][tid]
    Dt = text_D(S, set(skip) | {tid})
    r = {'glyph_px': int(len(g)), 'ink_bbox_pt': ink_bbox_pt(g),
         'gap_map_ink_pt': round(min_d(S['D_ink'], g), 2), 'gap_map_ink_px_rule_pt': round(min_d(S['D_px'], g), 2),
         'gap_other_text_pt': round(min_d(Dt, g), 2), 'd_own_pt': round(min_d(D[own], g), 2)}
    oth = sorted(((round(min_d(D[a], g), 2), a) for a in NAMED if a != own and a in D))
    r['d_other_pt'], r['nearest_other'] = oth[0]
    r['ratio_other_over_own'] = round(r['d_other_pt'] / max(r['d_own_pt'], 0.01), 2)
    r['milestone_1_to_2_pt'] = round(min_d(D['milestone_1_to_2'], g), 2)
    # d_rev: own asset -> nearest OTHER label vs own asset -> this label
    rev = sorted((round(min_d(D[own], gg), 2), k) for k, gg in S['G'].items() if k != tid and len(gg) and k not in skip)
    r['d_rev_pt'], r['d_rev_label'] = rev[0]
    r['ratio_rev_over_own'] = round(r['d_rev_pt'] / max(r['d_own_pt'], 0.01), 2)
    return r


B = state(RL + '/r11/poster_2x.png', spec11)
A = state(after_p, spec12)
res = {'after_export': after_p, 'map': RL + '/r11/map_only_2x.png (v8_14)', 'labels': {}}
for tid, own, skip in (('790:103', 'landmark_apennines', ()), ('797:80', 'water_tiber', ()), ('797:79', 'landmark_pantheon', ()),
                       ('790:192', 'support_core5_lab', ('790:193',)), ('790:193', 'support_core5_lab', ('790:192',))):
    res['labels'][tid] = {'text': spec12[tid][4][0][0] + (spec12[tid][4][1][0] if len(spec12[tid][4]) > 1 else ''),
                          'box_r11': spec11[tid][1], 'box_r12': spec12[tid][1],
                          'before': label_report(B, tid, own, skip), 'after': label_report(A, tid, own, skip)}
# Pantheon: its own label 797:79 vs the Apennines label 790:103 (OBJ_PLACE-13 d_rev for the Pantheon)
for nm, S in (('before', B), ('after', A)):
    res.setdefault('pantheon_check', {})[nm] = {'pantheon_to_797_79_pt': round(min_d(D['landmark_pantheon'], S['G']['797:79']), 2),
                                                'pantheon_to_790_103_pt': round(min_d(D['landmark_pantheon'], S['G']['790:103']), 2)}
    pc = res['pantheon_check'][nm]; pc['ratio'] = round(pc['pantheon_to_790_103_pt'] / pc['pantheon_to_797_79_pt'], 2)
# every text: glyph gap to map ink and to other text, before/after (any unmoved label that changed is a regression)
allk = []
for k in spec12:
    if not len(A['G'][k]): continue
    a_ink, b_ink = min_d(A['D_ink'], A['G'][k]), min_d(B['D_ink'], B['G'][k])
    allk.append((k, round(b_ink, 2), round(a_ink, 2)))
res['all_texts_ink_gap_changed'] = [x for x in allk if abs(x[1] - x[2]) > 0.01]
# glyph overlap between any two text boxes in the after export (glyph pixels claimed by two boxes' masks with pad 0)
own_mask = {}
for k, t in spec12.items():
    g = glyph_pts(A['txt'], t[1], 0.0)
    own_mask[k] = set(map(tuple, g.tolist()))
pairs = []
ks = list(own_mask)
for i in range(len(ks)):
    for j in range(i + 1, len(ks)):
        if own_mask[ks[i]] & own_mask[ks[j]]: pairs.append([ks[i], ks[j], len(own_mask[ks[i]] & own_mask[ks[j]])])
res['text_box_glyph_sharing_after'] = pairs
# crops 3x: before (r11 poster) / after (export), same window = union of both boxes + 30pt
Pb = Image.open(RL + '/r11/poster_2x.png').convert('RGB'); Pa = Image.open(after_p).convert('RGB')
crops = {}
for name, ids in (('790_103_apennines', ['790:103', '797:79']), ('797_80_tiber', ['797:80']), ('790_191_core5_lab_title', ['790:192', '790:193'])):
    bx = [spec11[i][1] for i in ids] + [spec12[i][1] for i in ids]
    x0 = max(0, min(b[0] for b in bx) - 30); y0 = max(0, min(b[1] for b in bx) - 30)
    x1 = min(1191, max(b[0] + b[2] for b in bx) + 30); y1 = min(1684, max(b[1] + b[3] for b in bx) + 30)
    if name.startswith('790_191'): y1 = min(1684, y1 + 60)       # include the specimens
    for tag, P in (('before', Pb), ('after', Pa)):
        c = P.crop((int(x0 * 2), int(y0 * 2), int(x1 * 2), int(y1 * 2))).resize((int((x1 - x0) * 3), int((y1 - y0) * 3)), Image.Resampling.LANCZOS)
        p = f'{WF}/crops/{name}_{tag}_3x.png'; c.save(p); crops.setdefault(name, {})[tag] = p
    crops[name]['window_pt'] = [x0, y0, x1, y1]
res['crops'] = crops
json.dump(res, open(out_p, 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in res.items() if k != 'crops'}, ensure_ascii=False, indent=1))
