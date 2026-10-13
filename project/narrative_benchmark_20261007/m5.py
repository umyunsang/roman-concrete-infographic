import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage import color, measure
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx=json.load(open(B+'assets_index.json')); A={a['id']:a for a in idx['assets']}
mine=['shape_core1_marker','shape_core2_marker','shape_core3_marker','shape_core4_marker','shape_core5_marker','shape_d2_leader','shape_d3_section','shape_pin_harbor','shape_pin_pompeii']
for aid in mine:
    a=A[aid]
    al=np.asarray(Image.open(a['files']['isolated_rgba']))[...,3].astype(float)/255
    ctx=np.asarray(Image.open(a['files']['context']).convert('RGB')).astype(float)/255
    lab=color.rgb2lab(ctx)
    m=al>0.5
    din=ndi.distance_transform_edt(m)/3.0   # pt
    dout=ndi.distance_transform_edt(~m)/3.0
    inner=(din>=0.34)&(din<=3)   # thin lines: from 1px inward
    outer=(dout>=1)&(dout<=3)
    cont=np.argwhere(m & (din<=0.34))
    H,W=m.shape
    res=[]
    for k,(r,c) in enumerate(cont[::3]):
        r0,r1,c0,c1=max(0,r-9),min(H,r+10),max(0,c-9),min(W,c+10)
        ii=inner[r0:r1,c0:c1]; oo=outer[r0:r1,c0:c1]
        if ii.sum()<2 or oo.sum()<2: continue
        li=np.median(lab[r0:r1,c0:c1][ii],axis=0); lo=np.median(lab[r0:r1,c0:c1][oo],axis=0)
        dL=abs(li[0]-lo[0]); dE=color.deltaE_ciede2000(li[None,None],lo[None,None])[0,0]
        res.append((dL,dE))
    res=np.array(res)
    ok=((res[:,0]>=10)|(res[:,1]>=10)).mean()
    lost=((res[:,0]<5)&(res[:,1]<5)).mean()
    print(aid,'samples',len(res),'pass(>=10) %.1f%%'%(100*ok),'lost %.1f%%'%(100*lost),'median dL %.1f dE %.1f min dL %.1f'%(np.median(res[:,0]),np.median(res[:,1]),res[:,0].min()))
