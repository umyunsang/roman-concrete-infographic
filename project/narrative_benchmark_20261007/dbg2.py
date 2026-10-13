import numpy as np, json
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
idx=json.load(open('../nb_work/review_loop/obj_r11/assets_index.json'))
A={a['id']:a for a in idx['assets']}
full=np.asarray(Image.open('../nb_work/review_loop/obj_r11/full/full_map_pass.png').convert('RGB')).astype(float)/255
FS=full.shape[1]/1191.0
print(full.shape, FS)
a=A['water_tiber']; x0,x1,y0,y1=a['crop_pt']
im=Image.open(a['files']['isolated_rgba']); print(im.mode, im.size)
iso=np.asarray(im.convert('RGB')).astype(float)/255; al=np.asarray(im)[...,3]>128
for dx in range(-3,4):
  for dy in range(-3,4):
    X0=int(round(x0*FS))+dx; Y0=int(round(y0*FS))+dy
    fc=full[Y0:Y0+iso.shape[0], X0:X0+iso.shape[1]]
    h,w=fc.shape[:2]
    d=np.abs(fc-iso[:h,:w]).max(-1)[al[:h,:w]]
    if dx==0 and dy==0 or np.median(d)<0.02: print(dx,dy,"median diff %.3f, frac<0.04 %.2f"%(np.median(d),(d<0.04).mean()))
