import numpy as np, sys
from scipy.cluster.vq import kmeans2
d = np.load(sys.argv[1]); col = d['col']; cen = d['cen']; area = d['area']
np.random.seed(0)
C, lab = kmeans2(col.astype(np.float64), 6, seed=1, minit='++')
for k in range(6):
    m = lab == k
    print(k, (C[k] * 255).round(), 'faces', m.sum(), 'area', area[m].sum().round(4), 'z range', cen[m, 2].min().round(2), cen[m, 2].max().round(2))
np.save(sys.argv[2], lab)
