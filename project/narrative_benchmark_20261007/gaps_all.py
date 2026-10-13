import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
P=np.asarray(Image.open(R+'r10/poster_2x.png').convert('L')).astype(float)
M=np.asarray(Image.open(R+'r10/map_only_2x.png').convert('L')).astype(float)
spec=json.load(open(R+'text_spec_r10.json'))['texts']
for tid,box,rot,al,segs in spec:
    x,y,w,h=box
    X0,Y0=max(0,int((x-25)*2)),max(0,int((y-25)*2)); X1,Y1=min(2382,int((x+w+25)*2)),min(3368,int((y+h+25)*2))
    p=P[Y0:Y1,X0:X1]; m=M[Y0:Y1,X0:X1]
    ink=np.abs(p-m)>12
    bx=np.zeros_like(ink); bx[max(0,int((y-2)*2)-Y0):int((y+h+2)*2)-Y0,max(0,int((x-2)*2)-X0):int((x+w+2)*2)-X0]=True; ink&=bx
    # local paper level: median of map in window excluding very dark
    paper=np.percentile(m,70)
    obj=ndi.binary_opening(m<paper-22,iterations=1)
    # exclude objects that the text sits on entirely (discs, sea): if >50% of ink is on obj, skip
    if obj[ink].mean()>0.5: 
        continue
    dt=ndi.distance_transform_edt(~obj)/2
    g=dt[ink].min()
    if g<3:
        yy,xx=np.nonzero(ink); i=np.argmin(dt[ink])
        txt=''.join(s[0] for s in segs).replace('\n','/')[:16]
        print(tid,txt,'min gap %.2f pt at (%.1f,%.1f)'%(g,(X0+xx[i])/2,(Y0+yy[i])/2))
