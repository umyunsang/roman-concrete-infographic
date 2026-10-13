import sys, json; sys.path.insert(0,'/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/oc2/lib')
from cl import *
from PIL import Image
import numpy as np
from scipy import ndimage as ndi
O='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/oc2/'
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
idx={a['id']:a for a in json.load(open(B+'obj_r11/assets_index.json'))['assets']}
idm=json.load(open(O+'idr/id_map.json'))
mo=np.array(Image.open(B+'r11/map_only_2x.png').convert('RGB')).astype(float)
fobj=np.array(Image.open(O+'idr/full_obj.png'))
H,W=mo.shape[:2]
ys=np.minimum((np.arange(H)*2.9992/2+0.5).astype(int),fobj.shape[0]-1); xs=np.minimum((np.arange(W)*2.9992/2+0.5).astype(int),fobj.shape[1]-1)
f2=fobj[ys][:,xs]
for aid in sys.argv[1:]:
  a=idx[aid]; bb=a['bbox_visible_final_pt']
  x0,x1,y0,y1=int(bb[0]*2)-12,int(bb[1]*2)+12,int(bb[2]*2)-12,int(bb[3]*2)+12
  sub=f2[y0:y1,x0:x1]; img=mo[y0:y1,x0:x1]
  mask=np.zeros(sub.shape[:2],bool)
  for o in a['objects']:
    c=idm['obj_ids'][o]; mask|=(sub[...,0]==c[0])&(sub[...,1]==c[1])&(sub[...,2]==c[2])&(sub[...,3]>127)
  L=lab(img)[...,0]
  di=ndi.distance_transform_edt(mask); do=ndi.distance_transform_edt(~mask)
  band=mask&(di<=1)
  inner_b=np.zeros_like(mask); inner_b[12:-12,12:-12]=True
  band&=inner_b
  Ri=mask&(di>=2)&(di<=4); Ro=(~mask)&(do>=2)&(do<=4)
  yy,xx=np.nonzero(band); h,w=mask.shape; dark=bright=n=0
  for y,x in zip(yy,xx):
    ya,yb,xa,xb=max(0,y-5),min(h,y+6),max(0,x-5),min(w,x+6)
    ri=Ri[ya:yb,xa:xb]; ro=Ro[ya:yb,xa:xb]
    if ri.sum()<2 or ro.sum()<2: continue
    n+=1; li=np.median(L[ya:yb,xa:xb][ri]); lo=np.median(L[ya:yb,xa:xb][ro]); lb=L[y,x]
    if lb<min(li,lo)-5: dark+=1
    elif lb>max(li,lo)+5: bright+=1
  print(aid,'band px',n,'darker',dark,'brighter',bright,'pct',round(100*(dark+bright)/max(n,1),1))
