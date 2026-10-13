import numpy as np, json, warnings
warnings.filterwarnings('ignore')
from PIL import Image
from skimage import color
idx=json.load(open('../nb_work/review_loop/obj_r11/assets_index.json'))
A={a['id']:a for a in idx['assets']}
a=A['tree_t_cypress']; x0,x1,y0,y1=a['crop_pt']
arr=np.asarray(Image.open(a['files']['isolated_rgba'])).astype(float)/255
al=arr[...,3]>0.9; L=color.rgb2lab(arr[...,:3])[...,0]
for ypt in (875,885,895,902):
    r=int(round((ypt-y0)*3))
    cols=np.nonzero(al[r])[0]
    prof=L[r-1:r+2, cols].mean(0)
    d=np.diff(prof)
    print("y %d width %.1fpt L profile:"%(ypt,len(cols)/3), np.round(prof,1).tolist(), "max adj dL %.1f"%np.abs(d).max())
