from PIL import Image
import numpy as np, json
im=np.asarray(Image.open('../nb_work/review_loop/r9/poster_2x.png').convert('RGB')).astype(float)
mo=np.asarray(Image.open('../nb_work/review_loop/r9/map_only_2x.png').convert('RGB')).astype(float)
L=0.2126*im[...,0]+0.7152*im[...,1]+0.0722*im[...,2]
Lm=0.2126*mo[...,0]+0.7152*mo[...,1]+0.0722*mo[...,2]
spec=json.load(open('../nb_work/review_loop/text_spec_r9.json'))['texts']
for t in spec:
    id,box,rot,al,segs=t
    if rot==0: continue
    x,y,w,h=box
    x0,y0,x1,y1=[int(round(v*2)) for v in (x,y,x+w,y+h)]
    d=L[y0:y1,x0:x1]-Lm[y0:y1,x0:x1]   # text-only difference (negative where ink)
    ink=d< -30
    # gradient orientation of text layer
    D=-d
    gy,gx=np.gradient(D)
    mag=np.hypot(gx,gy)
    ang=(np.degrees(np.arctan2(gy,gx))+180)%180  # edge normal orientation
    # stroke direction = normal+90
    sd=(ang+90)%180
    hist,edges=np.histogram(sd[mag>20],bins=36,range=(0,180),weights=mag[mag>20])
    top=np.argsort(hist)[::-1][:4]
    peaks=[(int(edges[i]+2.5),round(hist[i]/hist.sum(),3)) for i in top]
    # PCA of ink pixels to get baseline direction
    yy,xx=np.nonzero(ink)
    cx,cy=xx.mean(),yy.mean()
    C=np.cov(np.vstack([xx-cx,yy-cy]))
    ev,evec=np.linalg.eigh(C)
    v=evec[:,1]; base=np.degrees(np.arctan2(-v[1],v[0]))
    if base>90: base-=180
    if base<-90: base+=180
    print(id, segs[0][0], rot, 'inkpx',ink.sum(),'baseline(screen deg, ccw+)',round(base,1),'stroke-dir peaks (deg, image coords y-down)',peaks)
