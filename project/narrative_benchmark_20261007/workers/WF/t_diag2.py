import sys, json; sys.path.insert(0, sys.argv[1])
from wf_common import *
inv, objs, name2id, final, pxpt, f2, assets = load_ids()
po, mo, paper, ink, txt = load_maps()
L = mo @ np.array([0.299, 0.587, 0.114]); pL = paper @ np.array([0.299, 0.587, 0.114])
gid = name2id['T_land']
ground = f2 == gid
print('paper L', pL)
for name, (x0, x1, y0, y1) in {'apennines_area': (330, 470, 370, 470), 'tiber_area': (100, 230, 410, 480), 'all_ground': (0, 1191, 0, 1684)}.items():
    sl = (slice(y0 * 2, y1 * 2), slice(x0 * 2, x1 * 2))
    gl = L[sl][ground[sl]] - pL
    print(name, 'ground px', gl.size, 'dL pcts', np.percentile(gl, [1, 5, 25, 50, 75, 95, 99]).round(1).tolist(), 'frac<-12', round((gl < -12).mean(), 4), 'frac<-20', round((gl < -20).mean(), 4))
