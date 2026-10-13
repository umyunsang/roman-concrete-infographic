import numpy as np, sys
from PIL import Image, ImageCms
Image.MAX_IMAGE_PIXELS=None
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/'
icc=B+'out/print/PSOcoated_v3.icc'
cm=Image.open('cmyk144.tif'); print(cm.mode, cm.size)
srgb=ImageCms.createProfile('sRGB'); pso=ImageCms.getOpenProfile(icc)
t_c2r=ImageCms.buildTransform(pso, srgb, 'CMYK','RGB', renderingIntent=1)
t_r2c=ImageCms.buildTransform(srgb, pso, 'RGB','CMYK', renderingIntent=1)
proof=ImageCms.applyTransform(cm, t_c2r); proof.save('print_proof144.png')
P=np.asarray(proof).astype(np.float32)
d=Image.open(B+'review_loop/r10/poster_2x.png').convert('RGB'); print('poster', d.size)
dp=ImageCms.applyTransform(ImageCms.applyTransform(d,t_r2c),t_c2r); dp.save('poster_proof144.png')
D=np.asarray(dp).astype(np.float32)
rp=np.asarray(Image.open('rgbpdf144.png').convert('RGB')).astype(np.float32); print('rgbpdf', rp.shape)
h,w=D.shape[:2]
for off in [16,17,18]:
    Pc=P[off:off+h, off:off+w]
    print(off, 'print vs poster(proofed) mean abs', np.abs(Pc-D).mean())
off=17
Pc=P[off:off+h, off:off+w]
Rc=rp[off:off+h, off:off+w]
D0=np.asarray(d).astype(np.float32)
print('rgbpdf vs poster mean abs', np.abs(Rc-D0).mean())
diff=np.abs(Pc-D).sum(2)
np.save('diff_print_poster.npy', diff)
print('diff pct>60:', (diff>60).mean()*100, 'pct>120', (diff>120).mean()*100)
# block map 20pt blocks (40px)
bs=40
H,W=h//bs, w//bs
blk=diff[:H*bs,:W*bs].reshape(H,bs,W,bs)
frac=(blk>90).mean(axis=(1,3))
idx=np.argwhere(frac>0.03)
print('blocks with >3% px diff>90:', len(idx))
for (i,j) in idx[np.argsort(-frac[idx[:,0],idx[:,1]])][:40]:
    print('  pt x %d-%d y %d-%d frac %.3f'%(j*20,(j+1)*20,i*20,(i+1)*20, frac[i,j]))
diff2=np.abs(Rc-D0).sum(2)
blk=diff2[:H*bs,:W*bs].reshape(H,bs,W,bs); frac2=(blk>90).mean(axis=(1,3))
idx=np.argwhere(frac2>0.03); print('RGB pdf vs poster blocks >3%:', len(idx))
for (i,j) in idx[np.argsort(-frac2[idx[:,0],idx[:,1]])][:20]:
    print('  pt x %d-%d y %d-%d frac %.3f'%(j*20,(j+1)*20,i*20,(i+1)*20, frac2[i,j]))
