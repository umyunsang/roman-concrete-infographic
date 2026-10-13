from pathlib import Path
import numpy as np
import runpy
from PIL import Image,ImageDraw,ImageFont
p=Path(__file__).parent;a=np.load(p/'detail-object-geometry.npz');name='D2_lime_kiln';v=a[name+'_vertices'];c=a[name+'_centers'];n=a[name+'_normals'];st=a[name+'_starts'];ct=a[name+'_totals'];loops=a[name+'_loops']
helper=runpy.run_path(str(p/'hearth_object_parts.py'));roles=np.full(len(c),'kiln_shell',dtype=object);assignment=helper['select_arrays'](c,n)
for role,inds in assignment['faces'].items():roles[inds]=role
print({role:int(np.sum(roles==role)) for role in helper['PALETTE']})
img=Image.new('RGB',(2400,2400),(246,243,235));d=ImageDraw.Draw(img);font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',30)
for ix,azim in enumerate([-45,45,135,225]):
 row,col=divmod(ix,2);e=np.deg2rad(25);az=np.deg2rad(azim);direction=np.array([np.cos(e)*np.cos(az),np.cos(e)*np.sin(az),np.sin(e)]);right=np.array([-np.sin(az),np.cos(az),0]);up=np.cross(direction,right);uv=np.column_stack([v@right,-v@up]);scale=min(1060/np.ptp(uv,axis=0));off=np.array([col*1200+600,row*1200+650])-(uv.min(0)+uv.max(0))*.5*scale;pix=uv*scale+off
 shade=np.clip(.78+.22*n@np.array([-.5,-.4,.75]),.35,1.)
 for i in np.argsort(c@direction):
  if n[i]@direction<=0:continue
  inds=loops[st[i]:st[i]+ct[i]];hx=helper['PALETTE'][roles[i]].lstrip('#');rgb=np.array([int(hx[k:k+2],16) for k in (0,2,4)]);color=tuple((rgb*shade[i]).astype(np.uint8));d.polygon([tuple(x) for x in pix[inds]],fill=color)
 d.text((col*1200+40,row*1200+30),f'{name}: original surface parts, local azimuth {azim}',fill='#243E47',font=font)
img.save(p/'kiln-parts-audit.png')
