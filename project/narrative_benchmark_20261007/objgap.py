import json, sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
P=np.asarray(Image.open(R+'r10/poster_2x.png').convert('RGB')).astype(float)
M=np.asarray(Image.open(R+'r10/map_only_2x.png').convert('RGB')).astype(float)
spec={t[0]:t for t in json.load(open(R+'text_spec_r10.json'))['texts']}
D=np.abs(P-M).sum(2)
def L709(a): return 0.2126*a[...,0]+0.7152*a[...,1]+0.0722*a[...,2]
LP=L709(P); LM=L709(M)
ids=sys.argv[1:]
for id_ in ids:
    _,box,rot,al,segs=spec[id_]
    x,y,w,h=box
    X0,Y0,X1,Y1=int((x-1)*2),int((y-1)*2),int((x+w+1)*2),int((y+h+1)*2)
    m=30
    A0,B0,A1,B1=X0-m,Y0-m,X1+m,Y1+m
    Mw=M[B0:B1,A0:A1]; 
    G=np.zeros(Mw.shape[:2],bool)
    sl=(slice(Y0-B0,Y1-B0),slice(X0-A0,X1-A0))
    G[sl]=(D[Y0:Y1,X0:X1]>40)&(LP[Y0:Y1,X0:X1]<LM[Y0:Y1,X0:X1])
    # paper reference: median color of map pixels in window that are bright & low-sat
    Lw=L709(Mw)
    paper=np.median(Mw.reshape(-1,3)[Lw.reshape(-1)>np.percentile(Lw,60)],axis=0)
    dev=np.sqrt(((Mw-paper)**2).sum(2))
    for thr in (12,20,30):
        O=dev>thr
        O=ndi.binary_opening(O,iterations=1)
        dist=ndi.distance_transform_edt(~G)
        if O.sum()==0: print(id_,thr,'none'); continue
        k=np.argmin(np.where(O,dist,1e9)); qy,qx=np.unravel_index(k,O.shape)
        print(id_, 'thr',thr,'paper',paper.round(0),'min gap pt',round(dist[qy,qx]/2,2),'at',((A0+qx)/2,(B0+qy)/2), 'obj px under ink box', O[sl].sum())
