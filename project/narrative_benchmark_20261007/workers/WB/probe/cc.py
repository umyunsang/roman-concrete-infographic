import numpy as np, sys
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
d = np.load(sys.argv[1]); fv = d['fv']; co = d['co']; cen = d['cen']
nv = len(co)
r = np.r_[fv[:, 0], fv[:, 1], fv[:, 2]]; c = np.r_[fv[:, 1], fv[:, 2], fv[:, 0]]
A = coo_matrix((np.ones(len(r)), (r, c)), shape=(nv, nv))
n, lv = connected_components(A, directed=False)
lf = lv[fv[:, 0]]
u, cnt = np.unique(lf, return_counts=True)
o = np.argsort(-cnt)
print('components', n)
for k in o[:10]:
    m = lf == u[k]; print(u[k], cnt[k], cen[m].min(0).round(2), cen[m].max(0).round(2))
# merge duplicate vertices by position
q = np.round(co / 1e-5).astype(np.int64)
_, inv = np.unique(q, axis=0, return_inverse=True)
inv = inv.ravel()
fv2 = inv[fv]
r = np.r_[fv2[:, 0], fv2[:, 1], fv2[:, 2]]; c = np.r_[fv2[:, 1], fv2[:, 2], fv2[:, 0]]
m2 = inv.max() + 1
A = coo_matrix((np.ones(len(r)), (r, c)), shape=(m2, m2)); n, lv = connected_components(A, directed=False)
lf = lv[fv2[:, 0]]; u, cnt = np.unique(lf, return_counts=True); o = np.argsort(-cnt)
print('after weld components', n)
for k in o[:10]:
    m = lf == u[k]; print(u[k], cnt[k], cen[m].min(0).round(2), cen[m].max(0).round(2))
