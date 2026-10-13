import numpy as np, json
from PIL import Image
from scipy import ndimage as ndi
from skimage import measure
idx=json.load(open('../nb_work/review_loop/obj_r11/assets_index.json'))
A={a['id']:a for a in idx['assets']}
for aid in ['water_tiber','trees_s','trees_se']:
    a=A[aid]
    al=np.asarray(Image.open(a['files']['isolated_rgba']))[...,3]>128
    m=ndi.binary_fill_holes(al)
    cont=measure.find_contours(m.astype(float),0.5)
    L=[len(c) for c in cont]
    print(aid, al.shape, "ncont",len(cont),"lens top",sorted(L)[-5:], "sum perim px", sum(np.hypot(*np.diff(c,axis=0).T).sum() for c in cont if len(c)>=30))
