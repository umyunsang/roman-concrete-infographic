import numpy as np
from PIL import Image
from scipy import ndimage
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
P=np.array(Image.open(R+'r11/poster_2x.png').convert('RGB')).astype(int)
M=np.array(Image.open(R+'r11/map_only_2x.png').convert('RGB')).astype(int)
diff=np.abs(P-M).sum(-1)
text=diff>60
# shape mask from map_only: badge color reddish
def lab(rgb):
    c=rgb/255.0; lin=np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4)
    Mx=np.array([[0.4124,0.3576,0.1805],[0.2126,0.7152,0.0722],[0.0193,0.1192,0.9505]])
    XYZ=lin@Mx.T; n=np.array([0.95047,1,1.08883]); t=XYZ/n
    f=np.where(t>0.008856,np.cbrt(t),7.787*t+16/116)
    return np.stack([116*f[...,1]-16,500*(f[...,0]-f[...,1]),200*(f[...,1]-f[...,2])],-1)
boxes={'core1':[528,639,385,435],'core2':[57,134,747,797],'core3':[408,542,1031,1081],'core4':[638,751,1031,1081],'core5':[982,1153,816,866]}
for k,(x0,x1,y0,y1) in boxes.items():
    X0,X1,Y0,Y1=[int(v*2) for v in (x0-8,x1+8,y0-8,y1+8)]
    sub=M[Y0:Y1,X0:X1]; L=lab(sub)
    red=(L[...,1]>25)&(L[...,0]<55)
    t=text[Y0:Y1,X0:X1]
    # exclude digit inside badge: digit is light text over badge => counts as overlap by design; separate badge disc (largest comp) vs underline
    lb,n=ndimage.label(red)
    sizes=ndimage.sum(red,lb,range(1,n+1))
    order=np.argsort(sizes)[::-1]
    res=[]
    for j in order[:2]:
        comp=lb==(j+1)
        ys,xs=np.nonzero(comp)
        bb=[round(xs.min()/2+x0-8,1),round(xs.max()/2+x0-8,1),round(ys.min()/2+y0-8,1),round(ys.max()/2+y0-8,1)]
        dil=ndimage.binary_dilation(comp,iterations=0) if False else comp
        ov=(t&comp).sum()
        # nearest text distance (exclude text within badge disc bbox for disc)
        tt=t.copy()
        if (bb[1]-bb[0])<30: # disc: remove digit pixels inside disc bbox
            tt[ys.min():ys.max()+1, xs.min():xs.max()+1]=False
        dt=ndimage.distance_transform_edt(~tt)
        res.append((bb, int(ov), round(float(dt[comp].min())/2,2)))
    # mean color of disc
    print(k, res)
    j=order[0]; comp=lb==(j+1); er=ndimage.binary_erosion(comp,iterations=3)
    rgb=np.median(sub[er],axis=0); print('   disc median rgb', rgb, '#%02X%02X%02X'%tuple(int(v) for v in rgb))
