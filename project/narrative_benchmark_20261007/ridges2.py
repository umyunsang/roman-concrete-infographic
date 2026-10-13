import sys, json, numpy as np
sys.path.insert(0,'.')
from common import *
from scipy import ndimage as ndi
aid=sys.argv[1]
a,ctx,iso,crop,(sx,sy)=load_ctx(aid)
h,w=ctx.shape[:2]; s=(sx+sy)/2
M=np.load(f'{aid}_M.npy')
L=rgb2L(ctx); lab=rgb2lab(ctx); okl=rgb2oklch(ctx)
sig=3*s
Mf=M.astype(float)
hp=np.where(M,L-ndi.gaussian_filter(L*Mf,sig)/np.maximum(ndi.gaussian_filter(Mf,sig),1e-3),0)
# print-sim L
from PIL import Image, ImageCms
icc='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/PSOcoated_v3.icc'
srgb=ImageCms.createProfile('sRGB'); cmyk=ImageCms.getOpenProfile(icc)
t1=ImageCms.buildTransform(srgb,cmyk,'RGB','CMYK',renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC,flags=ImageCms.Flags.BLACKPOINTCOMPENSATION)
t2=ImageCms.buildTransform(cmyk,srgb,'CMYK','RGB',renderingIntent=ImageCms.Intent.ABSOLUTE_COLORIMETRIC)
pim=ImageCms.applyTransform(ImageCms.applyTransform(Image.fromarray(ctx),t1),t2)
P=np.array(pim).astype(float); LP=rgb2L(P)
hpP=np.where(M,LP-ndi.gaussian_filter(LP*Mf,sig)/np.maximum(ndi.gaussian_filter(Mf,sig),1e-3),0)
np.save(f'{aid}_ctxP.npy',P)
W=int(round(12*s))
Me=ndi.binary_erosion(M,iterations=int(round(1*s)))
x0,x1,y0,y1=crop
res=[]
for y in range(0,h-W,W//2):
    for x in range(0,w-W,W//2):
        m=Me[y:y+W,x:x+W]
        if m.mean()<0.97: continue
        patch=hp[y:y+W,x:x+W]
        win2=np.hanning(W)[:,None]*np.hanning(W)[None,:]
        F=np.abs(np.fft.fftshift(np.fft.fft2((patch-patch.mean())*win2)))**2
        cy=cx=W//2
        F[cy,cx]=0
        tot=F.sum()
        k=np.unravel_index(np.argmax(F),F.shape)
        fy=(k[0]-cy)/W; fx=(k[1]-cx)/W; f=np.hypot(fx,fy)
        # energy within +-1 bin of peak and its conjugate
        e=0
        for (ky,kx) in [k,(2*cy-k[0],2*cx-k[1])]:
            e+=F[max(0,ky-1):ky+2,max(0,kx-1):kx+2].sum()
        frac=e/tot
        A=float(np.percentile(patch,90)-np.percentile(patch,10))
        pp=hpP[y:y+W,x:x+W]; AP=float(np.percentile(pp,90)-np.percentile(pp,10))
        hi=patch>=np.percentile(patch,70); lo=patch<=np.percentile(patch,30)
        lh=np.median(lab[y:y+W,x:x+W][hi],axis=0); ll=np.median(lab[y:y+W,x:x+W][lo],axis=0)
        oh=np.median(okl[y:y+W,x:x+W][hi],axis=0); ol=np.median(okl[y:y+W,x:x+W][lo],axis=0)
        res.append(dict(pt=[round(x0+(x+W/2)/sx,1),round(y0+(y+W/2)/sy,1)],period=round(1/f/s,2) if f>0 else None,frac=round(float(frac),3),A=round(A,2),A_print=round(AP,2),
           dL=round(float(lh[0]-ll[0]),2),dE00=round(de00(lh,ll),2),dC=round(float(oh[1]-ol[1]),3),dh=round(float(abs((oh[2]-ol[2]+180)%360-180)),1),medL=round(float(np.median(L[y:y+W,x:x+W])),1)))
json.dump(res,open(f'{aid}_ridges2.json','w'))
rid=[r for r in res if r['frac']>=0.25 and r['period'] and 2.4<=r['period']<=6.5]
print(aid,'windows',len(res),'ridged',len(rid))
if rid:
    for k in ['period','A','A_print','dL','dE00','dh','dC']:
        v=np.array([r[k] for r in rid]); print('  ',k,'min',round(v.min(),2),'P10',round(np.percentile(v,10),2),'med',round(np.median(v),2),'max',round(v.max(),2))
    ratio=np.array([r['A_print']/r['A'] for r in rid]); print('   print_ratio min',round(ratio.min(),3),'med',round(np.median(ratio),3))
    for r in sorted(rid,key=lambda r:r['A'])[:4]: print('   low',r)
