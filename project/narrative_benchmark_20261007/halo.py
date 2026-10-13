import sys, json; sys.path.insert(0,'/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/oc2/lib')
from cl import *
from PIL import Image
import numpy as np
from scipy import ndimage as ndi
O='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/oc2/'
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx={a['id']:a for a in json.load(open(B+'assets_index.json'))['assets']}
al=json.load(open(O+'align.json')); idm=json.load(open(O+'idr/id_map.json'))
fobj=np.array(Image.open(O+'idr/full_obj.png'))
for aid in sys.argv[1:]:
  a=idx[aid]; g=al[aid]
  ctx=np.array(Image.open(a['files']['context']).convert('RGB')).astype(float)
  sub=fobj[g['Y']:g['Y']+g['h'],g['X']:g['X']+g['w']]
  mask=np.zeros(sub.shape[:2],bool)
  for o in a['objects']:
    c=idm['obj_ids'][o]; mask|=(sub[...,0]==c[0])&(sub[...,1]==c[1])&(sub[...,2]==c[2])&(sub[...,3]>127)
  # restrict roads to region bbox
  bb=a['bbox_visible_final_pt']; cp=a['crop_pt']
  x0=int((bb[0]-cp[0])*3); x1=int((bb[1]-cp[0])*3); y0=int((bb[2]-cp[2])*3); y1=int((bb[3]-cp[2])*3)
  reg=np.zeros_like(mask); reg[max(0,y0):y1,max(0,x0):x1]=True
  L=lab(ctx)[...,0]; OK=oklch(ctx)
  di=ndi.distance_transform_edt(mask); do=ndi.distance_transform_edt(~mask)
  band=mask&(di<=1.5)&reg
  Ri=mask&(di>=3)&(di<=6); Ro=(~mask)&(do>=3)&(do<=6)
  ys,xs=np.nonzero(band); H,W=mask.shape; halo=0; n=0
  for y,x in zip(ys,xs):
    ya,yb,xa,xb=max(0,y-8),min(H,y+9),max(0,x-8),min(W,x+9)
    ri=Ri[ya:yb,xa:xb]; ro=Ro[ya:yb,xa:xb]
    if ri.sum()<3 or ro.sum()<3: continue
    n+=1
    li=np.median(L[ya:yb,xa:xb][ri]); lo=np.median(L[ya:yb,xa:xb][ro])
    lb=L[y,x]; out=(lb<min(li,lo)-5) or (lb>max(li,lo)+5)
    if not out:
      ci=np.median(OK[ya:yb,xa:xb,1][ri]); co=np.median(OK[ya:yb,xa:xb,1][ro]); cb=OK[y,x,1]
      if cb>=0.02 and ci>=0.02 and co>=0.02:
        hi=np.median(OK[ya:yb,xa:xb,2][ri]); ho=np.median(OK[ya:yb,xa:xb,2][ro]); hb=OK[y,x,2]
        dd=lambda p,q: abs((p-q+180)%360-180)
        out = dd(hb,hi)>30 and dd(hb,ho)>30
    halo+=out
  print(aid,'boundary px',n,'halo px',halo,'pct',round(100*halo/max(n,1),2))
