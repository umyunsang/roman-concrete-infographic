import numpy as np
from PIL import Image, ImageFilter
Image.MAX_IMAGE_PIXELS=None
RV='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
W='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/'
bg=Image.open(W+'v8_11_map_print_bleed_5033x7087.png').convert('RGB')
b1=bg.resize((1208,1701),Image.LANCZOS).crop((8,8,8+1191,8+1684))  # approx 0.5pt off
b1=bg.resize((2416,3402),Image.LANCZOS).crop((17,17,17+2382,17+3368)).resize((1191,1684),Image.BOX)
mo=Image.open(RV+'r9/map_only_2x.png').convert('RGB').resize((1191,1684),Image.BOX)
a=np.asarray(b1.filter(ImageFilter.GaussianBlur(2))).astype(float); b=np.asarray(mo.filter(ImageFilter.GaussianBlur(2))).astype(float)
d=np.abs(a-b).sum(axis=2)
print('blurred diff mean %.2f p99 %.1f p99.9 %.1f max %.1f'%(d.mean(),np.percentile(d,99),np.percentile(d,99.9),d.max()))
ys,xs=np.where(d>40); print('n>40', len(ys))
if len(ys):
    bs=20; g=np.zeros((1684//bs+1,1191//bs+1),int)
    for y,x in zip(ys,xs): g[y//bs,x//bs]+=1
    idx=np.argsort(-g.ravel())[:8]
    for i in idx:
        by,bx=np.unravel_index(i,g.shape)
        if g[by,bx]: print(' block pt x %d y %d n %d'%(bx*bs,by*bs,g[by,bx]))
