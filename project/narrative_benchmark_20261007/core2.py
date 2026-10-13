from PIL import Image
import numpy as np, json
im=np.asarray(Image.open('../nb_work/review_loop/r9/poster_2x.png').convert('RGB')).astype(float)
mo=np.asarray(Image.open('../nb_work/review_loop/r9/map_only_2x.png').convert('RGB')).astype(float)
spec={t[0]:t for t in json.load(open('../nb_work/review_loop/text_spec_r9.json'))['texts']}
for b in ['790:147','790:153','790:159','790:165','790:171']:
    x,y,w,h=spec[b][1]
    X0,Y0,X1,Y1=int(x*2)-4,int(y*2)-6,int((x+w)*2)+4,int((y+h)*2)+2
    P=im[Y0:Y1,X0:X1]; M=mo[Y0:Y1,X0:X1]
    redP=(P[...,0]-P[...,1]>40)&(P[...,0]-P[...,2]>40)
    redM=(M[...,0]-M[...,1]>40)&(M[...,0]-M[...,2]>40)
    t=redP&~redM
    yy,xx=np.nonzero(t)
    # also measure underline rows (in map-only) further below
    UY0,UY1=int((y+h)*2)-4,int((y+h)*2)+24
    MM=mo[UY0:UY1,X0:X1+80]
    redU=(MM[...,0]-MM[...,1]>40)&(MM[...,0]-MM[...,2]>40)
    rs=redU.sum(1); rows=np.nonzero(rs>=60)[0]
    cols=np.nonzero(redU[rows].any(0))[0]
    ul=((X0+cols.min())/2,(X0+cols.max()+1)/2,(UY0+rows.min())/2,(UY0+rows.max()+1)/2)
    print(b, spec[b][4][0][0], 'L2 red ink x %.1f-%.1f w=%.1f  y %.1f-%.1f'%((xx.min()+X0)/2,(xx.max()+X0+1)/2,(xx.max()-xx.min()+1)/2,(yy.min()+Y0)/2,(yy.max()+Y0+1)/2),
      ' UL x %.1f-%.1f len=%.1f y %.1f-%.1f'%(ul[0],ul[1],ul[1]-ul[0],ul[2],ul[3]), ' len-w=%+.1f'%((ul[1]-ul[0])-(xx.max()-xx.min()+1)/2), 'gap L2->UL %.1f'%(ul[2]-(yy.max()+Y0+1)/2))
