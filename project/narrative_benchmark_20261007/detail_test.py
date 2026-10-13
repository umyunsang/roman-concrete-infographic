import json, sys, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.feature import canny
sys.path.insert(0,'.')
ROOT=sys.argv[1]
idx=json.load(open(os.path.join(ROOT,'assets_index.json'))); S=idx['crop_scale']
def lin(c):
    c=c/255.0; return np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4)
def Ls(l):
    Y=0.2126*l[...,0]+0.7152*l[...,1]+0.0722*l[...,2]; return np.where(Y>0.008856,116*np.cbrt(Y)-16,903.3*Y)
print('id\trole\tED15_02_06\tED3_04_10\tED3_06_15\tDE1pt\tDE3pt\tDEsig')
for a in idx['assets']:
    if a['id']=='ground_land': continue
    d=os.path.join(ROOT,'assets',a['id'])
    ctx=np.asarray(Image.open(os.path.join(d,'context.png')).convert('RGB')).astype(float)
    iso=np.asarray(Image.open(os.path.join(d,'isolated.png')).convert('RGB')).astype(float)
    al=np.asarray(Image.open(os.path.join(d,'isolated_rgba.png')))[...,3]
    M=al>=128
    L=Ls(lin(ctx)); Li=Ls(lin(iso))
    V=M&(np.abs(L-Li)<6)
    inner=ndi.binary_erosion(V,iterations=int(S))
    if inner.sum()<30: print(a['id'],a['role'],'n/a'); continue
    e1=canny(L/100,sigma=1.5,low_threshold=0.02,high_threshold=0.06)[inner].mean()
    e2=canny(L/100,sigma=3,low_threshold=0.04,high_threshold=0.10)[inner].mean()
    e3=canny(L/100,sigma=3,low_threshold=0.06,high_threshold=0.15)[inner].mean()
    # detail energy: mean abs high-pass inside mask (normalized convolution to avoid edge bleed from outside)
    w=V.astype(float)
    def nblur(img,s):
        num=ndi.gaussian_filter(img*w,s); den=ndi.gaussian_filter(w,s); return num/np.maximum(den,1e-6)
    hp1=np.abs(L-nblur(L,1*S))[inner].mean()
    hp3=np.abs(L-nblur(L,3*S))[inner].mean()
    # fraction of interior pixels with high-pass > 8 L* (strong detail)
    sig=(np.abs(L-nblur(L,2*S))>8)[inner].mean()
    print(f"{a['id']}\t{a['role']}\t{e1:.3f}\t{e2:.3f}\t{e3:.3f}\t{hp1:.2f}\t{hp3:.2f}\t{sig:.3f}")
