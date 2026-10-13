import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
ink=np.load('ink.npy'); g=np.load('grad.npy').astype(np.float32)
X0,Y0,X1,Y1=1700,1000,2382,1560
obj=g[Y0:Y1,X0:X1]>12
src=np.zeros_like(obj); src[1234-Y0:1300-Y0,1963-X0:2326-X0]=ink[1234:1300,1963:2326]
dt=ndi.distance_transform_edt(~src)
lab,n=ndi.label(ndi.binary_dilation(obj,iterations=3))
for i in range(1,n+1):
    mm=(lab==i)&obj
    if mm.sum()<25: continue
    d=dt[mm]; k=np.argmin(d); p=np.argwhere(mm)[k]
    if d.min()/2<70: print('d=%.1f nearest px pt (%.1f,%.1f)'%(d.min()/2,(p[1]+X0)/2,(p[0]+Y0)/2))
