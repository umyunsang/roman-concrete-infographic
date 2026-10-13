import sys, json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage import color, measure
Image.MAX_IMAGE_PIXELS=None
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx=json.load(open(B+'assets_index.json'))
obj2asset={}
for a in idx['assets']:
    for o in a['objects']: obj2asset.setdefault(o,[]).append(a['id'])
idm=json.load(open('idmap.json')); code2obj={int(k):v['obj'] for k,v in idm.items()}
ida=np.asarray(Image.open(B+'idpass/id_id_map.png'))[...,:3].astype(np.int64)
code=ida[...,0]*65536+ida[...,1]*256+ida[...,2]
s=1.9992
ground_assets={'ground_land','water_sea','water_tiber'}
for a in idx['assets']:
    if a['id'] not in sys.argv[1:]: continue
    x0,x1,y0,y1=a['crop_pt']
    ctx=np.asarray(Image.open(a['files']['context']).convert('RGB')).astype(float)/255
    H,W,_=ctx.shape
    vv,uu=np.mgrid[0:H,0:W]
    px=np.clip(((x0+uu/3)*s).astype(int),0,code.shape[1]-1); py=np.clip(((y0+vv/3)*s).astype(int),0,code.shape[0]-1)
    oc=code[py,px]
    own=np.vectorize(lambda c: code2obj.get(int(c),'?'))(np.unique(oc))
    lut={int(c):o for c,o in zip(np.unique(oc),own)}
    mine=set(a['objects'])
    m=np.isin(oc,[c for c,o in lut.items() if o in mine])
    # restrict R_core_road to the region: use vis mask from isolated compare
    vis=np.asarray(Image.open('vis_%s.png'%a['id']))>0
    if 'R_core_road' in mine: m=m&ndi.binary_dilation(vis,iterations=3)
    lbl,n=ndi.label(m); 
    if n>1:
        sz=ndi.sum(m,lbl,range(1,n+1)); m=np.isin(lbl,1+np.nonzero(sz>=max(sz.max()*0.02,30))[0])
    m=ndi.binary_fill_holes(m)
    isground=np.isin(oc,[c for c,o in lut.items() if any(x in ground_assets for x in obj2asset.get(o,[]))])
    lab=color.rgb2lab(ctx)
    din=ndi.distance_transform_edt(m); dout=ndi.distance_transform_edt(~m)
    cs=measure.find_contours(m.astype(float),0.5)
    rows=[]
    for c in cs:
        d=np.r_[0,np.cumsum(np.hypot(*np.diff(c,axis=0).T))]
        if d[-1]<9: continue
        for t in np.arange(0,d[-1],3.0):
            i=min(np.searchsorted(d,t),len(c)-1); y,x=c[i]
            if y<6 or x<6 or y>H-7 or x>W-7: continue
            ya,yb,xa,xb=int(max(0,y-12)),int(min(H,y+13)),int(max(0,x-12)),int(min(W,x+13))
            yy,xx=np.mgrid[ya:yb,xa:xb]; rr=np.hypot(yy-y,xx-x)<=12
            si=m[ya:yb,xa:xb]&(din[ya:yb,xa:xb]>=3)&(din[ya:yb,xa:xb]<=9)&rr
            so=(~m[ya:yb,xa:xb])&(dout[ya:yb,xa:xb]>=3)&(dout[ya:yb,xa:xb]<=9)&rr
            if si.sum()<5 or so.sum()<5: continue
            li=np.median(lab[ya:yb,xa:xb][si],axis=0); lo=np.median(lab[ya:yb,xa:xb][so],axis=0)
            gfrac=isground[ya:yb,xa:xb][so].mean()
            dL=abs(li[0]-lo[0]); dE=float(color.deltaE_ciede2000(li[None,None],lo[None,None])[0,0])
            rows.append((y,x,dL,dE,gfrac))
    R=np.array(rows)
    def stats(R):
        ok=(R[:,2]>=10)|(R[:,3]>=10); lost=(R[:,2]<5)&(R[:,3]<5)
        run=best=0
        for v in lost: run=run+1 if v else 0; best=max(best,run)
        return len(R), ok.mean()*100, lost.mean()*100, best/len(R)*100
    allst=stats(R); G=R[R[:,4]>=0.5]; gst=stats(G) if len(G) else None
    nong=R[R[:,4]<0.5]
    owners={}
    print('%-20s ALL n=%d pass=%.1f%% lost=%.1f%% maxrun=%.1f%% | vs GROUND only n=%d pass=%.1f%% lost=%.1f%% maxrun=%.1f%% | non-ground samples %d (lost %d)'%((a['id'],)+allst+gst+(len(nong), int(((nong[:,2]<5)&(nong[:,3]<5)).sum()))))
    np.save('contid_%s.npy'%a['id'],R)
