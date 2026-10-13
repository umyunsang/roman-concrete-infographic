import numpy as np, json
from PIL import Image
from scipy import ndimage as ndi
from skimage import measure
Image.MAX_IMAGE_PIXELS=None
idx=json.load(open('../nb_work/review_loop/obj_r11/assets_index.json'))
A={a['id']:a for a in idx['assets']}
for aid in ['ground_land','water_sea','water_tiber','road_ostiensis','road_appia','road_core_se','road_core_se_2','trees_s','trees_se','tree_t_pine_004','tree_t_pine_022','tree_t_cypress']:
    a=A[aid]; x0,x1,y0,y1=a['crop_pt']
    al=np.asarray(Image.open(a['files']['isolated_rgba']))[...,3]>128
    holes=ndi.binary_fill_holes(al)&~al
    lbl=measure.label(holes)
    regs=[p for p in measure.regionprops(lbl) if p.area>=9]
    # components of the mask (islands)
    l2=measure.label(al,connectivity=2); n=l2.max()
    sizes=np.bincount(l2.ravel())[1:]
    big=sizes.max()
    small=[(s/9) for s in sizes if s<big]
    print(aid,"holes>=1pt2:",len(regs), [("%.1fpt2 @(%.0f,%.0f)"%(p.area/9,x0+p.centroid[1]/3,y0+p.centroid[0]/3)) for p in sorted(regs,key=lambda p:-p.area)[:8]], "| islands:",n,"main %.0fpt2"%(big/9),"others>=1pt2:",sum(1 for s in small if s>=1))
