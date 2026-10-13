import numpy as np, sys, json
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
P=np.asarray(Image.open(R+'r10/poster_2x.png').convert('RGB')).astype(float)
M=np.asarray(Image.open(R+'r10/map_only_2x.png').convert('RGB')).astype(float)
def Y(rgb):
    c=rgb/255.0; l=np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4); return l@[0.2126,0.7152,0.0722]
spec={t[0]:t for t in json.load(open(R+'text_spec_r10.json'))['texts']}
for tid in sys.argv[1:]:
    t=spec[tid]; x,y,w,h=t[1]
    X0,Y0,X1,Y1=int((x-30)*2),int((y-30)*2),int((x+w+30)*2),int((y+h+30)*2)
    X0=max(X0,0);Y0=max(Y0,0)
    d=np.abs(P[Y0:Y1,X0:X1]-M[Y0:Y1,X0:X1]).sum(2)
    ink=d>24
    # restrict ink to text box +2
    bx=np.zeros_like(ink); bx[int((y-2)*2)-Y0:int((y+h+2)*2)-Y0,int((x-2)*2)-X0:int((x+w+2)*2)-X0]=True
    ink&=bx
    YM=Y(M[Y0:Y1,X0:X1]); g=np.median(YM)
    obj=np.abs(YM-g)>0.08
    dist=ndi.distance_transform_edt(~ink)
    if obj.sum()==0: print(tid,'no obj'); continue
    dd=dist[obj]; i=np.argmin(dd); yy,xx=np.nonzero(obj)
    print(tid, 'ground Y %.3f'%g, 'min gap ink->object %.2f pt at (%.1f,%.1f)'%(dd.min()/2,(X0+xx[i])/2,(Y0+yy[i])/2))
