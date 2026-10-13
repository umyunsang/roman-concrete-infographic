"""ana.py <id.npz> - WB measurements from an idcrop pass (areas, overlaps, gaps in pt)."""
import sys, json
import numpy as np
from scipy import ndimage as ndi
d = np.load(sys.argv[1]); names = list(d['names']); mats = list(d['mats']); sp = float(d['sp'][0]); ox, oy = d['origin_px']
om, oo, mm, mo = d['obj_map'], d['obj_ovl'], d['mat_map'], d['mat_ovl']
final = np.where(oo > 0, oo, om)
px2 = 1.0 / sp ** 2
def ids(pred):
    return [i for i, n in enumerate(names) if n and pred(n)]
def mask(arr, pred):
    return np.isin(arr, ids(pred))
def bbox(m):
    ys, xs = np.nonzero(m)
    if len(xs) == 0: return None
    return [round((xs.min() + ox) / sp, 1), round((xs.max() + 1 + ox) / sp, 1), round((ys.min() + oy) / sp, 1), round((ys.max() + 1 + oy) / sp, 1)]
def gap(a, b):
    if not a.any() or not b.any(): return None
    if (a & b).any(): return -float((a & b).sum() * px2)   # negative = overlap area pt2
    dt = ndi.distance_transform_edt(~b)
    return round(float(dt[a].min()) / sp, 2)
G = {
 'C2': lambda n: n.startswith('C2_'),
 'C2_mesh': lambda n: n == 'C2_hot_mixing',
 'D2_heat': lambda n: n.startswith('D2_heat'),
 'C2_heat': lambda n: n.startswith('C2_heat'),
 'D2_cube': lambda n: n == 'D2_cube',
 'D2_lime': lambda n: n.startswith('D2_lime') and n != 'D2_lime_kiln',
 'D2_model': lambda n: n == 'D2_cube' or (n.startswith('D2_lime') and n != 'D2_lime_kiln'),
 'field': lambda n: n == 'F_centuriatio',
 'MS2': lambda n: n.startswith('MS2'),
 'lead': lambda n: n in ('S_lead02', 'S_lead_dot2'),
 'land': lambda n: n == 'T_land',
}
rep = {}
for k, p in G.items():
    m = mask(final, p); rep[k] = {'area_final_pt2': round(float(m.sum() * px2), 1), 'bbox': bbox(m)}
for k in ('D2_heat', 'C2_heat'):
    rep[k]['area_own_pt2'] = round(float(mask(oo, G[k]).sum() * px2), 1)
# map-level C2 own area and vis (fraction of own map pixels not covered by overlay)
c2own = mask(om, G['C2'])
rep['C2']['map_own_pt2'] = round(float(c2own.sum() * px2), 1)
rep['C2']['covered_by_overlay_pt2'] = round(float((c2own & (oo > 0)).sum() * px2), 1)
rep['C2']['covered_by_nonC2_overlay_pt2'] = round(float((c2own & (oo > 0) & ~mask(oo, G['C2'])).sum() * px2), 1)
pairs = [('D2_heat', 'C2'), ('D2_heat', 'field'), ('D2_heat', 'D2_cube'), ('D2_heat', 'D2_lime'), ('D2_heat', 'MS2'),
         ('C2_heat', 'C2_mesh'), ('C2', 'field'), ('C2', 'D2_model'), ('C2', 'MS2'), ('D2_model', 'field')]
for a, b in pairs:
    A = mask(oo, G[a]) if a.endswith('heat') else mask(final, G[a])
    B = mask(final, G[b]) if not a.endswith('heat') else mask(om, G[b])
    rep[f'gap {a}-{b}'] = gap(A, B)
# lime04 coverage by the leader dot
l4 = names.index('D2_lime04') if 'D2_lime04' in names else -1
dot = names.index('S_lead_dot2') if 'S_lead_dot2' in names else -1
if l4 > 0:
    vis4 = (om == l4); cov = vis4 & (oo == dot)
    rep['lime04_visible_pt2'] = round(float(vis4.sum() * px2), 2); rep['lime04_covered_by_dot_pct'] = round(100 * cov.sum() / max(1, vis4.sum()), 1)
# C2 material areas (map pass, visible in final)
c2m = {}
for i, n in enumerate(mats):
    if not n: continue
    m = c2own & (mm == i) & (oo == 0)
    if m.any(): c2m[n] = round(float(m.sum() * px2), 1)
rep['C2_material_area_pt2'] = c2m
print(json.dumps(rep, ensure_ascii=False, indent=1))
