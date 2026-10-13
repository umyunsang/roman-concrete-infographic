import sys, json; sys.path.insert(0, sys.argv[1])
from wf_common import *
from scipy.ndimage import distance_transform_edt
inv, objs, name2id, final, pxpt, f2, assets = load_ids()
po, mo, paper, ink, txt = load_maps()
obj2asset = {o: a for a, os_ in assets.items() for o in os_}
print('water_sea objs', assets['water_sea']); print('water_tiber objs', assets['water_tiber'])
spec = {t[0]: t for t in json.load(open(RL + '/text_spec_r11.json'))['texts']}
d, (iy, ix) = distance_transform_edt(~ink, return_indices=True)
for tid, sh in (('790:103', (0, 0)), ('797:80', (0, 0)), ('797:80', (40, -4)), ('797:80', (30, 0)), ('790:103', (0, -18))):
    g = glyph_pts(txt, spec[tid][1], 1.0) + np.round(np.array(sh) * 2).astype(int)
    dd = d[g[:, 1], g[:, 0]]; k = dd.argmin(); gx, gy = g[k]
    nx, ny = ix[gy, gx], iy[gy, gx]
    oid = f2[ny, nx]; nm = objs[oid - 1] if oid > 0 else None
    print(tid, sh, 'gap', round(dd.min() / 2, 2), 'glyph', (gx / 2, gy / 2), 'ink px', (nx / 2, ny / 2), 'rgb', mo[ny, nx].astype(int).tolist(), 'paper', paper.tolist(), 'id', nm, obj2asset.get(nm))
# water_sea pixels near the Tiber label region
m = asset_mask(f2, name2id, assets, 'water_sea'); ys, xs = np.nonzero(m[700:1000, 150:450]); 
if len(xs): print('water_sea px in 75..225 x 350..500 pt:', len(xs), 'bbox pt', (xs.min()+150)/2, (xs.max()+150)/2, (ys.min()+700)/2, (ys.max()+700)/2)
ids = np.unique(f2[700:1000, 150:450][m[700:1000, 150:450]]); print([objs[i-1] for i in ids])
