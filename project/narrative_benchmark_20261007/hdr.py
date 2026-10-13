import numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
ink=np.load('ink.npy'); g=np.load('grad.npy').astype(np.float32)
obj=(g>12)|ink
H=int(330*2)
sub=obj[:H]
lab,n=ndi.label(ndi.binary_dilation(sub,iterations=3))
comps=[]
for i in range(1,n+1):
    m=(lab==i)&sub
    if m.sum()<40: continue
    ys,xs=np.nonzero(m)
    comps.append((ys.min()/2,ys.max()/2,xs.min()/2,xs.max()/2,int(m.sum())))
comps.sort()
for c in comps: print('y %.1f-%.1f x %.1f-%.1f n=%d'%c)
