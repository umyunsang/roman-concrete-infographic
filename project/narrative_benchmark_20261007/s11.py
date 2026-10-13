import sys; sys.path.insert(0,"/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/oc_b1")
from base import *
mine=['support_breakwater_block','support_harbor','support_pompeii_site','support_privernum','support_ruin_observers','landmark_pompeii_town','landmark_vesuvius','landmark_lime_kiln','landmark_apennines','landmark_aqueduct']
m11,ov11=r11_obj(); n2i=name2id()
mat,obj,matname,objkey=v813()
mo=np.asarray(Image.open(B+'nb_work/review_loop/r11/map_only_2x.png').convert('RGB')).astype(float)
H,W=m11.shape
# resample map_only to ID grid (bilinear)
yy=(np.arange(H)+0.5)*(2/S2)-0.5; xx=(np.arange(W)+0.5)*(2/S2)-0.5
y0=np.floor(yy).astype(int); x0=np.floor(xx).astype(int); fy=(yy-y0)[:,None,None]; fx=(xx-x0)[None,:,None]
y0=np.clip(y0,0,mo.shape[0]-2); x0=np.clip(x0,0,mo.shape[1]-2)
img=(mo[y0][:,x0]*(1-fy)*(1-fx)+mo[y0+1][:,x0]*fy*(1-fx)+mo[y0][:,x0+1]*(1-fy)*fx+mo[y0+1][:,x0+1]*fy*fx)
np.save('img_idgrid.npy',img.astype(np.float32))
res={}
for aid in mine:
    a=A[aid]; ids=[n2i[n] for n in a['objects']]
    msk=np.isin(m11,ids)&(ov11==0)
    ys,xs=np.where(msk); y0_,y1_=max(ys.min()-12,0),min(ys.max()+12,H); x0_,x1_=max(xs.min()-12,0),min(xs.max()+12,W)
    M=msk[y0_:y1_,x0_:x1_]; I=img[y0_:y1_,x0_:x1_]
    Lb=lab(I.reshape(-1,3)).reshape(I.shape); ok=oklch(I.reshape(-1,3)).reshape(I.shape)
    # material label inside asset (v813)
    keys=[objkey[n] for n in a['objects']]
    MAT=np.where(np.isin(obj[y0_:y1_,x0_:x1_],keys),mat[y0_:y1_,x0_:x1_],-1)
    din=ndi.distance_transform_edt(M); dout=ndi.distance_transform_edt(~M)
    band=M&(din<=1.0)
    inref=M&(din>=2)&(din<=4); outref=(~M)&(dout>=2)&(dout<=4)
    def lmean(ref,ch):
        num=ndi.uniform_filter(np.where(ref,ch,0),size=9); den=ndi.uniform_filter(ref.astype(float),size=9)
        return np.where(den>0,num/np.maximum(den,1e-9),np.nan), den
    Lin,_=lmean(inref,Lb[...,0]); Lout,dd=lmean(outref,Lb[...,0])
    lo=np.minimum(Lin,Lout)-5; hi=np.maximum(Lin,Lout)+5
    valid=band&~np.isnan(Lin)&~np.isnan(Lout)
    haloL=valid&((Lb[...,0]<lo)|(Lb[...,0]>hi))
    # hue
    def hmean(ref):
        a_,_=lmean(ref,Lb[...,1]); b_,_=lmean(ref,Lb[...,2]); return a_,b_
    ai,bi=hmean(inref); ao,bo=hmean(outref)
    hb=np.degrees(np.arctan2(Lb[...,2],Lb[...,1])); hi_=np.degrees(np.arctan2(bi,ai)); ho=np.degrees(np.arctan2(bo,ao))
    Cb=np.hypot(Lb[...,1],Lb[...,2]); Ci=np.hypot(ai,bi); Co=np.hypot(ao,bo)
    def hd(x,y): return np.abs((x-y+180)%360-180)
    chroma_ok=(Cb>=3)&(Ci>=3)&(Co>=3)
    haloH=valid&chroma_ok&(hd(hb,hi_)>30)&(hd(hb,ho)>30)
    halo=haloL|haloH
    # split by dark/bright & where
    dark=haloL&(Lb[...,0]<lo); bright=haloL&(Lb[...,0]>hi)
    # material boundary inside asset
    mb=np.zeros_like(M)
    for k in np.unique(MAT[M]):
        if k<0: continue
        r=(MAT==k)&M
        mb|=r&ndi.binary_dilation((MAT!=k)&M&(MAT>=0),iterations=1)
    res[aid]=dict(band=int(valid.sum()),halo=int(halo.sum()),pct=round(float(halo.sum()/max(valid.sum(),1)*100),2),dark=int(dark.sum()),bright=int(bright.sum()),hue=int(haloH.sum()),matb=int(mb.sum()))
    print(aid,res[aid])
    vis=np.clip(I,0,255).astype(np.uint8).copy(); vis[dark]=[255,0,0]; vis[bright]=[0,180,255]; vis[haloH&~haloL]=[255,0,255]
    Image.fromarray(vis).resize((vis.shape[1]*2,vis.shape[0]*2),Image.NEAREST).save(f'halo_{aid}.png')
