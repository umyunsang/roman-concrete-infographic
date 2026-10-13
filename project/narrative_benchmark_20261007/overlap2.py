import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.ndimage import zoom
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx=json.load(open(R+'assets_index.json')); A={a['id']:a for a in idx['assets']}
# local window in pt: x 30..160, y 880..1000  (3px/pt)
WX0,WY0,WW,WH=30*3,880*3,130*3,120*3
def place(aid, mask):
    c=A[aid]['crop_pt']; x0=int(round(c[0]*3))-WX0; y0=int(round(c[2]*3))-WY0
    big=np.zeros((WH,WW),bool); h,w=mask.shape
    ys0=max(0,-y0); xs0=max(0,-x0); ye=min(h,WH-y0); xe=min(w,WW-x0)
    if ye>ys0 and xe>xs0: big[y0+ys0:y0+ye, x0+xs0:x0+xe]=mask[ys0:ye,xs0:xe]
    return big
def lin(c):
    c=c/255.0; return np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)
def oklab(l):
    M1=np.array([[0.4122214708,0.5363325363,0.0514459929],[0.2119034982,0.6806995451,0.1073969566],[0.0883024619,0.2817188376,0.6299787005]])
    M2=np.array([[0.2104542553,0.7936177850,-0.0040720468],[1.9779984951,-2.4285922050,0.4505937099],[0.0259040371,0.7827717662,-0.8086757660]])
    return np.cbrt(l@M1.T)@M2.T
M2=place('core2_hot_mixing', np.asarray(Image.open(A['core2_hot_mixing']['files']['isolated_rgba']))[...,3]>=128)
d2=np.asarray(Image.open(A['detail_d2_making']['files']['isolated_rgba'])).astype(float)
ok=oklab(lin(d2[...,:3])); C=np.hypot(ok[...,1],ok[...,2])
heat=(d2[...,3]>=128)&(C>=0.10)
Hm=place('detail_d2_making',heat)
Cm=place('detail_d2_making',(d2[...,3]>=128)&~ndi.binary_dilation(heat,iterations=3))
FW=place('fields_w',np.asarray(Image.open(A['fields_w']['files']['isolated_rgba']))[...,3]>=128)
L2,n2=ndi.label(Hm)
print('overlap now pt2', (Hm&M2).sum()/9)
best=[]
for s in [0.5,0.6,0.7,0.8,1.0]:
  for dx in range(-14,15,1):
    for dy in range(-2,14,1):
        tp=tc=tf=0
        for i in range(1,n2+1):
            ys,xs=np.where(L2==i); y0,y1,x0,x1=ys.min(),ys.max(),xs.min(),xs.max()
            z=zoom((L2[y0:y1+1,x0:x1+1]==i).astype(float),s,order=0)>0.5
            hh,ww=z.shape; by=y1+dy*3; cx=(x0+x1)//2+dx*3
            big=np.zeros_like(Hm); big[by-hh+1:by+1, cx-ww//2:cx-ww//2+ww]=z
            tp+=(big&M2).sum(); tc+=(big&Cm).sum(); tf+=(big&FW).sum()
        if tc==0 and tf==0: best.append((tp,-s,abs(dx)+abs(dy),s,dx,dy))
best.sort()
for b in best[:10]: print('plinth overlap %.1f pt2  scale %.1f dx %+d dy %+d'%(b[0]/9,b[3],b[4],b[5]))
