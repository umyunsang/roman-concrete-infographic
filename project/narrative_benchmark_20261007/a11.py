import numpy as np
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS=None
RV='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
W='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/'
bg=Image.open(W+'v8_11_map_print_bleed_5033x7087.png').convert('RGB')
b2=bg.resize((2416,3402),Image.LANCZOS)
mo=np.asarray(Image.open(RV+'r9/map_only_2x.png').convert('RGB')).astype(np.float64)
best=None
for dy in range(14,21):
    for dx in range(14,21):
        c=np.asarray(b2.crop((dx,dy,dx+2382,dy+3368))).astype(np.float64)
        e=np.abs(c-mo).mean()
        if best is None or e<best[0]: best=(e,dx,dy)
print('best offset', best)
e,dx,dy=best
c=np.asarray(b2.crop((dx,dy,dx+2382,dy+3368))).astype(np.float64)
d=np.abs(c-mo).sum(axis=2)
print('mean diff %.2f  p99 %.1f  frac>60 %.5f'%(d.mean(), np.percentile(d,99), (d>60).mean()))
bs=40
g=(d>60)[:3360,:2360].reshape(84,bs,59,bs).sum(axis=(1,3))
idx=np.argsort(-g.ravel())[:10]
for i in idx:
    by,bx=np.unravel_index(i,g.shape); print(' block pt x %d-%d y %d-%d  n %d'%(bx*20,bx*20+20,by*20,by*20+20,g[by,bx]))
# mean color diff (global tone)
print('mean RGB print-bg', c.reshape(-1,3).mean(0), 'map_only', mo.reshape(-1,3).mean(0))
