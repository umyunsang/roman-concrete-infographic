import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
P=np.asarray(Image.open(R+'r10/poster_2x.png').convert('RGB')).astype(float)
M=np.asarray(Image.open(R+'r10/map_only_2x.png').convert('RGB')).astype(float)
def Y(rgb):
    c=rgb/255.0; l=np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4); return l@[0.2126,0.7152,0.0722]
YM=Y(M)
d=np.abs(P-M).sum(2)
spec=json.load(open(R+'text_spec_r10.json'))['texts']
for tid,box,rot,al,segs in spec:
    x,y,w,h=box
    X0,Y0=max(0,int((x-20)*2)),max(0,int((y-20)*2)); X1,Y1=int((x+w+20)*2),int((y+h+20)*2)
    ym=YM[Y0:Y1,X0:X1]; g=np.median(ym)
    # local smooth ground (remove soft shading): compare to 6pt median filter
    from scipy.ndimage import median_filter
    loc=median_filter(ym,size=25)
    obj=np.abs(ym-loc)>0.06
    lab,n=ndi.label(obj); sizes=ndi.sum(obj,lab,range(1,n+1))
    big=np.isin(lab,np.nonzero(sizes>=30)[0]+1)
    ink=d[Y0:Y1,X0:X1]>24
    bx=np.zeros_like(ink); bx[max(0,int((y-2)*2)-Y0):int((y+h+2)*2)-Y0,max(0,int((x-2)*2)-X0):int((x+w+2)*2)-X0]=True
    ink&=bx
    under=ink&big
    halo=ndi.binary_dilation(ink,iterations=2)&big
    if halo.sum()>0:
        yy,xx=np.nonzero(halo)
        txt=''.join(s[0] for s in segs).replace('\n','/')[:18]
        print(tid,txt,'under-stroke px',under.sum(),'halo px',halo.sum(),'frac %.4f'%(halo.sum()/max(1,ndi.binary_dilation(ink,iterations=2).sum())),'x %.1f-%.1f y %.1f-%.1f'%((X0+xx.min())/2,(X0+xx.max())/2,(Y0+yy.min())/2,(Y0+yy.max())/2))
