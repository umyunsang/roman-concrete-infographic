import numpy as np, json
from PIL import Image, ImageCms
from scipy import ndimage
Image.MAX_IMAGE_PIXELS=None
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/'
S=np.load('S_inv.npy'); G=np.asarray(Image.open('cmyk300.tif'))[1:1+S.shape[0]]
vec=np.abs(G.astype(np.int16)-S.astype(np.int16)).sum(2)>0
pso=ImageCms.getOpenProfile(B+'out/print/PSOcoated_v3.icc'); srgb=ImageCms.createProfile('sRGB')
tN=ImageCms.buildTransform(pso,srgb,'CMYK','RGB',renderingIntent=1)
def conv(arr):
    im=Image.fromarray(arr.reshape(1,-1,4).astype(np.uint8),'CMYK')
    return np.asarray(ImageCms.applyTransform(im,tN)).reshape(-1,3).astype(np.float64)
def Ys(rgb):
    c=rgb/255.0; Y=0.2126729*c[...,0]**2.4+0.7151522*c[...,1]**2.4+0.0721750*c[...,2]**2.4
    return np.where(Y<0.022, Y+(0.022-Y)**1.414, Y)
def apca(Yt,Yb):
    if Yb>Yt: S=(Yb**0.56-Yt**0.57)*1.14; return 0 if abs(S)<0.1 else (S-0.027)*100
    S=(Yb**0.65-Yt**0.62)*1.14; return 0 if abs(S)<0.1 else (S+0.027)*100
spec=json.load(open(B+'review_loop/text_spec_r10.json'))['texts']
f=300/72; rows=[]
body={'790:148','790:154','790:160','790:166','790:172'}
for tid,(x,y,w,h),rot,al,segs in spec:
    pad=3 if rot==0 else 6
    x0=int((x+8.5-pad)*f); y0=int((y+8.5-pad)*f); x1=int((x+w+8.5+pad)*f); y1=int((y+h+8.5+pad)*f)
    m=vec[y0:y1,x0:x1]; g=G[y0:y1,x0:x1]; s=S[y0:y1,x0:x1]
    keys,counts=np.unique(g[m],axis=0,return_counts=True)
    for k in np.argsort(-counts)[:2]:
        if counts[k]<0.08*m.sum(): continue
        km=(g==keys[k]).all(2)&m
        near=ndimage.binary_dilation(km,iterations=6)&~ndimage.binary_dilation(km,iterations=2)
        Yt=Ys(conv(keys[k][None,:]))[0]; Yb=np.median(Ys(conv(s[near])))
        sz=max(sg[2] for sg in segs)
        rows.append((abs(apca(Yt,Yb)), tid, sz, tuple((keys[k]/2.55).round(0)), 'body' if tid in body else ('large' if sz>=70 else 'content')))
rows.sort()
for r in rows[:12]: print('Lc %.1f %s %spt %s %s'%r)
print('min body', min(r[0] for r in rows if r[4]=='body'))
