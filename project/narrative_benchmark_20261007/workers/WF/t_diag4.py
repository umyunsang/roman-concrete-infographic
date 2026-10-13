import sys, json; sys.path.insert(0, sys.argv[1])
from wf_common import *
from scipy.ndimage import distance_transform_edt
inv, objs, name2id, final, pxpt, f2, assets = load_ids()
po, mo, paper, ink, txt = load_maps(sys.argv[1] + '/poster_2x_after.png')
ink_all, ink_obj, ink_sh = map_ink_obj(f2, name2id, mo, paper)
o2a = {o: a for a, os_ in assets.items() for o in os_}
d, (iy, ix) = distance_transform_edt(~ink_all, return_indices=True)
spec = {t[0]: t for t in json.load(open(RL + '/text_spec_r12.json'))['texts']}
for tid in ('790:103', '797:80', '790:192', '790:193'):
    g = glyph_pts(txt, spec[tid][1], 1.0); dd = d[g[:, 1], g[:, 0]]; k = dd.argmin(); gx, gy = g[k]; nx, ny = ix[gy, gx], iy[gy, gx]
    oid = f2[ny, nx]; nm = objs[oid - 1] if oid else None
    print(tid, round(dd.min() / 2, 2), 'nearest ink at pt', (nx / 2, ny / 2), nm, o2a.get(nm), 'shadow' if ink_sh[ny, nx] else 'object')
