import numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
M=Image.open(R+'r10/map_only_2x.png').convert('RGB')
A=np.asarray(M).astype(float); H=np.asarray(M.convert('HSV')).astype(float)
def Y(rgb):
    c=rgb/255.0; l=np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4); return l@[0.2126,0.7152,0.0722]
def cr(a,b):
    a,b=np.maximum(a,b),np.minimum(a,b); return (a+0.05)/(b+0.05)
regs={'ms1':(440,355,535,460),'ms2':(185,900,265,1010),'ms3':(765,900,860,1010)}
for k,(x0,y0,x1,y1) in regs.items():
    sub=A[y0*2:y1*2,x0*2:x1*2]; hs=H[y0*2:y1*2,x0*2:x1*2]
    hue=hs[...,0]*360/255; sat=hs[...,1]/255; val=hs[...,2]/255
    red=((hue<25)|(hue>335))&(sat>0.45)&(val>0.12)
    red=ndi.binary_closing(red,iterations=2); red=ndi.binary_fill_holes(red)
    lab,n=ndi.label(red); sizes=ndi.sum(red,lab,range(1,n+1)); keep=lab==(np.argmax(sizes)+1)
    Ys=Y(sub)
    face=ndi.binary_erosion(keep,iterations=3)
    yface=np.median(Ys[face]); faceRGB=np.median(sub[face],axis=0).astype(int)
    yedge=np.median(Ys[keep&~face])
    for a,b in [(1,4),(4,8)]:
        ring=ndi.binary_dilation(keep,iterations=b)&~ndi.binary_dilation(keep,iterations=a)
        yr=Ys[ring]; c=cr(yface,yr)
        print(k,'face rgb',faceRGB,'Yface %.3f'%yface,'Yedge(bevel) %.3f'%yedge,'ring %.1f-%.1fpt: Ymed %.3f'%(a/2,b/2,np.median(yr)),'C(face vs ring med) %.2f'%cr(yface,np.median(yr)),'frac<3 %.2f'%np.mean(c<3),'frac<2 %.2f'%np.mean(c<2))
    # what is the dark ring? classify ring 1-4px: shadow (low sat dark), pillar (stone), paper
