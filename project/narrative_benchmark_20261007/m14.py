import numpy as np, json
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
idx=json.load(open('../nb_work/review_loop/obj_r11/assets_index.json'))
pts=[(58,1370),(62,1373),(70,1375),(92,1385),(95,1387)]
for a in idx['assets']:
    x0,x1,y0,y1=a['crop_pt']
    hits=[]
    for (x,y) in pts:
        if x0<=x<x1 and y0<=y<y1:
            im=Image.open(a['files']['isolated_rgba'])
            arr=np.asarray(im)
            c=int((x-x0)*3); r=int((y-y0)*3)
            win=arr[max(0,r-6):r+7, max(0,c-6):c+7,3]
            if (win>128).any(): hits.append((x,y,int((win>128).mean()*100)))
    if hits: print(a['id'],hits)
