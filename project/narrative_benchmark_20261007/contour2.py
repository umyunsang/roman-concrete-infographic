import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage import color, measure
RL='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
A={a['id']:a for a in json.load(open(RL+'assets_index.json'))['assets']}
S=3
def contour(aid, sel=None, label=''):
    a=A[aid]; rgba=np.asarray(Image.open(a['files']['isolated_rgba']).convert('RGBA')).astype(float)/255
    ctx=np.asarray(Image.open(a['files']['context']).convert('RGB')).astype(float)/255
    m=rgba[...,3]>0.5
    if sel is not None:
        X0,X1=sel; mm=np.zeros_like(m); mm[:,X0:X1]=True; m=m&mm
    filled=ndi.binary_fill_holes(m); lab=color.rgb2lab(ctx)
    din=ndi.distance_transform_edt(filled); dout=ndi.distance_transform_edt(~filled)
    inner=(din>=S)&(din<=3*S); outer=(dout>=S)&(dout<=3*S)
    res=[]
    for c in measure.find_contours(filled.astype(float),0.5):
        if len(c)<10: continue
        seg=np.diff(c,axis=0); cum=np.concatenate([[0],np.cumsum(np.hypot(seg[:,0],seg[:,1]))])
        for t in np.arange(0,cum[-1],S):
            i=min(np.searchsorted(cum,t,side='right')-1,len(c)-1); y,x=map(int,c[i]); R=12
            y0,y1,x0,x1=max(0,y-R),min(m.shape[0],y+R+1),max(0,x-R),min(m.shape[1],x+R+1)
            yy,xx=np.mgrid[y0:y1,x0:x1]; near=np.hypot(yy-y,xx-x)<=R
            ii=inner[y0:y1,x0:x1]&near; oo=outer[y0:y1,x0:x1]&near
            if ii.sum()<3 or oo.sum()<3: continue
            li=np.median(lab[y0:y1,x0:x1][ii],axis=0); lo=np.median(lab[y0:y1,x0:x1][oo],axis=0)
            res.append((x,y,abs(li[0]-lo[0]),float(color.deltaE_ciede2000(li[None],lo[None])[0]),float(np.linalg.norm(li-lo))))
    r=np.array(res)
    ok=((r[:,2]>=10)|(r[:,3]>=10)).mean(); lost=((r[:,2]<5)&(r[:,3]<5))
    run=best=0
    for v in lost: run=run+1 if v else 0; best=max(best,run)
    i313=((r[:,2]>=10)|(r[:,4]>=25)).mean()
    print(f'{label:28s} n={len(r)} ok80={ok:.3f} lost={lost.mean():.3f} maxrun={best/len(r):.3f} medL={np.median(r[:,2]):.1f} medE00={np.median(r[:,3]):.1f} medE76={np.median(r[:,4]):.1f} I3-13(ΔL≥10|ΔE76≥25)={i313:.3f}')
    return r
r=contour('core2_hot_mixing',label='C02 all')
bad=r[(r[:,2]<10)&(r[:,3]<10)]
print('  failing samples (pt):', [(round(A['core2_hot_mixing']['crop_pt'][0]+x/3,1),round(A['core2_hot_mixing']['crop_pt'][2]+y/3,1),round(dl,1),round(de,1)) for x,y,dl,de,_ in bad[:40]])
# basic_recipe per icon x ranges in 3x px
contour('basic_recipe',(0,200),'B01 lime pile')
contour('basic_recipe',(220,430),'B02 ash pile')
contour('basic_recipe',(470,630),'B03 stones')
contour('basic_recipe',(690,984),'B04 mold')
contour('basic_sources',(0,140),'B05 books')
contour('basic_sources',(320,520),'B06 core+lens')
contour('basic_sources',(640,895),'B07 colosseum mini')
contour('detail_d3_tower',label='D02 tower')
contour('detail_d1_seawater',label='D03 seawater')
