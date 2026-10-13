import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
P=np.asarray(Image.open(R+'r10/poster_2x.png').convert('RGB')).astype(float)
M=np.asarray(Image.open(R+'r10/map_only_2x.png').convert('RGB')).astype(float)
def L709(a): return 0.2126*a[...,0]+0.7152*a[...,1]+0.0722*a[...,2]
LP=L709(P); LM=L709(M); D=np.abs(P-M).sum(2)
spec=json.load(open(R+'text_spec_r10.json'))['texts']
blocks=[('790:80','790:98'),('790:81','790:99'),('790:177','790:178'),('790:180','790:181'),('790:183','790:184'),('790:174','790:175'),
('790:109','790:112','790:113'),('790:121','790:123','790:126'),('790:122','790:125','790:127'),('790:192','790:193')]
S={t[0]:t for t in spec}
def lines(id_):
    _,box,rot,al,segs=S[id_]; x,y,w,h=box
    X0,Y0,X1,Y1=int((x-0.5)*2),int((y-0.5)*2),int((x+w+0.5)*2),int((y+h+0.5)*2)
    G=(D[Y0:Y1,X0:X1]>40)&(LP[Y0:Y1,X0:X1]<LM[Y0:Y1,X0:X1])
    rows=G.any(1); lab,n=ndi.label(ndi.binary_closing(rows,iterations=2)); out=[]
    for i in range(1,n+1):
        rr=np.where(lab==i)[0]
        if len(rr)<6: continue
        g=G[rr[0]:rr[-1]+1]; cols=np.where(g.any(0))[0]
        # coverage-weighted density
        sub=LP[Y0+rr[0]:Y0+rr[-1]+1, X0+cols[0]:X0+cols[-1]+1]; bg=LM[Y0+rr[0]:Y0+rr[-1]+1, X0+cols[0]:X0+cols[-1]+1]
        cov=np.clip((bg-sub)/np.maximum(bg-sub.min(),1),0,1)
        out.append(dict(top=(Y0+rr[0])/2,bot=(Y0+rr[-1]+1)/2,left=(X0+cols[0])/2,right=(X0+cols[-1]+1)/2,dens=cov.mean()))
    return out
for b in blocks:
    s=[]
    for id_ in b:
        for l in lines(id_): s.append((id_,l['left'],l['top'],l['bot'],round(l['dens'],3), l['right']))
    lefts=[v[1] for v in s]
    print(b,'left range',max(lefts)-min(lefts), [(v[0],v[1],v[2],v[3],v[4],v[5]) for v in s])
