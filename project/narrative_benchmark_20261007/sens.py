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
paper=np.array([0.0040323,0.03181737])
for a in ['trees_s','support_breakwater_block','support_harbor','tree_t_cypress','support_privernum']:
    ctx=np.asarray(Image.open(R+a+'/context.png').convert('RGB')).astype(float)
    rgba=np.asarray(Image.open(R+a+'/isolated_rgba.png').convert('RGBA')).astype(float)
    iso=np.asarray(Image.open(R+a+'/isolated.png').convert('RGB')).astype(float)
    M=rgba[...,3]>=128
    Lc=Ls(lin(ctx)); Li=Ls(lin(iso)); V=M&(abs(Lc-Li)<6)
    I=ndi.binary_erosion(V,iterations=3)
    kc_ctx=np.percentile(np.linalg.norm(ok(lin(ctx))[V][:,1:]-paper,axis=1),90)
    kc_iso=np.percentile(np.linalg.norm(ok(lin(iso))[V][:,1:]-paper,axis=1),90)
    kc_I=np.percentile(np.linalg.norm(ok(lin(ctx))[I][:,1:]-paper,axis=1),90)
    print(a,'Kc ctx %.4f iso %.4f ctx-interior %.4f'%(kc_ctx,kc_iso,kc_I))
