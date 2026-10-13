import json, sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
P=np.asarray(Image.open(R+'r10/poster_2x.png').convert('RGB')).astype(float)
M=np.asarray(Image.open(R+'r10/map_only_2x.png').convert('RGB')).astype(float)
def L709(a): return 0.2126*a[...,0]+0.7152*a[...,1]+0.0722*a[...,2]
def lin(c):
    c=c/255.0; return np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4)
def relL(a):
    l=lin(a); return 0.2126*l[...,0]+0.7152*l[...,1]+0.0722*l[...,2]
LP=L709(P); LM=L709(M); D=np.abs(P-M).sum(2)
spec={t[0]:t for t in json.load(open(R+'text_spec_r10.json'))['texts']}
for id_ in sys.argv[1:]:
    _,box,rot,al,segs=spec[id_]; x,y,w,h=box
    X0,Y0,X1,Y1=int((x-1)*2),int((y-1)*2),int((x+w+1)*2),int((y+h+1)*2)
    G=(D[Y0:Y1,X0:X1]>40)&(LP[Y0:Y1,X0:X1]<LM[Y0:Y1,X0:X1])
    # lines: row runs
    rows=G.any(1); lab,n=ndi.label(rows)
    for li in range(1,n+1):
        rr=np.where(lab==li)[0]
        if len(rr)<6: continue
        g=G[rr[0]:rr[-1]+1]
        cols=g.any(0)
        # words: merge col gaps < 5px (2.5pt)
        cl=ndi.binary_closing(cols,structure=np.ones(7))
        wl,wn=ndi.label(cl)
        for wi in range(1,wn+1):
            cc=np.where(wl==wi)[0]
            gx0,gx1=X0+cc[0],X0+cc[-1]+1; gy0,gy1=Y0+rr[0],Y0+rr[-1]+1
            gg=G[rr[0]:rr[-1]+1, cc[0]:cc[-1]+1]
            # poster bg excluding glyph (L<120 dilated 2px) per rubric
            sub=P[gy0:gy1,gx0:gx1]; sL=LP[gy0:gy1,gx0:gx1]
            gm=ndi.binary_dilation((sL<120)|gg,iterations=2)
            bg=sL[~gm]
            rl=relL(sub)
            inkL=np.mean(np.sort(rl[gg])[:max(1,gg.sum()//5)])
            bgL=np.percentile(rl[~gm],5) if (~gm).sum() else np.nan
            print(f"{id_} line{li} word{wi} x{gx0/2:.1f}-{gx1/2:.1f} y{gy0/2:.1f}-{gy1/2:.1f} bgstd={bg.std():.2f} n={bg.size} contrast={(bgL+0.05)/(inkL+0.05):.2f}")
