"""WF label search on r11 (v8_14) pixels.
Run: uv run -q --no-project --with pillow --with numpy --with scipy python -I wf_search.py <WF dir> <out.json> [poster_2x] [map_2x]
For each label: evaluate shifts on a 0.5pt grid and keep the smallest move that meets
  glyph gap to map ink >= INK (6pt target, 4pt hard), glyph gap to other text >= 6, d_own <= 20 (OBJ_INFO-25 / OBJ_PLACE-13),
  d_other / d_own >= 2 (rubric 1.5, margin), and for 790:103 the Pantheon check d(Pantheon, 790:103) >= 2 x d(Pantheon, 797:79).
Also reports current-state numbers for the CORE blocks (① ④ ⑤) and the ⑤ SUPPORT title."""
import sys, json
sys.path.insert(0, sys.argv[1])
from wf_common import *

out_p = sys.argv[2]
poster_p = sys.argv[3] if len(sys.argv) > 3 else RL + '/r11/poster_2x.png'
map_p = sys.argv[4] if len(sys.argv) > 4 else RL + '/r11/map_only_2x.png'
inv, objs, name2id, final, pxpt, f2, assets = load_ids()
po, mo, paper, ink, txt = load_maps(poster_p, map_p)
spec = {t[0]: t for t in json.load(open(RL + '/text_spec_r11.json'))['texts']}

NAMED = [a for a in assets if not (a.startswith('fields_') or a.startswith('tree') or a.startswith('road_core') or a.startswith('shape_')
                                   or a in ('ground_land', 'header_gate', 'road_ostiensis'))]
MILESTONES = ['milestone_1_to_2', 'milestone_2_to_34', 'milestone_34_to_5']
masks = {a: asset_mask(f2, name2id, assets, a) for a in assets}
masks['water_tiber'], masks['water_sea'] = water_masks(f2, name2id)
D = {a: dist(m) for a, m in masks.items() if m.any()}
ink_all, ink_obj, ink_shadow = map_ink_obj(f2, name2id, mo, paper)
D_ink = dist(ink_all)            # objects + cast shadows (search rule)
D_ink_px = dist(ink)             # old pixel rule (RGB distance to paper > 20, includes lit slopes) - reported only

# glyphs per text id (pad 2pt; overlapping pads resolved by nearest box later is unnecessary here)
G = {tid: glyph_pts(txt, t[1], pad=1.0) for tid, t in spec.items()}


def other_text_D(skip):
    m = np.zeros_like(txt)
    for tid, g in G.items():
        if tid in skip or len(g) == 0: continue
        m[g[:, 1], g[:, 0]] = True
    return dist(m)


def evaluate(tid, own, shift, D_txt, extra=None):
    g = G[tid]
    r = {'ink': round(min_d(D_ink, g, shift), 2), 'ink_px_rule': round(min_d(D_ink_px, g, shift), 2), 'text': round(min_d(D_txt, g, shift), 2),
         'd_own': round(min_d(D[own], g, shift), 2)}
    oth = sorted(((round(min_d(D[a], g, shift), 2), a) for a in NAMED if a != own and a in D), key=lambda x: x[0])
    r['d_other'], r['nearest_other'] = oth[0]
    r['others_top3'] = [[a, d] for d, a in oth[:3]]
    r['ratio_other_own'] = round(r['d_other'] / max(r['d_own'], 0.01), 2)
    r['milestones'] = {m: round(min_d(D[m], g, shift), 2) for m in MILESTONES}
    r['ink_bbox_pt'] = ink_bbox_pt(g, shift)
    if extra: r.update(extra(g, shift))
    return r


res = {'paper_rgb': paper.tolist(), 'named_assets': NAMED}

# ---------- d_rev helpers: distance from an asset to a label's glyphs
def asset_to_label(a, tid, shift=(0, 0)):
    return round(min_d(D[a], G[tid], shift), 2)


def search(tid, own, D_txt, rng, extra=None, accept=None, ink_min=6.0, text_min=6.0, dmax=20.0, ratio_min=2.0):
    cands = []
    xs = np.arange(rng[0], rng[1] + 0.01, 0.5); ys = np.arange(rng[2], rng[3] + 0.01, 0.5)
    g = G[tid]
    # vectorised prefilter on ink / text / own
    for dy in ys:
        for dx in xs:
            s = (dx, dy)
            a = min_d(D_ink, g, s)
            if a < ink_min: continue
            b = min_d(D[own], g, s)
            if b > dmax: continue
            c = min_d(D_txt, g, s)
            if c < text_min: continue
            cands.append((float(np.hypot(dx, dy)), dx, dy))
    cands.sort()
    good = []
    for _, dx, dy in cands:
        r = evaluate(tid, own, (dx, dy), D_txt, extra)
        if r['ratio_other_own'] < ratio_min: continue
        if accept and not accept(r): continue
        good.append({'shift': [float(dx), float(dy)], **r})
        if len(good) >= 12: break
    return good, len(cands)


# ================= 790:103 아펜니노 산맥 =================
D_txt103 = other_text_D({'790:103'})
pan_own_label = asset_to_label('landmark_pantheon', '797:79')


def extra103(g, s):
    return {'pantheon_to_this_label': round(min_d(D['landmark_pantheon'], g, s), 2),
            'pantheon_to_own_label_797_79': pan_own_label,
            'pantheon_rev_ratio': round(min_d(D['landmark_pantheon'], g, s) / pan_own_label, 2),
            'core1_marker': round(min_d(D['shape_core1_marker'], g, s), 2)}


res['790:103'] = {'box_r11': spec['790:103'][1], 'current': evaluate('790:103', 'landmark_apennines', (0, 0), D_txt103, extra103)}
good, n = search('790:103', 'landmark_apennines', D_txt103, (-40, 40, -45, 15), extra103,
                 accept=lambda r: r['pantheon_rev_ratio'] >= 2.0)
res['790:103']['n_prefilter'] = n
res['790:103']['candidates'] = good
for s in ([0, -18], [-2, -22], [-8, -12]):
    res['790:103'].setdefault('reviewer_suggestions', {})[str(s)] = evaluate('790:103', 'landmark_apennines', s, D_txt103, extra103)

# ================= 797:80 티베르강 =================
D_txt80 = other_text_D({'797:80'})
res['797:80'] = {'box_r11': spec['797:80'][1], 'current': evaluate('797:80', 'water_tiber', (0, 0), D_txt80)}
good, n = search('797:80', 'water_tiber', D_txt80, (-10, 60, -40, 40))
res['797:80']['n_prefilter'] = n
res['797:80']['candidates'] = good
for s in ([40, -4], [30, 0]):
    res['797:80'].setdefault('reviewer_suggestions', {})[str(s)] = evaluate('797:80', 'water_tiber', s, D_txt80)

# ================= 797:79 판테온 (current, for the d_rev check) =================
D_txt79 = other_text_D({'797:79'})
res['797:79'] = {'box_r11': spec['797:79'][1], 'current': evaluate('797:79', 'landmark_pantheon', (0, 0), D_txt79)}

# ================= ⑤ SUPPORT title 790:192 / 790:193 (frame 790:191) =================
D_txt191 = other_text_D({'790:192', '790:193'})
for s in ([0, 0], [0, 3], [0, 4]):
    r = {}
    for tid in ('790:192', '790:193'):
        r[tid] = evaluate(tid, 'support_core5_lab', s, D_txt191)
    res.setdefault('790:191', {})[str(s)] = r

# ================= CORE blocks: current numbers and minimal Figma-only moves =================
core = {'core1': (['790:146', '790:147', '790:148'], 'core1_modern_building'),
        'core4': (['790:164', '790:165', '790:166'], 'detail_core4_three_cubes'),
        'core5': (['790:170', '790:171', '790:172'], 'support_core5_lab')}
for k, (tids, own) in core.items():
    allg = np.vstack([G[t] for t in tids])
    G['_' + k] = allg
    D_txtk = other_text_D(set(tids))
    rr = {}
    for s in ([0, 0], [0, 1.5], [0, -1.5], [1.5, 0], [-1.5, 0], [0, 3], [0, 6], [12, 0], [0, -22]):
        rr[str(s)] = evaluate('_' + k, own, s, D_txtk)
        rr[str(s)]['marker_' + k] = round(min_d(D['shape_%s_marker' % k], allg, s), 2)
    res[k] = rr
# the ④ DETAIL heading + stage labels
for tid in ('790:183', '790:184', '790:186', '790:187', '790:188'):
    res.setdefault('core4_detail', {})[tid] = evaluate(tid, 'detail_core4_three_cubes', (0, 0), other_text_D({tid}))

json.dump(res, open(out_p, 'w'), ensure_ascii=False, indent=1)
print('ok', out_p)
