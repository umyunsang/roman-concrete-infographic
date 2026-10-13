import numpy as np, json, sys
from PIL import Image
from scipy import ndimage as ndi
from skimage import color, measure, morphology
A='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/assets'
def de76(a,b): return np.sqrt(((a-b)**2).sum(-1))
for a in sys.argv[1:]:
    ctx=np.asarray(Image.open(f'{A}/{a}/context.png').convert('RGB')).astype(float)/255
    al=np.asarray(Image.open(f'{A}/{a}/isolated_rgba.png'))[...,3]>127
    m=morphology.binary_closing(al,morphology.disk(2))
    lab=color.rgb2lab(ctx)
    din=ndi.distance_transform_edt(m); dout=ndi.distance_transform_edt(~m)
    # I3-13 global: inside 2-10pt (6-30px) vs outside 2-10pt
    ins=(din>=6)&(din<=30); outs=(dout>=6)&(dout<=30)
    gi=np.median(lab[ins],0); go=np.median(lab[outs],0)
    i313_dL=abs(gi[0]-go[0]); i313_de=de76(gi,go)
    # per-contour samples every 3px
    cs=measure.find_contours(m.astype(float),0.5)
    H,W=m.shape
    samples=[]; runs=[]
    for c in cs:
        if len(c)<9: continue
        # resample by arc length 3px
        d=np.r_[0,np.cumsum(np.hypot(*np.diff(c,axis=0).T))]
        tt=np.arange(0,d[-1],3.0)
        pts=np.c_[np.interp(tt,d,c[:,0]),np.interp(tt,d,c[:,1])]
        seq=[]
        for y,x in pts:
            y0,y1=int(max(0,y-9)),int(min(H,y+10)); x0,x1=int(max(0,x-9)),int(min(W,x+10))
            yy,xx=np.mgrid[y0:y1,x0:x1]; disk=(yy-y)**2+(xx-x)**2<=81
            di=din[y0:y1,x0:x1]; do=dout[y0:y1,x0:x1]
            I=disk&(di>=3)&(di<=9); O=disk&(do>=3)&(do<=9)
            if I.sum()<3 or O.sum()<3: seq.append(None); continue
            li=np.median(lab[y0:y1,x0:x1][I],0); lo=np.median(lab[y0:y1,x0:x1][O],0)
            dL=abs(li[0]-lo[0]); dE=float(color.deltaE_ciede2000(li[None,None],lo[None,None])[0,0])
            seq.append((dL,dE))
        samples+= [s for s in seq if s is not None]
        # longest run of lost contour
        best=cur=0
        for s in seq:
            if s is not None and s[0]<5 and s[1]<5: cur+=1; best=max(best,cur)
            else: cur=0
        runs.append((best,len(seq)))
    S=np.array(samples)
    ok=((S[:,0]>=10)|(S[:,1]>=10)).mean(); lost=((S[:,0]<5)&(S[:,1]<5)).mean()
    maxrun=max(runs,key=lambda r:r[0]/max(r[1],1))
    print(f'{a}: n={len(S)} strong(>=10)={ok*100:.1f}% lost={lost*100:.1f}% worst run {maxrun[0]}/{maxrun[1]} ({maxrun[0]/max(maxrun[1],1)*100:.1f}% of that contour) | I3-13 dL={i313_dL:.1f} dE76={i313_de:.1f} medians in {gi.round(1)} out {go.round(1)}')
