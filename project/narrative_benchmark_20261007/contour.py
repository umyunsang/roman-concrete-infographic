import sys, json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage import color, measure
A='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx=json.load(open(A+'assets_index.json'))
ids=sys.argv[1:]
S=3
for a in idx['assets']:
    if a['id'] not in ids: continue
    al=np.asarray(Image.open(a['files']['isolated_rgba']))[...,3]
    m=al>=128
    m=ndi.binary_fill_holes(m)
    ctx=np.asarray(Image.open(a['files']['context']).convert('RGB')).astype(float)/255
    lab=color.rgb2lab(ctx)
    din=ndi.distance_transform_edt(m); dout=ndi.distance_transform_edt(~m)
    H,W=m.shape
    cs=measure.find_contours(m.astype(float),0.5)
    samples=[]
    for c in cs:
        # resample every 1pt (3px) along contour
        d=np.r_[0,np.cumsum(np.hypot(*np.diff(c,axis=0).T))]
        if d[-1]<9: continue
        for s in np.arange(0,d[-1],3.0):
            i=np.searchsorted(d,s); i=min(i,len(c)-1); y,x=c[i]
            y0,y1,x0,x1=int(max(0,y-12)),int(min(H,y+13)),int(max(0,x-12)),int(min(W,x+13))
            # skip samples at crop border (asset touching crop edge)
            if y<6 or x<6 or y>H-7 or x>W-7: continue
            yy,xx=np.mgrid[y0:y1,x0:x1]; rr=np.hypot(yy-y,xx-x)<=12
            sub_in=m[y0:y1,x0:x1]&(din[y0:y1,x0:x1]>=3)&(din[y0:y1,x0:x1]<=9)&rr
            sub_out=(~m[y0:y1,x0:x1])&(dout[y0:y1,x0:x1]>=3)&(dout[y0:y1,x0:x1]<=9)&rr
            if sub_in.sum()<5 or sub_out.sum()<5: continue
            li=np.median(lab[y0:y1,x0:x1][sub_in],axis=0); lo=np.median(lab[y0:y1,x0:x1][sub_out],axis=0)
            dL=abs(li[0]-lo[0]); dE=float(color.deltaE_ciede2000(li[None,None],lo[None,None])[0,0]); dE76=float(np.linalg.norm(li-lo))
            samples.append((y,x,dL,dE,dE76))
    S_=np.array(samples)
    ok=(S_[:,2]>=10)|(S_[:,3]>=10)
    lost=(S_[:,2]<5)&(S_[:,3]<5)
    i313=(S_[:,2]>=10)|(S_[:,4]>=25)
    # longest run of lost (in sample order)
    run=0; best=0
    for v in lost:
        run=run+1 if v else 0; best=max(best,run)
    print('%-20s n=%d  pass(dL>=10|dE>=10)=%.1f%%  lost=%.1f%%  longest lost run=%d (%.1f%%)  I3-13 pass=%.1f%%  median dL=%.1f dE00=%.1f'%(a['id'],len(S_),ok.mean()*100,lost.mean()*100,best,best/len(S_)*100,i313.mean()*100,np.median(S_[:,2]),np.median(S_[:,3])))
    np.save('contour_%s.npy'%a['id'],S_)
