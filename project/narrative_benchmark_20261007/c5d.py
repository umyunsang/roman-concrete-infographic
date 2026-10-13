import numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
M=Image.open(R+'r10/map_only_2x.png').convert('RGB')
A=np.asarray(M).astype(float); H=np.asarray(M.convert('HSV')).astype(float)
def Y(rgb):
    c=rgb/255.0; l=np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4); return l@[0.2126,0.7152,0.0722]
cr=lambda a,b:(np.maximum(a,b)+0.05)/(np.minimum(a,b)+0.05)
regs={'ms1':(440,355,535,460),'ms2':(185,900,265,1010),'ms3':(765,900,860,1010)}
for k,(x0,y0,x1,y1) in regs.items():
    sub=A[y0*2:y1*2,x0*2:x1*2]; hs=H[y0*2:y1*2,x0*2:x1*2]
    hue=hs[...,0]*360/255; sat=hs[...,1]/255; val=hs[...,2]/255
    redall=((hue<25)|(hue>335))&(sat>0.45)&(val>0.12)
    redall=ndi.binary_fill_holes(ndi.binary_closing(redall,iterations=2))
    lab,n=ndi.label(redall); sizes=ndi.sum(redall,lab,range(1,n+1)); plate=lab==(np.argmax(sizes)+1)
    bright=plate&(val>0.45)&(sat>0.6)
    Ys=Y(sub); yb=np.median(Ys[bright]); 
    ring=ndi.binary_dilation(plate,iterations=8)&~ndi.binary_dilation(plate,iterations=3)
    yr=Ys[ring]; c=cr(yb,yr)
    # outer silhouette contrast: darkest plate part (edge) vs ring
    print(k,'bright face rgb',np.median(sub[bright],axis=0).astype(int),'Y %.3f'%yb,'| ring(1.5-4pt) Y median %.3f -> C %.2f'%(np.median(yr),cr(yb,np.median(yr))),'| ring px frac<3: %.2f'%np.mean(c<3),'| silhouette (all plate) Y med %.3f -> C vs ring med %.2f'%(np.median(Ys[plate]),cr(np.median(Ys[plate]),np.median(yr))))
