import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
spec=json.load(open(R+'text_spec_r10.json'))['texts']
ink=np.load('ink.npy'); g=np.load('grad.npy').astype(np.float32)
for t in spec:
    if t[2]==0: continue
    x,y,w,h=t[1]
    x0,y0,x1,y1=[int(v*2) for v in (x-3,y-3,x+w+3,y+h+3)]
    m=60
    wx0,wy0,wx1,wy1=x0-m,y0-m,x1+m,y1+m
    gw=g[wy0:wy1,wx0:wx1]>12
    inkw=np.zeros_like(gw); inkw[y0-wy0:y1-wy0,x0-wx0:x1-wx0]=ink[y0:y1,x0:x1]
    # remove ink-adjacent gradient (map has no text, so fine)
    dt,ind=ndi.distance_transform_edt(~gw,return_indices=True)
    d=dt[inkw]; k=np.argmin(d); p=np.argwhere(inkw)[k]; q=(ind[0][tuple(p)],ind[1][tuple(p)])
    print(t[0], t[4][0][0], 'min gap pt %.1f'%(d.min()/2), 'at ink',( (p[1]+wx0)/2,(p[0]+wy0)/2),'obj',((q[1]+wx0)/2,(q[0]+wy0)/2))
