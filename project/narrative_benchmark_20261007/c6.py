import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
P=np.asarray(Image.open(R+'r10/poster_2x.png').convert('RGB')).astype(np.float64)
M=np.asarray(Image.open(R+'r10/map_only_2x.png').convert('RGB')).astype(np.float64)
d=np.abs(P-M).sum(2)
def lin(c):
    c=np.asarray(c)/255.0
    return np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4)
def Ylum(rgb):
    l=lin(rgb); return l[...,0]*0.2126+l[...,1]*0.7152+l[...,2]*0.0722
YM=Ylum(M)
spec=json.load(open(R+'text_spec_r10.json'))['texts']
for tid,box,rot,al,segs in spec:
    x,y,w,h=box
    x0,y0=max(0,int((x-2)*2)),max(0,int((y-2)*2)); x1,y1=int((x+w+2)*2)+1,int((y+h+2)*2)+1
    mask=d[y0:y1,x0:x1]>24
    halo=ndi.binary_dilation(mask,iterations=2)
    wx0,wy0=max(0,int((x-20)*2)),max(0,int((y-20)*2)); wx1,wy1=int((x+w+20)*2),int((y+h+20)*2)
    ground=np.median(YM[wy0:wy1,wx0:wx1])
    yb=YM[y0:y1,x0:x1][halo]
    dev=np.abs(yb-ground)>0.08
    frac=dev.mean()
    if frac>0.0:
        yy,xx=np.nonzero(halo)
        sel=dev
        px=(x0+xx[sel])/2; py=(y0+yy[sel])/2
        txt=''.join(s[0] for s in segs).replace('\n','/')[:20]
        print(tid,txt,'ground Y %.3f'%ground,'frac %.4f'%frac,'n',sel.sum(),'x %.1f-%.1f y %.1f-%.1f'%(px.min(),px.max(),py.min(),py.max()), 'minY %.3f maxY %.3f'%(yb.min(),yb.max()))
