import numpy as np, json
from PIL import Image
from scipy import ndimage as ndi
from skimage import measure
idx=json.load(open('../nb_work/review_loop/obj_r11/assets_index.json'))
A={a['id']:a for a in idx['assets']}
a=A['water_tiber']
al=np.asarray(Image.open(a['files']['isolated_rgba']))[...,3]>128
m=ndi.binary_fill_holes(al)
dist_in=ndi.distance_transform_edt(m); dist_out=ndi.distance_transform_edt(~m)
print("mask frac",m.mean(), "dist_in max",dist_in.max(), "dist_out max", dist_out.max())
c=max(measure.find_contours(m.astype(float),0.5),key=len)
print(c[:3], c[-3:], len(c))
d=np.r_[0,np.cumsum(np.hypot(*np.diff(c,axis=0).T))]; print("len",d[-1])
