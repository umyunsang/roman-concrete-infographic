import json, sys, os
import numpy as np
from PIL import Image
from skimage.color import rgb2lab
ROOT=sys.argv[1]
idx=json.load(open(os.path.join(ROOT,'assets_index.json'))); S=idx['crop_scale']
def lin(c):
    c=c/255.0; return np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4)
def oklab(l):
    r,g,b=l[...,0],l[...,1],l[...,2]
    L_=np.cbrt(0.4122214708*r+0.5363325363*g+0.0514459929*b); M_=np.cbrt(0.2119034982*r+0.6806995451*g+0.1073969566*b); S_=np.cbrt(0.0883024619*r+0.2817188376*g+0.6299787005*b)
    return np.stack([0.2104542553*L_+0.7936177850*M_-0.0040720468*S_,1.9779984951*L_-2.4285922050*M_+0.4505937099*S_,0.0259040371*L_+0.7827717662*M_-0.8086757660*S_],-1)
for hexc in ['#A0CFCF','#F4E8D1','#75865C','#983821','#365864','#3F9DAA','#CDA477','#9E7C69','#D15B36']:
    rgb=np.array([int(hexc[i:i+2],16) for i in (1,3,5)],float)
    ok=oklab(lin(rgb)); lab=rgb2lab((rgb/255.0)[None,None])[0,0]
    print(hexc,'OkL %.3f C %.3f h %.0f'%(ok[0],np.hypot(ok[1],ok[2]),(np.degrees(np.arctan2(ok[2],ok[1]))+360)%360),'| CIELAB L %.1f C* %.1f'%(lab[0],np.hypot(lab[1],lab[2])))
print('--- strong chroma area (C>=0.10) pt2 per asset')
for a in idx['assets']:
    d=os.path.join(ROOT,'assets',a['id'])
    ctx=np.asarray(Image.open(os.path.join(d,'context.png')).convert('RGB')).astype(float)
    al=np.asarray(Image.open(os.path.join(d,'isolated_rgba.png')))[...,3]>=128
    ok=oklab(lin(ctx)); C=np.hypot(ok[...,1],ok[...,2])
    area=((C>=0.10)&al).sum()/S/S
    a8=((C>=0.08)&al).sum()/S/S
    if area>1 or a8>50: print(a['id'],a['role'],'C>=.10: %.0f pt2'%area,' C>=.08: %.0f pt2'%a8)
