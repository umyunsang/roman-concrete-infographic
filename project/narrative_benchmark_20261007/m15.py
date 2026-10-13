import numpy as np, json, warnings
warnings.filterwarnings('ignore')
from PIL import Image
from scipy import ndimage as ndi
from skimage import morphology, measure
idx=json.load(open('../nb_work/review_loop/obj_r11/assets_index.json'))
A={a['id']:a for a in idx['assets']}
S=3
for aid in ['road_core_se','road_core_se_2','road_appia','road_ostiensis','tree_t_cypress','tree_t_pine_004','tree_t_pine_022','trees_s','trees_se','water_tiber']:
    a=A[aid]; x0,x1,y0,y1=a['crop_pt']
    al=np.asarray(Image.open(a['files']['isolated_rgba']))[...,3]>128
    f=ndi.binary_fill_holes(al)
    r=f&~morphology.binary_opening(f,morphology.disk(3))   # radius 1pt at 3px/pt
    regs=[p for p in measure.regionprops(measure.label(r,connectivity=2)) if p.major_axis_length/S>=3]
    out=[]
    for p in regs:
        r0,c0,r1,c1=p.bbox
        out.append("len %.1f w %.1f @x %.1f-%.1f y %.1f-%.1f"%(p.major_axis_length/S,p.minor_axis_length/S,x0+c0/S,x0+c1/S,y0+r0/S,y0+r1/S))
    print(aid,"fin candidates:",len(regs)); [print("   ",o) for o in out[:12]]
