import numpy as np, sys, json
from PIL import Image
from scipy import ndimage
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
M2=Image.open(R+'r11/map_only_2x.png').convert('RGB')
def lab(rgb):
    c=rgb/255.0; lin=np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4)
    Mx=np.array([[0.4124,0.3576,0.1805],[0.2126,0.7152,0.0722],[0.0193,0.1192,0.9505]])
    XYZ=lin@Mx.T; n=np.array([0.95047,1,1.08883]); t=XYZ/n
    f=np.where(t>0.008856,np.cbrt(t),7.787*t+16/116)
    return np.stack([116*f[...,1]-16,500*(f[...,0]-f[...,1]),200*(f[...,1]-f[...,2])],-1)
def pyr(I,n=9):
    P=[I]
    for i in range(1,n):
        g=ndimage.gaussian_filter(P[-1],1.0); P.append(g[::2,::2])
    return P
def up(a,shape):
    zy=shape[0]/a.shape[0]; zx=shape[1]/a.shape[1]
    return ndimage.zoom(a,(zy,zx),order=1)[:shape[0],:shape[1]] if True else a
def N(m):
    m=m-m.min(); 
    if m.max()>0: m=m/m.max()
    mx=ndimage.maximum_filter(m,size=5)
    peaks=m[(m==mx)&(m>0.05)]
    if len(peaks)>1:
        gm=peaks.max(); mbar=(peaks.sum()-gm)/(len(peaks)-1)
    else: mbar=0
    return m*(1-mbar)**2
def chan(I):
    P=pyr(I)
    tgt=P[4].shape
    acc=np.zeros(tgt)
    for c in (2,3,4):
        for d in (3,4):
            s=c+d
            if s>=len(P) or P[s].size==0: continue
            fm=np.abs(P[c]-up(P[s],P[c].shape))
            acc+=up(N(fm),tgt)
    return N(acc)
def saliency(box_ctx):
    x0,x1,y0,y1=box_ctx
    c=M2.crop([int(x0*2),int(y0*2),int(x1*2),int(y1*2)])
    c=c.resize((c.width//2,c.height//2),Image.BOX)
    L=lab(np.array(c).astype(float))
    S=chan(L[...,0]/100)+chan(L[...,1]/100)+chan(L[...,2]/100)
    S=N(S)
    S=up(S,(c.height,c.width))
    return S
if __name__=='__main__':
    box=[float(v) for v in sys.argv[1:5]]; inner=[float(v) for v in sys.argv[5:9]]
    S=saliency(box)
    x0,y0=box[0],box[2]
    mx=ndimage.maximum_filter(S,size=13)  # ~6pt radius NMS
    pk=np.argwhere((S==mx)&(S>0.05))
    pts=[(float(S[r,c]),c+x0+0.5,r+y0+0.5) for r,c in pk]
    pts=[p for p in pts if inner[0]<=p[1]<=inner[1] and inner[2]<=p[2]<=inner[3]]
    pts.sort(reverse=True)
    for p in pts[:5]: print(round(p[0],3), round(p[1],1), round(p[2],1))
