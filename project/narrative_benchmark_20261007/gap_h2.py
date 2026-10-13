from PIL import Image
import numpy as np, json
from scipy import ndimage as ndi
im=np.asarray(Image.open('../nb_work/review_loop/r9/poster_2x.png').convert('RGB')).astype(float)
mo=np.asarray(Image.open('../nb_work/review_loop/r9/map_only_2x.png').convert('RGB')).astype(float)
def lum(a): return 0.2126*a[...,0]+0.7152*a[...,1]+0.0722*a[...,2]
L=lum(im); Lm=lum(mo)
# paper estimate: median at quarter res
small=Lm[::4,::4]
med=ndi.median_filter(small,size=15)
paper=np.kron(med,np.ones((4,4)))[:Lm.shape[0],:Lm.shape[1]]
smallc=mo[::4,::4]
medc=np.stack([np.kron(ndi.median_filter(smallc[...,k],size=15),np.ones((4,4)))[:Lm.shape[0],:Lm.shape[1]] for k in range(3)],-1)
dev=np.abs(Lm-paper); cdev=np.abs(mo-medc).max(-1)
obj=(dev>15)|(cdev>20)
obj=ndi.binary_opening(obj,iterations=1)
np.save('obj.npy',obj)
spec=json.load(open('../nb_work/review_loop/text_spec_r9.json'))['texts']
res=[]
for t in spec:
    id,box,rot,al,segs=t
    x,y,w,h=box
    pad=30
    X0,Y0=max(0,int(x*2)-pad),max(0,int(y*2)-pad)
    X1,Y1=min(2382,int((x+w)*2)+pad),min(3368,int((y+h)*2)+pad)
    d=L[Y0:Y1,X0:X1]-Lm[Y0:Y1,X0:X1]
    own=np.zeros_like(d,bool)
    own[max(0,int(y*2)-Y0-4):int((y+h)*2)-Y0+4, max(0,int(x*2)-X0-4):int((x+w)*2)-X0+4]=True
    ink=(np.abs(d)>20)&own
    if not ink.any(): continue
    o=obj[Y0:Y1,X0:X1]
    dist=ndi.distance_transform_edt(~o)
    mind=dist[ink].min()/2
    iy,ix=np.unravel_index(np.argmin(np.where(ink,dist,1e9)),dist.shape)
    res.append((round(mind,2),id,segs[-1][0].replace('\n','/')[:20],'at',( (ix+X0)/2,(iy+Y0)/2)))
for r in sorted(res)[:40]: print(r)
