import numpy as np, json
from PIL import Image, ImageCms, ImageFilter
Image.MAX_IMAGE_PIXELS=None
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/'
S=np.load('S_inv.npy')
G=np.asarray(Image.open('cmyk300.tif'))[1:1+S.shape[0]]
diff=np.abs(G.astype(np.int16)-S.astype(np.int16)).sum(2)
vec=diff>0
print('vector px', vec.sum())
pso=ImageCms.getOpenProfile(B+'out/print/PSOcoated_v3.icc'); srgb=ImageCms.createProfile('sRGB')
tN=ImageCms.buildTransform(pso,srgb,'CMYK','RGB',renderingIntent=1)
tB=ImageCms.buildTransform(pso,srgb,'CMYK','RGB',renderingIntent=1,flags=ImageCms.Flags.BLACKPOINTCOMPENSATION)
def conv(arr, t):
    im=Image.fromarray(arr.reshape(1,-1,4).astype(np.uint8),'CMYK')
    return np.asarray(ImageCms.applyTransform(im,t)).reshape(-1,3).astype(np.float64)
def lum(rgb):
    c=rgb/255.0; c=np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4)
    return c@np.array([0.2126,0.7152,0.0722])
def cr(a,b):
    hi=np.maximum(a,b); lo=np.minimum(a,b); return (hi+0.05)/(lo+0.05)
spec=json.load(open(B+'review_loop/text_spec_r10.json'))['texts']
f=300/72
res=[]
from scipy import ndimage
for t in spec:
    tid,(x,y,w,h),rot,al,segs=t
    pad=3 if rot==0 else 6
    x0=int((x+8.5-pad)*f); y0=int((y+8.5-pad)*f); x1=int((x+w+8.5+pad)*f); y1=int((y+h+8.5+pad)*f)
    m=vec[y0:y1,x0:x1]
    if m.sum()==0: res.append((tid,'NO INK')); continue
    g=G[y0:y1,x0:x1]; s=S[y0:y1,x0:x1]
    # distinct solid colors in mask
    cols=g[m]
    keys,counts=np.unique(cols,axis=0,return_counts=True)
    order=np.argsort(-counts)
    sizes=sorted(set(sg[2] for sg in segs))
    out=[]
    for k in order[:3]:
        if counts[k]<0.08*m.sum(): continue
        km=(g==keys[k]).all(2)&m
        near=ndimage.binary_dilation(km,iterations=6)
        bgpx=s[near]
        tc=keys[k][None,:]
        for tag,tt in (('noBPC',tN),('BPC',tB)):
            trgb=conv(tc,tt); brgb=conv(bgpx,tt)
            Lt=lum(trgb)[0]; Lb=lum(brgb)
            if Lt<np.median(Lb): worst=np.percentile(Lb,2)
            else: worst=np.percentile(Lb,98)
            out.append((tag, tuple(np.round(keys[k]/2.55,1)), round(float(cr(Lt,np.median(Lb))),2), round(float(cr(Lt,worst)),2)))
    res.append((tid, sizes, ''.join(s_[0] for s_ in segs)[:14].replace('\n','/'), out))
json.dump([list(map(str,r)) for r in res], open('contrast_out.json','w'), ensure_ascii=False)
low=[]
for r in res:
    if len(r)<4: print(r); continue
    tid,sizes,txt,out=r
    for o in out:
        if o[0]=='noBPC':
            print(tid, sizes, txt, o[1], 'median %.2f worst2%% %.2f'%(o[2],o[3]), ' | BPC', [p for p in out if p[0]=='BPC' and p[1]==o[1]][0][2:])
