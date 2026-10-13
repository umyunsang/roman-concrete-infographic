import json, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/oc_b5_r11')
from clr import *
Image.MAX_IMAGE_PIXELS = None
R = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
aid='shape_d3_section'; ox,oy=908,3625
ctx = np.array(Image.open(R+'assets/'+aid + '/context.png').convert('RGB')).astype(float)
rgba = np.array(Image.open(R+'assets/'+aid + '/isolated_rgba.png')).astype(float)
H,W=ctx.shape[:2]
mp = np.array(Image.open(R + 'full/full_map_pass.png').convert('RGB'))[oy:oy+H, ox:ox+W].astype(float)
a=rgba[...,3]
obj=a>127; band=obj&~ndi.binary_erosion(obj); full=a>=254
idx = ndi.distance_transform_edt(~full, return_distances=False, return_indices=True)
core = ctx[idx[0], idx[1]]
Lc=lab(ctx)[...,0]; Lcore=lab(core)[...,0]; Lm=lab(mp)[...,0]
lo=np.minimum(Lcore,Lm); hi=np.maximum(Lcore,Lm)
fl=band&((Lc<lo-5)|(Lc>hi+5))
ys,xs=np.nonzero(fl)
print('flagged',len(ys))
for y,x in list(zip(ys,xs))[::25]:
    print((y,x),'alpha',int(a[y,x]),'L',round(Lc[y,x],1),'core',round(Lcore[y,x],1),'map',round(Lm[y,x],1), 'coreidx',(idx[0][y,x],idx[1][y,x]))
# alternative: inside reference = median of ctx over full-alpha pixels within 2..4 px inside along obj (local window)
