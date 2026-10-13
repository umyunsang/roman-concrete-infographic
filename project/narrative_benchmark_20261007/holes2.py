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
PX=2.9992
R=ramp('#A9A69F')
for aid in sys.argv[1:]:
  a=idx[aid]; g=al[aid]
  ctx=np.array(Image.open(a['files']['context']).convert('RGB')).astype(float)
  sub=fobj[g['Y']:g['Y']+g['h'],g['X']:g['X']+g['w']]
  mask=np.zeros(sub.shape[:2],bool)
  for o in a['objects']:
    c=idm['obj_ids'][o]; mask|=(sub[...,0]==c[0])&(sub[...,1]==c[1])&(sub[...,2]==c[2])&(sub[...,3]>127)
  bb=a['bbox_visible_final_pt']; cp=a['crop_pt']
  x0=int((bb[0]-cp[0])*3); x1=int((bb[1]-cp[0])*3); y0=int((bb[2]-cp[2])*3); y1=int((bb[3]-cp[2])*3)
  reg=np.zeros_like(mask); reg[max(0,y0):y1,max(0,x0):x1]=True
  filled=ndi.binary_fill_holes(mask)
  inner_fill=ndi.binary_erosion(filled,iterations=3)  # exclude 1pt boundary band
  # within the filled road silhouette (excluding 1pt band), pixels far from basalt AND limestone ramps
  Rl=ramp('#C7BEAA')
  LAB=lab(ctx)
  sel=inner_fill&reg
  labs=LAB[sel]
  d1=np.concatenate([np.min(de00(labs[i:i+20000,None,:],R[None]),axis=1) for i in range(0,len(labs),20000)])
  d2=np.concatenate([np.min(de00(labs[i:i+20000,None,:],Rl[None]),axis=1) for i in range(0,len(labs),20000)])
  far=np.zeros_like(sel); far[sel]=np.minimum(d1,d2)>8
  lbl,n=ndi.label(far); sizes=ndi.sum(far,lbl,range(1,n+1)) if n else []
  big=[(i+1,s) for i,s in enumerate(sizes) if s>=9]
  print(aid,'far(>8 from both road ramps) px',int(far.sum()),'blobs>=1pt2',len(big))
  for i,s in sorted(big,key=lambda t:-t[1])[:10]:
    mm=lbl==i; cy,cx=ndi.center_of_mass(mm); px=ctx[mm]
    onroad=(mm&mask).sum()/mm.sum()
    print('   blob pt2',round(s/PX**2,1),'at pt',(round(cp[0]+cx/PX,1),round(cp[2]+cy/PX,1)),'median',hx(np.median(px,0)),'L*',round(float(np.median(lab(px)[:,0])),1),'frac on road-ID',round(float(onroad),2))
