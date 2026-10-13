import json, numpy as np
from PIL import Image
from skimage import color
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx=json.load(open(B+'assets_index.json')); A={a['id']:a for a in idx['assets']}
def analyze(aid, cx, cy, r_dot, r_core, src='isolated_rgba'):
    a=A[aid]; x0,x1,y0,y1=a['crop_pt']
    im=np.asarray(Image.open(a['files'][src]).convert('RGBA')).astype(float)/255
    H,W,_=im.shape
    yy,xx=np.mgrid[0:H,0:W]; X=x0+(xx+0.5)/3; Y=y0+(yy+0.5)/3
    rr=np.hypot(X-cx,Y-cy)
    lab=color.rgb2lab(im[...,:3]); L=lab[...,0]
    core=(rr<=r_core)&(im[...,3]>=0.98)
    base=np.percentile(L[core],10); hi=np.percentile(L[core],95)
    thr=(base+hi)/2
    light=core&(L>=base+5)
    # dE00 between dark cluster and light cluster
    dk=lab[core&(L<thr)].mean(0); lt=lab[core&(L>=thr)].mean(0) if (core&(L>=thr)).any() else dk
    dE=color.deltaE_ciede2000(dk[None,None,:],lt[None,None,:])[0,0]
    # transitions along rows/cols within core
    maxT=0
    sub=(L>=thr)
    for r in range(H):
        cols=np.where(core[r])[0]
        if len(cols)<3: continue
        seq=sub[r,cols]
        for s in range(len(seq)):
            seg=seq[s:s+9]
            t=int(np.sum(seg[1:]!=seg[:-1])); maxT=max(maxT,t)
    for c in range(W):
        rows=np.where(core[:,c])[0]
        if len(rows)<3: continue
        seq=sub[rows,c]
        for s in range(len(seq)):
            seg=seq[s:s+9]
            t=int(np.sum(seg[1:]!=seg[:-1])); maxT=max(maxT,t)
    print(aid,'core px',core.sum(),'core area pt2 %.2f'%(core.sum()/9),'L base(p10) %.1f hi(p95) %.1f dL %.1f thr %.1f'%(base,hi,hi-base,thr),
          'light(>=base+5) area pt2 %.2f'%(light.sum()/9),'light(>=thr) area %.2f'%((core&sub).sum()/9),'dE00 dark-light %.1f'%dE,'max transitions in 3pt %d'%maxT)
analyze('shape_pin_harbor',198.0,1497.0,1.7,1.35)
analyze('shape_d2_leader',128.0,1007.0,1.6,1.3)
analyze('shape_pin_pompeii',724.03,1494.0,1.7,1.35)
for src in ['context']:
    pass
