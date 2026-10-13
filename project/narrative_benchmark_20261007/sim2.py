import numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/assets/'
def lin(c):
    c=c/255.; return np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)
def Ls(l):
    Y=l@np.array([.2126,.7152,.0722]); return np.where(Y>.008856,116*np.cbrt(Y)-16,903.3*Y)
def L2Y(L): return ((L+16)/116)**3
def Y2L(Y): return 116*np.cbrt(Y)-16
S=3
def Dof(L,V):
    Vf=V.astype(float); N=ndi.gaussian_filter(L*Vf,2*S)/np.maximum(ndi.gaussian_filter(Vf,2*S),1e-6)
    I=ndi.binary_erosion(V,iterations=S); return float(np.mean((abs(L-N)>8)[I]))
a='road_ostiensis'
ctx=np.asarray(Image.open(R+a+'/context.png').convert('RGB')).astype(float)
rgba=np.asarray(Image.open(R+a+'/isolated_rgba.png').convert('RGBA')).astype(float)
iso=np.asarray(Image.open(R+a+'/isolated.png').convert('RGB')).astype(float)
M=rgba[...,3]>=128; Lc=Ls(lin(ctx)); Li=Ls(lin(iso)); V=M&(abs(Lc-Li)<6)
for jt in [59,61]:
    for f in [1.0,0.92,0.88,0.85]:
        L2=np.maximum(Lc,jt)
        hi=L2>72
        L2=np.where(hi, Y2L(L2Y(L2)*f), L2)
        print('joint>=%d curb Yx%.2f D=%.3f'%(jt,f,Dof(L2,V)))
# hexes
M1=np.array([[0.4122214708,0.5363325363,0.0514459929],[0.2119034982,0.6806995451,0.1073969566],[0.0883024619,0.2817188376,0.6299787005]])
M2=np.array([[0.2104542553,0.7936177850,-0.0040720468],[1.9779984951,-2.4285922050,0.4505937099],[0.0259040371,0.7827717662,-0.8086757660]])
def hex2lin(h): return lin(np.array([int(h[i:i+2],16) for i in (1,3,5)],float))
def lin2hex(l):
    l=np.clip(l,0,1); s=np.where(l<=0.0031308,12.92*l,1.055*l**(1/2.4)-0.055); return '#%02X%02X%02X'%tuple(int(round(v*255)) for v in s)
def toOk(l): return np.cbrt(M1@l) @ M2.T if False else M2@np.cbrt(M1@l)
def fromOk(o):
    lms=np.linalg.solve(M2,o)**3; return np.linalg.solve(M1,lms)
for h in ['#8D9A70','#A9B188','#75865C']:
    o=toOk(hex2lin(h)); C=np.hypot(o[1],o[2]); hh=np.degrees(np.arctan2(o[2],o[1]))
    for f in [0.85,0.8]:
        o2=np.array([o[0],o[1]*f,o[2]*f]); print(h,'Oklch L %.3f C %.3f h %.1f -> C x%.2f = %.3f'%(o[0],C,hh,f,C*f), lin2hex(fromOk(o2)))
for h,f in [('#C7BEAA',0.88),('#C7BEAA',0.92),('#A9A69F',1.49)]:
    print(h,'lin x',f,'->',lin2hex(hex2lin(h)*f), 'L* %.1f -> %.1f'%(Ls(hex2lin(h)), Ls(hex2lin(h)*f)))
