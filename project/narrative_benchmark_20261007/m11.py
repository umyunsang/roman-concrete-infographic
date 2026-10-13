import numpy as np, json, warnings
warnings.filterwarnings('ignore')
from PIL import Image
from scipy import ndimage as ndi
from skimage import color
Image.MAX_IMAGE_PIXELS=None
idx=json.load(open('../nb_work/review_loop/obj_r11/assets_index.json'))
out={}
for a in idx['assets']:
    im=Image.open(a['files']['isolated_rgba']); arr=np.asarray(im).astype(float)/255
    al=arr[...,3]>0.5
    if al.sum()<50: continue
    # downscale huge ones by sampling a window for speed
    L=color.rgb2lab(arr[...,:3])[...,0]
    Ls=ndi.gaussian_filter(L,1.5)
    gy,gx=np.gradient(Ls); g=np.hypot(gx,gy)*3  # per pt
    m=ndi.binary_erosion(al,iterations=3)
    if m.sum()<20: m=al
    out[a['id']]=float(g[m].mean())
for k,v in sorted(out.items(), key=lambda t:t[1]): print("%-28s G=%.2f"%(k,v))
json.dump(out,open('G_all.json','w'))
