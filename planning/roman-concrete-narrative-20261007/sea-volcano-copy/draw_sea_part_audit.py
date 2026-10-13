from pathlib import Path
import runpy, json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
p=Path(__file__).parent
h=runpy.run_path(str(p/'sea_object_parts.py'))
a=np.load(p/'sea-object-geometry.npz')
img=Image.new('RGB',(2400,2550),(246,243,235));d=ImageDraw.Draw(img)
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',28)
small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',23)
d.text((40,24),'Original v8 geometry: selected seaside surface parts (read-only audit)',fill='#243E47',font=font)
for j,(role,hx) in enumerate(h['PALETTE'].items()):
 x=40+j*390;d.rectangle((x,75,x+30,105),fill=hx);d.text((x+42,78),role,fill='#243E47',font=small)
for idx,name in enumerate(h['EXPECTED']):
 row,col=divmod(idx,2);xo=col*1200;yo=150+row*1200
 v=a[name+'_vertices'];c=a[name+'_centers'];n=a[name+'_normals'];ar=a[name+'_areas'];st=a[name+'_starts'];ct=a[name+'_totals'];loops=a[name+'_loops'];r=h['select_arrays'](name,c,n,ar)
 labels=np.full(len(c),r['default'],dtype=object)
 for role,faces in r['faces'].items():labels[faces]=role
 ev=np.deg2rad(25);az=np.deg2rad(-55)
 direction=np.array([np.cos(ev)*np.cos(az),np.cos(ev)*np.sin(az),np.sin(ev)])
 right=np.array([-np.sin(az),np.cos(az),0]);up=np.cross(direction,right)
 uv=np.column_stack([v@right,-v@up]);scale=min(1050/np.ptp(uv,axis=0));off=np.array([xo+600,yo+630])-(uv.min(0)+uv.max(0))*.5*scale;pix=uv*scale+off
 light=np.array([-.5,-.4,.75]);light/=np.linalg.norm(light);shade=np.clip(.84+.16*(n@light),.55,1.)
 for i in np.argsort(c@direction):
  if n[i]@direction <= 0: continue
  hx=h['PALETTE'][labels[i]].lstrip('#');rgb=np.array([int(hx[k:k+2],16) for k in (0,2,4)])
  color=tuple(np.clip(rgb*shade[i],0,255).astype(np.uint8));inds=loops[st[i]:st[i]+ct[i]];poly=[tuple(point) for point in pix[inds]]
  d.polygon(poly,fill=color)
 d.text((xo+40,yo+12),name,fill='#243E47',font=font)
 counts={role:int(np.sum(labels==role)) for role in h['PALETTE'] if np.any(labels==role)}
 d.text((xo+40,yo+52),' | '.join(role.replace('sea_','')+' '+str(count) for role,count in counts.items()),fill='#475D61',font=small)
img.save(p/'sea-object-parts-audit.png')
print(p/'sea-object-parts-audit.png')
