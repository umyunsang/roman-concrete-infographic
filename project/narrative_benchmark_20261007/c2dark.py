import json, numpy as np
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/assets/core2_hot_mixing/'
ctx=np.asarray(Image.open(R+'context.png').convert('RGB')).astype(float)
iso=np.asarray(Image.open(R+'isolated.png').convert('RGB')).astype(float)
al=np.asarray(Image.open(R+'isolated_rgba.png'))[...,3]
def lin(c):
    c=c/255.0; return np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)
def Ls(l):
    Y=l@np.array([.2126,.7152,.0722]); return np.where(Y>.008856,116*np.cbrt(Y)-16,903.3*Y)
Lc=Ls(lin(ctx)); Li=Ls(lin(iso)); M=al>=128; V=M&(abs(Lc-Li)<6)
p5=np.percentile(Lc[V],5)
dark=V&(Lc<=p5)
ys,xs=np.where(dark)
print('P5',p5,'dark px',dark.sum())
# spatial histogram: rows/cols
H,W=V.shape
print('dark y range px',ys.min(),ys.max(),'x',xs.min(),xs.max())
# region: pit interior approx y 150-250 x 100-280 (crop px); figures above y<150
pit=(ys>=140)&(ys<=260)&(xs>=95)&(xs<=285)
fig=(ys<140)|((xs>270)&(ys<230))
print('in pit box',pit.sum(),'figure zone',fig.sum(),'other',(~pit&~fig).sum())
print('mean rgb dark',ctx[dark].mean(0).round())
# percent of V by L bins
for t in [30,35,40,45,50]: print('L<=%d frac %.3f'%(t,(Lc[V]<=t).mean()))
out=np.zeros_like(ctx).astype(np.uint8)+60; out[V]=(ctx[V]*.6).astype(np.uint8); out[dark]=[255,0,255]
Image.fromarray(out).resize((W*2,H*2),Image.NEAREST).save('c2dark.png')
