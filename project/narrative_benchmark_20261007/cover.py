import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx=json.load(open(R+'assets_index.json'))
oid=json.load(open('oid.json')); a2o=json.load(open('a2o.json'))
final=np.load('final.npy'); m=np.load('m.npy')
PX=final.shape[1]/1191
land=oid['T_land']; sea=oid['L10_sea']; tib=oid['L02_tiber']; wm=oid['W_water_marks']
res={}
for a in idx['assets']:
    aid=a['id']; x0,x1,y0,y1=a['crop_pt']
    al=np.array(Image.open(a['files']['isolated_rgba']))[...,3]>=128
    h,w=al.shape
    v,u=np.nonzero(al)
    X=x0+(u+0.5)/3; Y=y0+(v+0.5)/3
    ix=np.clip((X*PX).astype(int),0,final.shape[1]-1); iy=np.clip((Y*PX).astype(int),0,final.shape[0]-1)
    f=final[iy,ix]
    own=set(oid[n] for n in a2o[aid])
    onland=(f==land)
    # exclude bottom 0.5pt band of each column of silhouette (support contact band)
    bottom=np.zeros_like(al)
    colmax=np.where(al.any(0), h-1-np.argmax(al[::-1],0), -1)
    band=np.zeros(len(u),bool)
    band=(v>=colmax[u]-1.5)  # 0.5pt = 1.5px
    cov=np.zeros_like(al); cov[v[onland],u[onland]]=True
    cov2=np.zeros_like(al); sel=onland&~band; cov2[v[sel],u[sel]]=True
    lab,n=ndi.label(cov)
    sizes=ndi.sum(cov,lab,range(1,n+1)) if n else np.array([0])
    vis=np.isin(f,list(own)).sum()
    res[aid]=dict(M=len(u)/9, vis_pt2=vis/9, land_in_M_pt2=onland.sum()/9, land_in_M_noband_pt2=sel.sum()/9,
                  frac=onland.sum()/max(1,len(u)), maxblob_pt2=float(sizes.max())/9, nblob_ge2=int((sizes/9>=2).sum()))
    if res[aid]['maxblob_pt2']>=2:
        k=int(np.argmax(sizes))+1; vv,uu=np.nonzero(lab==k)
        res[aid]['maxblob_center_pt']=[round(x0+uu.mean()/3,1), round(y0+vv.mean()/3,1)]
        bl=[]
        for kk in np.argsort(-sizes)[:6]:
            if sizes[kk]/9<2: break
            vv,uu=np.nonzero(lab==kk+1); bl.append([round(x0+uu.mean()/3,1), round(y0+vv.mean()/3,1), round(sizes[kk]/9,1)])
        res[aid]['blobs']=bl
json.dump(res,open('cover.json','w'),indent=1)
for k,v in sorted(res.items(), key=lambda kv:-kv[1]['maxblob_pt2']):
    print(k, {kk:(round(vv,3) if isinstance(vv,float) else vv) for kk,vv in v.items()})
