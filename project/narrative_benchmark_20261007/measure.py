import json, numpy as np
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
P=np.asarray(Image.open(R+'r10/poster_2x.png').convert('RGB')).astype(float)
M=np.asarray(Image.open(R+'r10/map_only_2x.png').convert('RGB')).astype(float)
spec=json.load(open(R+'text_spec_r10.json'))['texts']
def L709(a): return 0.2126*a[...,0]+0.7152*a[...,1]+0.0722*a[...,2]
def lin(c):
    c=c/255.0; return np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4)
def relL(a):
    l=lin(a); return 0.2126*l[...,0]+0.7152*l[...,1]+0.0722*l[...,2]
LP=L709(P); LM=L709(M)
D=np.abs(P-M).sum(2)
from scipy import ndimage as ndi
out=[]
for t in spec:
    id_,box,rot,al,segs=t
    x,y,w,h=box
    txt=''.join(s[0] for s in segs)
    pad=3
    X0,Y0,X1,Y1=int((x-pad)*2),int((y-pad)*2),int((x+w+pad)*2),int((y+h+pad)*2)
    X0=max(X0,0);Y0=max(Y0,0)
    d=D[Y0:Y1,X0:X1]; lp=LP[Y0:Y1,X0:X1]; lm=LM[Y0:Y1,X0:X1]
    white = segs[0][5].upper() in ('#FFF4DD',)
    if white: ink=(d>40)&(lp>lm)
    else: ink=(d>40)&(lp<lm)
    if ink.sum()==0: print(id_,'NO INK'); continue
    ys,xs=np.where(ink)
    ib=(X0+xs.min(),Y0+ys.min(),X0+xs.max()+1,Y0+ys.max()+1)
    # glyph pixels (strong) and darkest 20%
    gl=lp[ink]
    if white: inkv=np.sort(P[Y0:Y1,X0:X1][ink].reshape(-1,3),axis=0)
    # contrast: ink = darkest 20% glyph pixels avg (relL), bg = poster pixels in ink bbox excluding dilated glyph, 5th pct (darkest)
    sub=P[ib[1]:ib[3],ib[0]:ib[2]]; subL=LP[ib[1]:ib[3],ib[0]:ib[2]]
    ginks=ink[ib[1]-Y0:ib[3]-Y0, ib[0]-X0:ib[2]-X0]
    gd=ndi.binary_dilation(ginks,iterations=2)
    rl=relL(sub)
    gv=rl[ginks]
    if white:
        inkL=np.mean(np.sort(gv)[-max(1,len(gv)//5):])
        bgv=rl[~gd]; bgL=np.percentile(bgv,95) if bgv.size else np.nan
        cr=(inkL+0.05)/(bgL+0.05)
    else:
        inkL=np.mean(np.sort(gv)[:max(1,len(gv)//5)])
        bgv=rl[~gd]; bgL=np.percentile(bgv,5) if bgv.size else np.nan
        cr=(bgL+0.05)/(inkL+0.05)
    # map bg std in ink bbox + 2pt (4px)
    mb=LM[ib[1]-4:ib[3]+4, ib[0]-4:ib[2]+4]
    out.append(dict(id=id_,txt=txt.replace('\n','/'),rot=rot,ink_pt=[round(v/2,1) for v in ib],inkh=round((ib[3]-ib[1])/2,2),cr=round(cr,2),mapstd=round(float(mb.std()),2),maprange=round(float(np.percentile(mb,99)-np.percentile(mb,1)),1)))
for o in out: print(o)
json.dump(out,open('measure_out.json','w'),ensure_ascii=False)
