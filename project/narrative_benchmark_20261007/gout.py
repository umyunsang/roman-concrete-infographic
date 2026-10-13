import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
ink=np.load('ink.npy'); g=np.load('grad.npy').astype(np.float32)
M=np.asarray(Image.open(R+'r10/map_only_2x.png').convert('RGB')).astype(np.int16)
cores=json.load(open('cores.json'))
paper=np.array([238,226,204])
for k,v in cores.items():
    x0,y0,x1,y1=v[4]
    m=80
    X0,Y0,X1,Y1=int((x0-m)*2),int((y0-m)*2),int((x1+m)*2),int((y1+m)*2)
    X0=max(X0,0);Y0=max(Y0,0)
    win=M[Y0:Y1,X0:X1]
    obj=(g[Y0:Y1,X0:X1]>12)|(np.sqrt(((win-paper)**2).sum(2))>40)
    # block region mask = text-spec union box +1pt (own ink, disk, underline)
    blk=np.zeros(obj.shape,bool); blk[int((y0-1)*2)-Y0:int((y1+1)*2)-Y0,int((x0-1)*2)-X0:int((x1+1)*2)-X0]=True
    obj&=~blk
    # ink of this block (all ink inside box) + disk/underline region => use block box itself as source
    src=np.zeros_like(blk); 
    sub=ink[int(y0*2):int(y1*2),int(x0*2):int(x1*2)]
    src[int(y0*2)-Y0:int(y1*2)-Y0,int(x0*2)-X0:int(x1*2)-X0]=sub
    # add red disk/underline pixels in box
    redm=(win[...,0]-win[...,1]>40)&(win[...,0]>100)
    src|=redm&blk
    dt=ndi.distance_transform_edt(~src)
    lab,n=ndi.label(ndi.binary_dilation(obj,iterations=2))
    items=[]
    for i in range(1,n+1):
        mm=(lab==i)&obj
        if mm.sum()<30: continue
        d=dt[mm].min()/2
        ys,xs=np.nonzero(mm)
        items.append((d,(xs.min()+X0)/2,(ys.min()+Y0)/2,(xs.max()+X0)/2,(ys.max()+Y0)/2,int(mm.sum())))
    items.sort()
    print('CORE',k)
    for it in items[:7]: print('   d=%.1f bbox=(%.0f,%.0f)-(%.0f,%.0f) n=%d'%it)
