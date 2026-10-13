import numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
ink=np.load('ink.npy'); g=np.load('grad.npy').astype(np.float32)
M=np.asarray(Image.open(R+'r10/map_only_2x.png').convert('RGB')).astype(np.int16)
x0,y0,x1,y1=270*2,480*2,400*2,515*2
paper=np.array([240,228,206])
win=M[y0:y1,x0:x1]; dist=np.sqrt(((win-paper)**2).sum(2))
obj=(g[y0:y1,x0:x1]>12)|(dist>28)
# label ink only within label box
inkw=np.zeros_like(obj); inkw[(496-2)*2-y0:(507+2)*2-y0,(298-2)*2-x0:(382+2)*2-x0]=ink[(496-2)*2:(507+2)*2,(298-2)*2:(382+2)*2]
dt,ind=ndi.distance_transform_edt(~obj,return_indices=True)
d=dt[inkw]; k=np.argmin(d); p=np.argwhere(inkw)[k]
q=(ind[0][tuple(p)],ind[1][tuple(p)])
print('min dist pt',d.min()/2,'ink px pt',(p[1]+x0)/2,(p[0]+y0)/2,'obj px pt',(q[1]+x0)/2,(q[0]+y0)/2,'col',win[q])
# list distances by object cluster
lab,n=ndi.label(obj)
for i in range(1,n+1):
    m=lab==i
    if m.sum()<20: continue
    dd=ndi.distance_transform_edt(~m)[inkw].min()/2
    ys,xs=np.nonzero(m)
    if dd<15: print('cluster',i,'size',m.sum(),'bbox pt',(xs.min()+x0)/2,(ys.min()+y0)/2,(xs.max()+x0)/2,(ys.max()+y0)/2,'dist',dd)
# label ink bbox
ys,xs=np.nonzero(inkw); print('ink bbox', (xs.min()+x0)/2,(ys.min()+y0)/2,(xs.max()+x0)/2,(ys.max()+y0)/2)
