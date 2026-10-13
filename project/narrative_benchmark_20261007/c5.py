import numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
M=np.asarray(Image.open(R+'r10/map_only_2x.png').convert('RGB')).astype(float)
def Y(rgb):
    c=rgb/255.0; l=np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4); return l@[0.2126,0.7152,0.0722]
def cr(a,b):
    a,b=max(a,b),min(a,b); return (a+0.05)/(b+0.05)
regions={'ms1':(440,360,530,460),'ms2':(185,900,265,1010),'ms3':(770,900,860,1010),
 'disc1':(525,383,552,410),'disc2':(55,745,82,772),'disc3':(405,1029,432,1056),'disc4':(635,1029,662,1056),'disc5':(980,814,1007,841),
 'ul1':(525,425,645,436),'ul2':(55,787,170,798),'ul3':(405,1071,545,1082),'ul4':(635,1071,755,1082),'ul5':(980,856,1160,867)}
for k,(x0,y0,x1,y1) in regions.items():
    sub=M[y0*2:y1*2,x0*2:x1*2]; r,g,b=sub[...,0],sub[...,1],sub[...,2]
    red=(r-g>45)&(r>90)&(r-b>45)
    red=ndi.binary_opening(red,iterations=1)
    lab,n=ndi.label(red)
    if n==0: print(k,'none'); continue
    sizes=ndi.sum(red,lab,range(1,n+1)); keep=np.isin(lab,np.nonzero(sizes>=0.2*sizes.max())[0]+1)
    Ys=Y(sub)
    ring=ndi.binary_dilation(keep,iterations=4)&~ndi.binary_dilation(keep,iterations=1)
    fg=Ys[ndi.binary_erosion(keep,iterations=1)] if ndi.binary_erosion(keep,iterations=1).sum()>10 else Ys[keep]
    yf=np.median(fg); yr=Ys[ring]
    # per-ring pixel contrast fraction <3
    c_med=cr(yf,np.median(yr)); c_dark=cr(yf,np.percentile(yr,2)); c_light=cr(yf,np.percentile(yr,98))
    frac_lt3=np.mean([cr(yf,v)<3 for v in yr])
    medc=np.median(sub[keep],axis=0).astype(int)
    print(k,'plate/disc median',medc,'Y %.3f'%yf,'ring median Y %.3f'%np.median(yr),'C(med) %.2f'%c_med,'C(ring dark2%%) %.2f'%c_dark,'C(ring light98%%) %.2f'%c_light,'ring frac<3: %.3f'%frac_lt3,'area px',keep.sum())
