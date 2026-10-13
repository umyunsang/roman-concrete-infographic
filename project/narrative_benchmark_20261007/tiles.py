import numpy as np
from PIL import Image, ImageCms
Image.MAX_IMAGE_PIXELS=None
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/'
t=[np.asarray(Image.open('pimg-%03d.jpg'%i)) for i in range(4)]
print([x.shape for x in t], Image.open('pimg-000.jpg').mode)
top=np.concatenate([t[0],t[1]],1); bot=np.concatenate([t[2],t[3]],1)
S=np.concatenate([top,bot],0).astype(np.int16); print('stitched', S.shape)
np.save('stitched_cmyk.npy', S.astype(np.uint8))
# compare with gs render @300
G=np.asarray(Image.open('cmyk300.tif')).astype(np.int16); print('gs300', G.shape)
# sample map area without text: region far from text e.g. px (2000:2300, 3000:3300)
for (y,x) in [(1500,1500),(3000,2500),(5000,4000),(6500,600)]:
    a=S[y:y+100,x:x+100]; g=G[y:y+100,x:x+100]
    print('pdf-img vs gs render at',(x,y),'mean abs per ch', np.abs(a-g).mean(axis=(0,1)), 'means', a.mean(axis=(0,1)).round(1), g.mean(axis=(0,1)).round(1))
# TAC on image
tac=S.sum(2)/255*100
print('IMAGE TAC max %.1f  p99.9 %.1f p99 %.1f  >300: %d px  >290: %d px'%(tac.max(), np.percentile(tac,99.9), np.percentile(tac,99), (tac>300).sum(), (tac>290).sum()))
print('K max', S[...,3].max()*100/255, 'C max', S[...,0].max()*100/255)
yy,xx=np.unravel_index(np.argmax(tac), tac.shape); print('max TAC at px', xx,yy, 'pt', xx*0.24,yy*0.24, S[yy,xx]*100/255)
# full render TAC (incl vectors)
tg=G.sum(2)/255*100
print('RENDER TAC max %.1f  >300: %d px; >305: %d'%(tg.max(), (tg>300).sum(), (tg>305).sum()))
# seams: column 2516|2517 and row 3543|3544
def seam_stat(arr, axis, idx):
    a=arr.astype(np.float32)
    if axis==1:
        d_seam=np.abs(a[:,idx]-a[:,idx-1]).mean()
        d_near=np.mean([np.abs(a[:,i]-a[:,i-1]).mean() for i in list(range(idx-6,idx-1))+list(range(idx+1,idx+6))])
    else:
        d_seam=np.abs(a[idx]-a[idx-1]).mean()
        d_near=np.mean([np.abs(a[i]-a[i-1]).mean() for i in list(range(idx-6,idx-1))+list(range(idx+1,idx+6))])
    return d_seam, d_near
print('seam col 2517 (stitched): %.3f vs neighbours %.3f'%seam_stat(S,1,2517))
print('seam row 3544 (stitched): %.3f vs neighbours %.3f'%seam_stat(S,0,3544))
# JPEG 8x8 block grid alignment at seam: 2517 not multiple of 8 -> check block boundary stats generally
print('gs render seam col (x=2517): %.3f vs %.3f'%seam_stat(G,1,2517))
print('gs render seam row (y=3544 from top -> 7088-3544):', seam_stat(G,0,G.shape[0]-3543), seam_stat(G,0,3544))
# compare to source v8_12 png converted to CMYK
src=Image.open(B+'v8_12_map_print_bleed_5033x7087.png'); print('src', src.mode, src.size)
pso=ImageCms.getOpenProfile(B+'PSOcoated_v3.icc'); srgb=ImageCms.createProfile('sRGB')
tr=ImageCms.buildTransform(srgb,pso,'RGB','CMYK',renderingIntent=1)
sc=np.asarray(ImageCms.applyTransform(src.convert('RGB'),tr)).astype(np.int16)
np.save('src_cmyk.npy', sc.astype(np.uint8))
e=np.abs(S-sc)
print('pdf image vs src->CMYK(lcms rel, no BPC) mean abs per ch', e.mean(axis=(0,1)).round(2), 'p99', np.percentile(e,99,axis=(0,1)), 'max', e.max(axis=(0,1)))
src11=Image.open(B+'v8_11_map_print_bleed_5033x7087.png')
sc11=np.asarray(ImageCms.applyTransform(src11.convert('RGB'),tr)).astype(np.int16)
e11=np.abs(S-sc11).sum(2)
print('vs v8_11 mean', e11.mean(), ' vs v8_12 mean', e.sum(2).mean())
d1112=np.abs(sc11-sc).sum(2)>30
ys,xs=np.nonzero(d1112); print('v8_11 vs v8_12 differing px', d1112.sum(), 'bbox pt', xs.min()*0.24, xs.max()*0.24, ys.min()*0.24, ys.max()*0.24)
m=d1112
print(' in that area: pdf matches v8_12 err', np.abs(S-sc).sum(2)[m].mean(), ' v8_11 err', e11[m].mean())
