import numpy as np, colorsys
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
M=Image.open(R+'r10/map_only_2x.png').convert('RGB')
A=np.asarray(M).astype(float); H=np.asarray(M.convert('HSV')).astype(float)
def Y(rgb):
    c=rgb/255.0; l=np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4); return l@[0.2126,0.7152,0.0722]
def cr(a,b):
    a,b=max(a,b),min(a,b); return (a+0.05)/(b+0.05)
regs={'ms1 (①→②)':(440,355,535,460),'ms2 (②→③)':(185,900,265,1010),'ms3 (④→⑤)':(765,900,860,1010)}
for k,(x0,y0,x1,y1) in regs.items():
    sub=A[y0*2:y1*2,x0*2:x1*2]; hs=H[y0*2:y1*2,x0*2:x1*2]
    hue=hs[...,0]*360/255; sat=hs[...,1]/255; val=hs[...,2]/255
    red=((hue<22)|(hue>340))&(sat>0.5)&(val>0.18)
    red=ndi.binary_closing(red,iterations=2); red=ndi.binary_fill_holes(red)
    lab,n=ndi.label(red); sizes=ndi.sum(red,lab,range(1,n+1)); keep=lab==(np.argmax(sizes)+1)
    Ys=Y(sub)
    ring=ndi.binary_dilation(keep,iterations=3)&~keep
    yf=np.median(Ys[keep]); yr=Ys[ring]
    # boundary-pixel pair contrast: for each ring pixel, nearest plate pixel luminance
    dist,idx=ndi.distance_transform_edt(~keep,return_indices=True)
    iy,ix=idx[0][ring],idx[1][ring]
    pair=np.array([cr(a,b) for a,b in zip(Ys[iy,ix],yr)])
    print(k,'plate median rgb',np.median(sub[keep],axis=0).astype(int),'Y %.3f'%yf,'| ring median Y %.3f'%np.median(yr),'C(plate med vs ring med) %.2f'%cr(yf,np.median(yr)),
          '| C(plate med vs ring per-pixel): p10 %.2f median %.2f'%(np.percentile([cr(yf,v) for v in yr],10),np.median([cr(yf,v) for v in yr])),
          '| ring frac<3 (vs plate median) %.2f'%np.mean([cr(yf,v)<3 for v in yr]), '| edge-pair median %.2f'%np.median(pair))
