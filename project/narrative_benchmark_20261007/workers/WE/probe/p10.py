import bpy, sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from welib import *
S = Screen(); L = Land()
np.set_printoptions(suppress=True, precision=3, linewidth=220)
o = bpy.data.objects['F_centuriatio']; me = o.data
W, lab, flab, ls, lt, lv = face_islands(o)
n = lab.max() + 1
nf = np.bincount(flab, minlength=n)
role = np.zeros(len(me.polygons), np.int32); me.attributes['rc_v12_13_field_role'].data.foreach_get('value', role)
P = S.project(W)
isl_role = np.array([np.bincount(role[flab == k]).argmax() for k in range(n)])
kind = np.where(isl_role == 13, 'straw', np.where(isl_role == 12, 'vine', 'plate'))
print('kinds', {k: int((kind == k).sum()) for k in ('straw', 'vine', 'plate')})
def info(k):
    m = lab == k
    return dict(k=int(k), kind=str(kind[k]), nf=int(nf[k]), nv=int(m.sum()), role=int(isl_role[k]), pt=[round(P[m, 0].min(), 1), round(P[m, 0].max(), 1), round(P[m, 1].min(), 1), round(P[m, 1].max(), 1)],
                wmin=W[m].min(0).round(3).tolist(), wmax=W[m].max(0).round(3).tolist())
def find(box, kinds=('plate',)):
    x0, x1, y0, y1 = box
    out = []
    for k in range(n):
        if kind[k] not in kinds: continue
        m = lab == k
        cx, cy = P[m].mean(0)
        if x0 <= cx <= x1 and y0 <= cy <= y1: out.append(info(k))
    return out
print('fields_w plate', find((24, 90, 893, 932)))
print('fields_sw bank', find((180, 225, 1062, 1112), ('plate', 'straw')))
print('fields_sw vine plate', find((35, 110, 1238, 1290)))
print('fields_nw river', find((250, 300, 600, 650)))
print('fields_e SE', find((1015, 1142, 498, 566)))
print('fields_e OP18', find((840, 920, 798, 892)))
# straw geometry sample
k = np.nonzero(kind == 'straw')[0][0]
m = np.nonzero(lab == k)[0]
print('straw verts', W[m].round(3))
for f in np.nonzero(flab == k)[0][:18]:
    print(' f', lv[ls[f]:ls[f] + lt[f]].tolist())
hs = np.array([np.ptp(W[lab == k, 2]) for k in np.nonzero(kind == 'straw')[0]])
print('straw heights', np.percentile(hs, [0, 10, 50, 90, 100]).round(3), (hs < 0.49).sum())
# plate sample verts (fields_w)
