"""classify.py faces.npz lab6.npy out_cls.npy [jar ellipsoid cx cy cz ax ay az] - per-face part classes for the Meshy pourer.
classes: 0 skin, 1 tunic, 2 cloth (belt, sandals), 3 hair, 4 jar"""
import numpy as np, sys, json
from scipy.sparse import coo_matrix
d = np.load(sys.argv[1]); lab = np.load(sys.argv[2]); cen = d['cen']; fv = d['fv']; co = d['co']; area = d['area']
P = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
jc = np.array(P.get('jar_c', [-0.11, -0.25, 0.21])); ja = np.array(P.get('jar_a', [0.15, 0.23, 0.17]))
Z_NECK = P.get('z_neck', 0.62); Z_HEM = P.get('z_hem', -0.42); Z_ANKLE = P.get('z_ankle', -0.80)
orange = np.isin(lab, [0, 4]); cream = np.isin(lab, [2]); tan = lab == 3; dark = np.isin(lab, [1, 5])
inj = (((cen - jc) / ja) ** 2).sum(1) <= 1.0
cls = np.zeros(len(cen), np.int8)                        # skin by default
cls[(cream | tan) & (cen[:, 2] < Z_NECK) & (cen[:, 2] > Z_HEM - 0.04) & ~inj] = 1
cls[dark & (cen[:, 2] > Z_NECK - 0.02)] = 3
cls[dark & (cen[:, 2] < Z_ANKLE)] = 2
cls[dark & (cen[:, 2] > Z_HEM) & (cen[:, 2] < 0.3) & ~inj] = 2
cls[inj] = 4
# majority smoothing over vertex-sharing neighbours (welded), 3 passes, within body zones
q = np.round(co / 1e-5).astype(np.int64); _, inv = np.unique(q, axis=0, return_inverse=True); inv = inv.ravel()
f = inv[fv]; nv = inv.max() + 1; nf = len(f)
rows = np.repeat(np.arange(nf), 3); cols = f.ravel()
VF = coo_matrix((np.ones(len(rows)), (cols, rows)), shape=(nv, nf)).tocsr()
for it in range(3):
    onehot = np.zeros((nf, 5)); onehot[np.arange(nf), cls] = area[:, None][:, 0] if False else 1
    vcount = VF @ onehot                                # per vertex class counts
    fcount = vcount[f].sum(1)                           # per face neighbourhood counts
    new = fcount.argmax(1).astype(np.int8)
    keep = fcount.max(1) < 0.6 * fcount.sum(1)          # only flip when a clear majority
    cls = np.where(keep, cls, new)
np.save(sys.argv[3], cls)
for k, n in enumerate(['skin', 'tunic', 'cloth', 'hair', 'jar']):
    m = cls == k; print(n, m.sum(), round(float(area[m].sum()), 4), cen[m].min(0).round(2) if m.any() else '', cen[m].max(0).round(2) if m.any() else '')
