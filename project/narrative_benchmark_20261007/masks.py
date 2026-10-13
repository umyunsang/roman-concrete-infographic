import json, numpy as np
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
idx=json.load(open(R+'obj_r11/assets_index.json'))
H,W=3367,2381; S=W/1191.0
M={}
for a in idx['assets']:
    al=np.asarray(Image.open(a['files']['isolated_rgba']))[...,3]
    x0,x1,y0,y1=a['crop_pt']
    # place into poster grid at 2px/pt
    gx0,gy0=int(round(x0*S)),int(round(y0*S)); gw,gh=int(round((x1-x0)*S)),int(round((y1-y0)*S))
    im=Image.fromarray(al).resize((gw,gh),Image.BILINEAR)
    m=np.zeros((H,W),bool)
    sub=np.asarray(im)>=128
    ya,xa=max(gy0,0),max(gx0,0); yb,xb=min(gy0+gh,H),min(gx0+gw,W)
    m[ya:yb,xa:xb]=sub[ya-gy0:yb-gy0, xa-gx0:xb-gx0]
    M[a['id']]=m
np.savez_compressed('M_all.npz',**M)
print(len(M))
