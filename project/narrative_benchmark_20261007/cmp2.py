import numpy as np
from PIL import Image, ImageCms
Image.MAX_IMAGE_PIXELS=None
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/'
icc=B+'out/print/PSOcoated_v3.icc'
cm=Image.open('cmyk576.tif')
a=np.asarray(cm)
H,W=a.shape[:2]; print(a.shape)
# box downsample by 4 in CMYK (approx AA)
H4,W4=H//4,W//4
a4=a[:H4*4,:W4*4].reshape(H4,4,W4,4,4).astype(np.float32).mean(axis=(1,3))
cm144=Image.fromarray(np.round(a4).astype(np.uint8),'CMYK'); cm144.save('cmyk144aa.tif')
srgb=ImageCms.createProfile('sRGB'); pso=ImageCms.getOpenProfile(icc)
t_c2r=ImageCms.buildTransform(pso, srgb, 'CMYK','RGB', renderingIntent=1)
proof=ImageCms.applyTransform(cm144, t_c2r); proof.save('print_proof144aa.png')
P=np.asarray(proof).astype(np.float32)
D=np.asarray(Image.open('poster_proof144.png')).astype(np.float32)
D0=np.asarray(Image.open(B+'review_loop/r10/poster_2x.png').convert('RGB')).astype(np.float32)
R=np.asarray(Image.open('rgbpdf144aa.png').convert('RGB')).astype(np.float32)
h,w=D.shape[:2]
for off in [16,17,18]:
    print(off, np.abs(P[off:off+h,off:off+w]-D).mean(), 'rgb', np.abs(R[off:off+h,off:off+w]-D0).mean())
off=17
Pc=P[off:off+h,off:off+w]; Rc=R[off:off+h,off:off+w]
def blocks(diff, thr=90, fr=0.02, name=''):
    bs=20
    Hh,Ww=h//bs,w//bs
    blk=diff[:Hh*bs,:Ww*bs].reshape(Hh,bs,Ww,bs)
    frac=(blk>thr).mean(axis=(1,3))
    idx=np.argwhere(frac>fr)
    print(name,'blocks(10pt) >%.0f%% px diff>%d:'%(fr*100,thr), len(idx))
    for (i,j) in idx[np.argsort(-frac[idx[:,0],idx[:,1]])][:30]:
        print('  pt x %d-%d y %d-%d frac %.3f'%(j*10,(j+1)*10,i*10,(i+1)*10, frac[i,j]))
    return frac
d1=np.abs(Pc-D).sum(2); np.save('d_print_poster.npy', d1)
f1=blocks(d1, name='print vs poster')
d2=np.abs(Rc-D0).sum(2); np.save('d_rgb_poster.npy', d2)
f2=blocks(d2, name='rgbpdf vs poster')
print('global pct >60', (d1>60).mean()*100, (d2>60).mean()*100)
