import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx=json.load(open(R+'assets_index.json')); A={a['id']:a for a in idx['assets']}
def lin(c):
    c=c/255.0; return np.where(c<=.04045, c/12.92, ((c+.055)/1.055)**2.4)
def Lstar(l):
    Y=l@np.array([.2126,.7152,.0722]); return np.where(Y>.008856, 116*np.cbrt(Y)-16, 903.3*Y)
f=A['landmark_pantheon']['files']
ctx=np.asarray(Image.open(f['context']).convert('RGB')).astype(float); iso=np.asarray(Image.open(f['isolated']).convert('RGB')).astype(float)
rgba=np.asarray(Image.open(f['isolated_rgba']).convert('RGBA'))
Lc=Lstar(lin(ctx)); Li=Lstar(lin(iso)); M=rgba[...,3]>=128; V=M&(np.abs(Lc-Li)<6)
I=ndi.binary_erosion(V, iterations=3)
N=ndi.gaussian_filter(Lc*V,6)/np.maximum(ndi.gaussian_filter(V*1.0,6),1e-6)
d=Lc-N; hit=(np.abs(d)>8)&I
H,W=Lc.shape; yy,xx=np.mgrid[:H,:W]
# hue split: roof material is darker orange (#A88565) vs stone (#D3BE9E)
rgb=ctx
from skimage.color import rgb2lab
lab=rgb2lab(rgb/255.0)
hue=np.degrees(np.arctan2(lab[...,2],lab[...,1])); C=np.hypot(lab[...,1],lab[...,2])
regions={'portico(x<185,y>165)':(xx<185)&(yy>165),'dome(y<125)':(yy<125),'drum/rest':~(((xx<185)&(yy>165))|(yy<125))}
tot=hit.sum()
for k,r in regions.items():
    print(k,'I px',(I&r).sum(),'hits',(hit&r).sum(),'share %.2f'%((hit&r).sum()/tot),'local D %.3f'%((hit&r).sum()/max((I&r).sum(),1)))
# material proxy: C* > 22 => roof (orange), else stone
roof=V&(C>24)
print('roof-proxy share of V %.2f, of hits %.2f'%(roof.sum()/V.sum(), (hit&roof).sum()/tot))
print('median L roof-proxy %.1f stone-proxy %.1f'%(np.median(Lc[roof]), np.median(Lc[V&~roof])))
# pt size info
print('crop px',W,H,'bbox',A['landmark_pantheon']['bbox_visible_final_pt'])
