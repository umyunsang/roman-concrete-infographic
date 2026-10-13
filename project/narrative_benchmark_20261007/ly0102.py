import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
spec=json.load(open(R+'text_spec_r10.json'))['texts']
ink=np.load('ink.npy'); g=np.load('grad.npy').astype(np.float32)
M=np.asarray(Image.open(R+'r10/map_only_2x.png').convert('RGB')).astype(np.int16)
H,W=ink.shape
res={}
for t in spec:
    tid,(x,y,w,h),rot=t[0],t[1],t[2]
    if rot!=0: continue
    pad=4
    x0,y0,x1,y1=[int(round(v*2)) for v in (x-pad,y-pad,x+w+pad,y+h+pad)]
    x0=max(x0,0);y0=max(y0,0);x1=min(x1,W);y1=min(y1,H)
    sub=ink[y0:y1,x0:x1]
    ys,xs=np.nonzero(sub)
    if len(ys)==0: print(tid,'no ink');continue
    iy0,iy1,ix0,ix1=ys.min()+y0,ys.max()+y0,xs.min()+x0,xs.max()+x0
    # window
    m=60
    wx0,wy0,wx1,wy1=max(ix0-m,0),max(iy0-m,0),min(ix1+m,W),min(iy1+m,H)
    win=M[wy0:wy1,wx0:wx1]
    # paper: ring 30px around ink bbox
    ring=np.zeros(win.shape[:2],bool)
    ry0,ry1,rx0,rx1=iy0-wy0-30,iy1-wy0+30,ix0-wx0-30,ix1-wx0+30
    ring[max(ry0,0):ry1,max(rx0,0):rx1]=True
    ring[iy0-wy0:iy1-wy0+1,ix0-wx0:ix1-wx0+1]=False
    pix=win[ring]; Lp=0.299*pix[:,0]+0.587*pix[:,1]+0.114*pix[:,2]
    bright=pix[Lp>=np.percentile(Lp,40)]
    paper=np.median(bright,0)
    dist=np.sqrt(((win-paper)**2).sum(2))
    gw=g[wy0:wy1,wx0:wx1]
    red=(win[...,0]-win[...,1]>40)&(win[...,0]>100)
    obj=((gw>12)|(dist>28))
    objnr=obj&~red
    inkw=ink[wy0:wy1,wx0:wx1]
    # overlap: obj inside ink bbox
    ov=objnr[iy0-wy0:iy1-wy0+1, ix0-wx0:ix1-wx0+1].sum()
    dt,ind=ndi.distance_transform_edt(~objnr,return_indices=True)
    di=dt[inkw]
    k=np.argmin(di); iyx=np.argwhere(inkw)[k]
    ny,nx=ind[0][tuple(iyx)],ind[1][tuple(iyx)]
    col=win[ny,nx]
    res[tid]=dict(ink=[ix0/2,iy0/2,ix1/2,iy1/2],paper=paper.tolist(),ov=int(ov),dmin=float(di.min()/2),near=[(nx+wx0)/2,(ny+wy0)/2],col=col.tolist(),txt=t[4][0][0][:14])
    print(f"{tid:8s} ink=({ix0/2:.1f},{iy0/2:.1f})-({ix1/2:.1f},{iy1/2:.1f}) ov={ov:5d} dmin={di.min()/2:5.1f}pt near=({(nx+wx0)/2:.1f},{(ny+wy0)/2:.1f}) col={col.tolist()} paper={np.round(paper).astype(int).tolist()} {t[4][0][0][:14]!r}")
json.dump(res,open('ly0102.json','w'),ensure_ascii=False)
