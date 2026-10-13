import json, sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx=json.load(open(R+'assets_index.json')); A={a['id']:a for a in idx['assets']}
def lin(c):
    c=c/255.0; return np.where(c<=.04045, c/12.92, ((c+.055)/1.055)**2.4)
def Lstar(l):
    Y=l@np.array([.2126,.7152,.0722]); return np.where(Y>.008856, 116*np.cbrt(Y)-16, 903.3*Y)
aid=sys.argv[1]; x0,y0,x1,y1=[int(v) for v in sys.argv[2:6]]
f=A[aid]['files']
ctx=np.asarray(Image.open(f['context']).convert('RGB')).astype(float); iso=np.asarray(Image.open(f['isolated']).convert('RGB')).astype(float)
rgba=np.asarray(Image.open(f['isolated_rgba']).convert('RGBA'))
Lc=Lstar(lin(ctx)); Li=Lstar(lin(iso)); M=rgba[...,3]>=128; V=M&(np.abs(Lc-Li)<6)
I=ndi.binary_erosion(V, iterations=3)
N=ndi.gaussian_filter(Lc*V,6)/np.maximum(ndi.gaussian_filter(V*1.0,6),1e-6)
diff=Lc-N; hit=(np.abs(diff)>8)&I
ov=ctx.copy()
ov[hit&(diff<0)]=[0,90,255]; ov[hit&(diff>0)]=[255,200,0]
a=Image.fromarray(ctx[y0:y1,x0:x1].astype(np.uint8)); b=Image.fromarray(ov[y0:y1,x0:x1].astype(np.uint8))
w,h=a.size; im=Image.new('RGB',(w*2+6,h),(255,255,255)); im.paste(a,(0,0)); im.paste(b,(w+6,0))
k=int(sys.argv[6]) if len(sys.argv)>6 else 2
im=im.resize((im.size[0]*k,im.size[1]*k),Image.NEAREST); im.save(aid+'_heat.png'); print(im.size, ctx.shape)
