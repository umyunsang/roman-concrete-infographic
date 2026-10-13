import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage import color
A='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/assets'
ids=['header_gate','fields_e','fields_nw','fields_s','fields_se','fields_sw','fields_w','trees_s','trees_se','tree_t_cypress','tree_t_pine_004','tree_t_pine_022']
G={}
for a in ids:
    im=Image.open(f'{A}/{a}/isolated_rgba.png')
    w,h=im.size; im2=im.resize((round(w*2/3),round(h*2/3)),Image.LANCZOS)
    arr=np.asarray(im2).astype(float)/255
    m=arr[...,3]>0.9
    m=ndi.binary_erosion(m,iterations=2)
    L=color.rgb2lab(arr[...,:3])[...,0]
    Ls=ndi.gaussian_filter(L,1.0)
    gy,gx=np.gradient(Ls)
    g=np.hypot(gx,gy)*2  # per pt
    G[a]=float(g[m].mean())
med=np.median(list(G.values()))
for a,v in G.items(): print(f'{a:18s} G={v:6.2f}  ratio to G-grade median {v/med:.2f}')
print('median',med)
