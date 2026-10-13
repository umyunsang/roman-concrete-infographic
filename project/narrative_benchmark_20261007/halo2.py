import sys, json; sys.path.insert(0,'/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/oc2/lib')
from cl import *
from PIL import Image
import numpy as np
from scipy import ndimage as ndi
O='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/oc2/'
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx={a['id']:a for a in json.load(open(B+'assets_index.json'))['assets']}
al=json.load(open(O+'align.json'))
for aid in sys.argv[1:]:
  a=idx[aid]; g=al[aid]
  iso=np.array(Image.open(a['files']['isolated']).convert('RGB')).astype(float)
  sub=np.array(Image.open(O+'idr/iso_mat_'+aid+'.png'))[g['Y']:g['Y']+g['h'],g['X']:g['X']+g['w']]
  mask=sub[...,3]>127
  L=lab(iso)[...,0]
  di=ndi.distance_transform_edt(mask); do=ndi.distance_transform_edt(~mask)
  # outer silhouette only: band on both sides of boundary, 1.5px
  band=(mask&(di<=1.5))|((~mask)&(do<=1.0))
  Ri=mask&(di>=3)&(di<=6); Ro=(~mask)&(do>=3)&(do<=6)
  ys,xs=np.nonzero(band); H,W=mask.shape; dark=bright=n=0
  for y,x in zip(ys,xs):
    ya,yb,xa,xb=max(0,y-8),min(H,y+9),max(0,x-8),min(W,x+9)
    ri=Ri[ya:yb,xa:xb]; ro=Ro[ya:yb,xa:xb]
    if ri.sum()<3 or ro.sum()<3: continue
    n+=1; li=np.median(L[ya:yb,xa:xb][ri]); lo=np.median(L[ya:yb,xa:xb][ro]); lb=L[y,x]
    if lb<min(li,lo)-5: dark+=1
    elif lb>max(li,lo)+5: bright+=1
  print(aid,'band px',n,'darker',dark,'brighter',bright,'pct',round(100*(dark+bright)/max(n,1),1))
