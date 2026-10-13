import numpy as np, json, warnings, sys
warnings.filterwarnings('ignore')
from PIL import Image
from scipy import ndimage as ndi
from skimage import color
Image.MAX_IMAGE_PIXELS=None
idx=json.load(open('../nb_work/review_loop/obj_r11/assets_index.json'))
A={a['id']:a for a in idx['assets']}
full=np.asarray(Image.open('../nb_work/review_loop/obj_r11/full/full_map_pass.png').convert('RGB')).astype(float)/255
for aid in sys.argv[1:]:
    a=A[aid]; x0,x1,y0,y1=a['crop_pt']
    im=Image.open(a['files']['isolated_rgba']); arr=np.asarray(im).astype(float)/255
    X0=int(round(x0*3)); Y0=int(round(y0*3))
    fc=full[Y0:Y0+arr.shape[0], X0:X0+arr.shape[1]]; h,w=fc.shape[:2]; arr=arr[:h,:w]
    vis=(arr[...,3]>0.5)&(np.abs(fc-arr[...,:3]).max(-1)<0.04)
    m=ndi.binary_fill_holes(ndi.binary_opening(vis))
    di=ndi.distance_transform_edt(m)/3; do=ndi.distance_transform_edt(~m)/3
    lab=color.rgb2lab(fc)
    li=np.median(lab[(di>=2)&(di<=10)],axis=0); lo=np.median(lab[(do>=2)&(do<=10)],axis=0)
    print(aid,"in L*a*b* %s out %s dL*=%.1f dE76=%.1f"%(np.round(li,1),np.round(lo,1),abs(li[0]-lo[0]),np.linalg.norm(li-lo)))
