import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/assets/'
def lin(c):
    c=c/255.; return np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)
def Ls(l):
    Y=l@np.array([.2126,.7152,.0722]); return np.where(Y>.008856,116*np.cbrt(Y)-16,903.3*Y)
M1=np.array([[0.4122214708,0.5363325363,0.0514459929],[0.2119034982,0.6806995451,0.1073969566],[0.0883024619,0.2817188376,0.6299787005]])
M2=np.array([[0.2104542553,0.7936177850,-0.0040720468],[1.9779984951,-2.4285922050,0.4505937099],[0.0259040371,0.7827717662,-0.8086757660]])
def ok(l): return np.cbrt(l@M1.T)@M2.T
S=3
def Dof(L,V):
    Vf=V.astype(float); N=ndi.gaussian_filter(L*Vf,2*S)/np.maximum(ndi.gaussian_filter(Vf,2*S),1e-6)
    I=ndi.binary_erosion(V,iterations=S); return float(np.mean((abs(L-N)>8)[I]))
for a in ['road_ostiensis','road_appia','road_core_se','road_core_se_2']:
    ctx=np.asarray(Image.open(R+a+'/context.png').convert('RGB')).astype(float)
    rgba=np.asarray(Image.open(R+a+'/isolated_rgba.png').convert('RGBA')).astype(float)
    iso=np.asarray(Image.open(R+a+'/isolated.png').convert('RGB')).astype(float)
    M=rgba[...,3]>=128; Lc=Ls(lin(ctx)); Li=Ls(lin(iso)); V=M&(abs(Lc-Li)<6)
    d=ndi.distance_transform_edt(~M); ring=(d>9)&(d<=45); medR=np.median(Lc[ring])
    out=[]
    for lo,hi in [(0,200),(57,200),(59,200),(61,200),(59,76),(59,74),(61,74)]:
        L2=np.clip(Lc,lo,hi)
        D=Dof(L2,V); K=max(medR-np.percentile(L2[V],5), np.percentile(L2[V],95)-medR)
        out.append('[%d,%d] D=%.3f K=%.1f'%(lo,hi,D,K))
    print(a,' | '.join(out))
# trees_s chroma scaling
paper=np.array([0.0040323,0.03181737])
a='trees_s'
ctx=np.asarray(Image.open(R+a+'/context.png').convert('RGB')).astype(float)
rgba=np.asarray(Image.open(R+a+'/isolated_rgba.png').convert('RGBA')).astype(float)
iso=np.asarray(Image.open(R+a+'/isolated.png').convert('RGB')).astype(float)
M=rgba[...,3]>=128; Lc=Ls(lin(ctx)); Li=Ls(lin(iso)); V=M&(abs(Lc-Li)<6)
o=ok(lin(ctx))[V]
for f in [1.0,0.95,0.9,0.85,0.8,0.75]:
    ab=o[:,1:]*f
    print('trees_s chroma x%.2f Kc=%.4f'%(f,np.percentile(np.linalg.norm(ab-paper,axis=1),90)))
# per-material contribution: foliage vs trunk
