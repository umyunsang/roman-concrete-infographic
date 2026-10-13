import numpy as np, sys
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.cluster.vq import kmeans2
d = np.load(sys.argv[1]); fv = d['fv']; co = d['co']; cen = d['cen']; col = d['col']; area = d['area']
q = np.round(co / 1e-5).astype(np.int64); _, inv = np.unique(q, axis=0, return_inverse=True); inv = inv.ravel()
f = inv[fv]; m2 = inv.max() + 1
r = np.r_[f[:, 0], f[:, 1], f[:, 2]]; c = np.r_[f[:, 1], f[:, 2], f[:, 0]]
n, lv = connected_components(coo_matrix((np.ones(len(r)), (r, c)), shape=(m2, m2)), directed=False)
lf = lv[f[:, 0]]; u, cnt = np.unique(lf, return_counts=True); o = np.argsort(-cnt)
print('components', n)
for k in o[:25]:
    m = lf == u[k]; print(u[k], cnt[k], cen[m].min(0).round(3), cen[m].max(0).round(3), 'col', (np.average(col[m], axis=0, weights=area[m]) * 255).round())
C, lab = kmeans2(col.astype(np.float64), 6, seed=1, minit='++')
for k in range(6):
    m = lab == k; print('cluster', k, (C[k] * 255).round(), m.sum(), cen[m].min(0).round(2), cen[m].max(0).round(2))
np.save(sys.argv[2], lab); np.save(sys.argv[3], lf)
