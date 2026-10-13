import numpy as np, json
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
idx=json.load(open('../nb_work/review_loop/obj_r11/assets_index.json'))
A={a['id']:a for a in idx['assets']}
a=A['ground_land']
im=Image.open(a['files']['isolated_rgba']); arr=np.asarray(im).astype(float)/255
full=np.asarray(Image.open('../nb_work/review_loop/obj_r11/full/full_map_pass.png').convert('RGB')).astype(float)/255
h=min(arr.shape[0],full.shape[0]); w=min(arr.shape[1],full.shape[1])
vis=(arr[:h,:w,3]>0.5)&(np.abs(full[:h,:w]-arr[:h,:w,:3]).max(-1)<0.04)
# pit ellipse in pt (from iso view): centre ~ (588, 829), semi-axes ~ (188, 122)
yy,xx=np.mgrid[0:h,0:w]/3.0
cx,cy,ax,ay=588,829,190,124
e=((xx-cx)/ax)**2+((yy-cy)/ay)**2
ring=(e>0.85)&(e<1.08)
print("pit rim ring px", ring.sum(), "land visible in final:", (ring&vis).sum(), "(%.2f%%)"%(100*(ring&vis).sum()/ring.sum()))
inside=e<0.85
print("pit interior land visible px:", (inside&vis).sum())
