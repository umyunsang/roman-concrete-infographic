"""classes: 0 skin, 1 tunic, 2 cloth (belt, sandals), 3 hair, 4 hoe"""
import numpy as np, sys
from scipy.sparse import coo_matrix
d = np.load(sys.argv[1]); lab = np.load(sys.argv[2]); comp = np.load(sys.argv[3]); cen = d['cen']; fv = d['fv']; co = d['co']
z = cen[:, 2]
Z_NECK, Z_HEM, Z_ANKLE = 0.36, -0.16, -0.40
cream = np.isin(lab, [0, 3]); dark = lab == 1
cls = np.zeros(len(cen), np.int8)
body = np.isin(comp, [2, 9, 10, 11, 12])
cls[body & cream & (z > Z_HEM - 0.02) & (z < Z_NECK)] = 1
cls[body & dark & (z > Z_NECK)] = 3
cls[body & dark & (z < Z_ANKLE)] = 2
cls[comp == 4] = 1
cls[comp == 6] = 3
cls[np.isin(comp, [7, 8])] = 2
small_feet = np.isin(comp, [1, 3, 5, 13, 14, 15, 16])
cls[small_feet] = 2
cls[comp == 0] = 4
# smoothing inside the body component only
q = np.round(co / 1e-5).astype(np.int64); _, inv = np.unique(q, axis=0, return_inverse=True); inv = inv.ravel()
f = inv[fv]; nv = inv.max() + 1; nf = len(f)
VF = coo_matrix((np.ones(nf * 3), (f.ravel(), np.repeat(np.arange(nf), 3))), shape=(nv, nf)).tocsr()
for it in range(2):
    oh = np.zeros((nf, 5)); oh[np.arange(nf), cls] = 1
    fc = (VF @ oh)[f].sum(1); new = fc.argmax(1).astype(np.int8)
    flip = body & (fc.max(1) >= 0.6 * fc.sum(1))
    cls = np.where(flip, new, cls)
np.save(sys.argv[4], cls)
for k, n in enumerate(['skin', 'tunic', 'cloth', 'hair', 'hoe']):
    m = cls == k; print(n, m.sum(), cen[m].min(0).round(2), cen[m].max(0).round(2))
