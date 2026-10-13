import numpy as np
from PIL import Image, ImageCms
Image.MAX_IMAGE_PIXELS=None
RV='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
W='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/'
poster=np.asarray(Image.open(RV+'r9/poster_2x.png').convert('RGB')).astype(np.int16)
maponly=np.asarray(Image.open(RV+'r9/map_only_2x.png').convert('RGB')).astype(np.int16)
print('poster', poster.shape, 'maponly', maponly.shape)
pv=np.asarray(Image.open('print_vec_144.tif')).astype(np.int16)
print('print vec', pv.shape)
bgfill=np.array([0.094,0.125,0.22,0.004])*255
pmask_full=(np.abs(pv-bgfill).sum(axis=2)>12)
sv=np.asarray(Image.open('screen_vec_144.png').convert('RGB')).astype(np.int16)
# screen bg fill color = most common
vals,counts=np.unique(sv.reshape(-1,3),axis=0,return_counts=True)
sfill=vals[counts.argmax()]; print('screen fill', sfill)
smask_full=(np.abs(sv-sfill).sum(axis=2)>12)
o=17
pm=pmask_full[o:o+3368,o:o+2382]; sm=smask_full[o:o+3368,o:o+2382]
tm=(np.abs(poster-maponly).sum(axis=2)>24)
print('ink px: print %d screen %d poster-text %d'%(pm.sum(), sm.sum(), tm.sum()))
inter=(pm&sm).sum(); print('IoU print vs screen vec %.4f'%(inter/(pm|sm).sum()))
inter2=(pm&tm).sum(); print('IoU print vec vs poster textmask %.4f'%(inter2/(pm|tm).sum()))
# outside trim content in vector masks
print('print vec ink outside trim:', pmask_full.sum()-pm.sum(), ' screen vec ink outside trim:', smask_full.sum()-sm.sum())
np.save('pm144.npy',pm); np.save('tm144.npy',tm); np.save('sm144.npy',sm)
# differences blockwise: elements in poster textmask not in print vec (dilate pm by 2)
def dil(m,n):
    for _ in range(n): m = m | np.roll(m,1,0) | np.roll(m,-1,0) | np.roll(m,1,1) | np.roll(m,-1,1)
    return m
miss = tm & ~dil(pm,3)
extra = pm & ~dil(tm,3)
print('poster-text px not covered by print vectors (3px tol):', miss.sum(), ' print vec px not in poster textmask:', extra.sum())
bs=40
for name,m in (('MISS',miss),('EXTRA',extra)):
    H,Wd=m.shape
    g=m[:H//bs*bs,:Wd//bs*bs].reshape(H//bs,bs,Wd//bs,bs).sum(axis=(1,3))
    idx=np.argsort(-g.ravel())[:10]
    for i in idx:
        by,bx=np.unravel_index(i,g.shape)
        if g[by,bx]<15: break
        print(name,'block pt x %d-%d y %d-%d count %d'%(bx*bs/2,(bx+1)*bs/2,by*bs/2,(by+1)*bs/2,g[by,bx]))
