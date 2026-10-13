import sys; sys.path.insert(0, sys.argv[1])
from wf_common import *
inv, objs, name2id, final, pxpt, f2, assets = load_ids()
print(len(objs), final.shape, final.max())
for o in inv['objects']:
    if o['name'] in ('R8_pantheon', 'L02_tiber', 'L01_gennaro', 'NB_modern_building', 'B_pons1'):
        i = name2id[o['name']]; ys, xs = np.nonzero(final == i)
        print(o['name'], o['bbox_visible_final_pt'], [round(xs.min()/pxpt, 1), round((xs.max()+1)/pxpt, 1), round(ys.min()/pxpt, 1), round((ys.max()+1)/pxpt, 1)])
