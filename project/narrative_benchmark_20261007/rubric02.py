import numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
P=np.asarray(Image.open(R+'r10/poster_2x.png').convert('RGB')).astype(np.float32)
X0,Y0,X1,Y1=250*2,460*2,420*2,560*2
w=P[Y0:Y1,X0:X1]
L=0.299*w[...,0]+0.587*w[...,1]+0.114*w[...,2]
gx=np.zeros_like(L);gy=np.zeros_like(L)
gx[:,1:-1]=(L[:,2:]-L[:,:-2])/2; gy[1:-1,:]=(L[2:,:]-L[:-2,:])/2
G=np.hypot(gx,gy)
box=np.zeros(L.shape,bool); box[496*2-Y0:507*2-Y0, 298*2-X0:382*2-X0]=True
inkm=(L<140)&box
dil=ndi.binary_dilation(inkm,iterations=4)
# paper: 30px ring around label box, bright 60%
ring=np.zeros_like(box); ring[496*2-Y0-30:507*2-Y0+30,298*2-X0-30:382*2-X0+30]=True; ring&=~box
px=w[ring]; Lp=0.299*px[:,0]+0.587*px[:,1]+0.114*px[:,2]
paper=np.median(px[Lp>=np.percentile(Lp,40)],0)
dist=np.sqrt(((w-paper)**2).sum(2))
obj=((G>12)|(dist>28))&~dil
dt,ind=ndi.distance_transform_edt(~obj,return_indices=True)
d=dt[inkm]; k=np.argmin(d); p=np.argwhere(inkm)[k]
q=(ind[0][tuple(p)],ind[1][tuple(p)])
print('paper',paper.round(),'min ink->object %.1f pt'%(d.min()/2),'ink',((p[1]+X0)/2,(p[0]+Y0)/2),'obj',((q[1]+X0)/2,(q[0]+Y0)/2),'col',w[q].round())
ys,xs=np.nonzero(inkm); print('ink bbox',(xs.min()+X0)/2,(ys.min()+Y0)/2,(xs.max()+X0+1)/2,(ys.max()+Y0+1)/2)
