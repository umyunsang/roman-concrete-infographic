import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage import color
RL='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
A={a['id']:a for a in json.load(open(RL+'assets_index.json'))['assets']}
S=3
def G(aid,sel=None):
    a=A[aid]; rgba=np.asarray(Image.open(a['files']['isolated_rgba']).convert('RGBA')).astype(float)/255
    m=rgba[...,3]>0.5
    if sel: mm=np.zeros_like(m); mm[:,sel[0]:sel[1]]=True; m&=mm
    L=color.rgb2lab(rgba[...,:3])[...,0]; Ls=ndi.gaussian_filter(L,0.5*S)
    gy,gx=np.gradient(Ls); g=np.hypot(gx,gy)*S  # L* per pt
    inner=ndi.binary_erosion(m,iterations=int(1*S))  # exclude silhouette edge 1pt
    return float(g[inner].mean())
ids={'C':['core1_modern_building','core2_hot_mixing','detail_core3_lime_specimen','detail_core4_three_cubes','support_core5_lab'],'D':['detail_d1_seawater','detail_d2_making','detail_d3_tower']}
for k,v in ids.items():
    vals={i:round(G(i),2) for i in v}; print(k,vals,'median',np.median(list(vals.values())))
b={'B01':G('basic_recipe',(0,200)),'B02':G('basic_recipe',(220,430)),'B03':G('basic_recipe',(470,630)),'B04':G('basic_recipe',(690,984)),'B05':G('basic_sources',(0,140)),'B06':G('basic_sources',(320,520)),'B07':G('basic_sources',(640,895))}
print('B',{k:round(v,2) for k,v in b.items()},'median',round(float(np.median(list(b.values()))),2))
