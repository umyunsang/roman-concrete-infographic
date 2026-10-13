from PIL import Image
import numpy as np, json
from scipy import ndimage as ndi
im=np.asarray(Image.open('../nb_work/review_loop/r9/poster_2x.png').convert('RGB')).astype(float)
mo=np.asarray(Image.open('../nb_work/review_loop/r9/map_only_2x.png').convert('RGB')).astype(float)
def lum(a): return 0.2126*a[...,0]+0.7152*a[...,1]+0.0722*a[...,2]
L=lum(im); Lm=lum(mo)
spec=json.load(open('../nb_work/review_loop/text_spec_r9.json'))['texts']
res=[]
for t in spec:
    id,box,rot,al,segs=t
    if rot!=0: continue
    x,y,w,h=box
    pad=30
    X0,Y0=max(0,int(x*2)-pad),max(0,int(y*2)-pad)
    X1,Y1=min(2382,int((x+w)*2)+pad),min(3368,int((y+h)*2)+pad)
    d=L[Y0:Y1,X0:X1]-Lm[Y0:Y1,X0:X1]
    # restrict ink to the text's own box (+2px) to avoid neighbours
    own=np.zeros_like(d,bool)
    bx0,by0=int(x*2)-X0-4,int(y*2)-Y0-4
    own[max(0,by0):int((y+h)*2)-Y0+4, max(0,bx0):int((x+w)*2)-X0+4]=True
    ink=(np.abs(d)>20)&own
    if not ink.any(): continue
    reg=Lm[Y0:Y1,X0:X1]; regc=mo[Y0:Y1,X0:X1]
    paper=ndi.median_filter(reg,size=61)
    paperc=np.stack([ndi.median_filter(regc[...,k],size=61) for k in range(3)],-1)
    dev=np.abs(reg-paper); cdev=np.abs(regc-paperc).max(-1)
    obj=(dev>15)|(cdev>20)
    obj=ndi.binary_opening(obj,iterations=1)
    dist=ndi.distance_transform_edt(~obj)
    mind=dist[ink].min()/2
    # where is the nearest object pixel
    res.append((round(mind,2),id,segs[-1][0].replace('\n','/')[:20]))
for r in sorted(res)[:30]: print(r)
