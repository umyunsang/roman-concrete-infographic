import numpy as np, json
from PIL import Image
idx=json.load(open('../nb_work/review_loop/obj_r11/assets_index.json'))
A={a['id']:a for a in idx['assets']}
a=A['road_core_se']; x0,x1,y0,y1=a['crop_pt']
al=np.asarray(Image.open(a['files']['isolated_rgba']))[...,3]>128
yy,xx=np.mgrid[0:al.shape[0],0:al.shape[1]]
X=x0+xx/3; Y=y0+yy/3
# wedge beyond landing to the right/up of the right curb end: x>953.9
m=al&(X>953.9)
print("area beyond x>953.9: %.1f pt2, x %.1f-%.1f y %.1f-%.1f"%(m.sum()/9,X[m].min(),X[m].max(),Y[m].min(),Y[m].max()))
# tab above disk: y<869.5 region near x 940-950
m2=al&(Y<869.0)&(X>936)&(X<952)
print("tab above landing far edge: %.1f pt2, x %.1f-%.1f y %.1f-%.1f"%(m2.sum()/9,X[m2].min(),X[m2].max(),Y[m2].min(),Y[m2].max()))
