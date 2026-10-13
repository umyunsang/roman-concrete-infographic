import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage import color, morphology
A='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx=json.load(open(A+'assets_index.json'))
out={}
for a in idx['assets']:
    im=np.asarray(Image.open(a['files']['isolated_rgba'])).astype(float)
    m=im[...,3]>=250
    m=morphology.erosion(m, morphology.disk(3))  # exclude 1pt rim
    if m.sum()<50: continue
    L=color.rgb2lab(im[...,:3]/255)[...,0]
    Ls=ndi.gaussian_filter(L,1.5)   # sigma 0.5pt at 3px/pt
    gy,gx=np.gradient(Ls)
    G=np.hypot(gx,gy)*3  # per pt
    out[a['id']]=float(G[m].mean())
json.dump(out,open('gnoise.json','w'),indent=0)
for k,v in sorted(out.items(), key=lambda kv: kv[1]): print('%-28s %.2f'%(k,v))
