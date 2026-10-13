"""Itti L*a*b* saliency exactly as critic oi_b0/sal.py + m_sal2.py (OBJ_INFO-22), parametrised by image path."""
import json, sys, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, maximum_filter, zoom
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
def srgb2lin(c): return np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4)
M=np.array([[0.4124564,0.3575761,0.1804375],[0.2126729,0.7151522,0.0721750],[0.0193339,0.1191920,0.9503041]])
WN=np.array([0.95047,1.0,1.08883])
def rgb2lab(rgb):
    lin=srgb2lin(np.asarray(rgb,dtype=np.float64)); xyz=lin@M.T/WN
    f=np.where(xyz>0.008856,np.cbrt(xyz),7.787*xyz+16/116)
    return np.stack([116*f[...,1]-16,500*(f[...,0]-f[...,1]),200*(f[...,1]-f[...,2])],-1)
def rgb2oklab(rgb):
    lin=srgb2lin(np.asarray(rgb,dtype=np.float64))
    M1=np.array([[0.4122214708,0.5363325363,0.0514459929],[0.2119034982,0.6806995451,0.1073969566],[0.0883024619,0.2817188376,0.6299787005]])
    M2=np.array([[0.2104542553,0.7936177850,-0.0040720468],[1.9779984951,-2.4285922050,0.4505937099],[0.0259040371,0.7827717662,-0.8086757660]])
    return np.cbrt(lin@M1.T)@M2.T
def oklch(rgb):
    o=rgb2oklab(rgb); return np.stack([o[...,0],np.hypot(o[...,1],o[...,2]),np.degrees(np.arctan2(o[...,2],o[...,1]))%360],-1)
def pyr(X,n=9):
    P=[X]
    for i in range(1,n): P.append(gaussian_filter(P[-1],1.0)[::2,::2])
    return P
def up(a,shape): return zoom(a,(shape[0]/a.shape[0],shape[1]/a.shape[1]),order=1)
def N(m):
    m=m-m.min(); mx=m.max()
    if mx<=0: return m
    m=m/mx
    lm=(maximum_filter(m,5)==m)&(m>0.05)
    vals=m[lm]
    if len(vals)>1: vals=np.sort(vals)[:-1]; mbar=vals.mean()
    else: mbar=0
    return m*(1-mbar)**2
def conspic(X):
    P=pyr(X); out=None; tgt=P[4].shape
    for c in (2,3,4):
        for d in (3,4):
            s=c+d
            if s>=len(P) or P[s].size==0 or min(P[s].shape)<1: continue
            f=np.abs(P[c]-up(P[s],P[c].shape)); f=up(N(f),tgt)
            out=f if out is None else out+f
    return N(out)
def saliency(rgb):
    lab=rgb2lab(rgb)
    return (conspic(lab[...,0]/100)+conspic(lab[...,1]/100)+conspic(lab[...,2]/100))/3
def peaks(S,k=2,win=3):
    lm=(maximum_filter(S,win)==S)&(S>0); ys,xs=np.nonzero(lm); v=S[ys,xs]; o=np.argsort(-v)
    return [(ys[i],xs[i],v[i]) for i in o[:k]]
def dilate_pt(mask,pt,ppp=3):
    r=int(round(pt*ppp)); return ndi.binary_dilation(mask,iterations=r) if r>0 else mask
def load(p): return np.asarray(Image.open(p).convert('RGB')).astype(np.float64)/255.
def detail(map2x_path, asset, cuefn, k=6, pad=60, label=''):
    """asset: dict from assets_index (bbox_visible_final_pt, crop_pt, files.isolated_rgba)."""
    im=load(map2x_path)
    x0,x1,y0,y1=asset['bbox_visible_final_pt']
    X0,Y0=max(0,x0-pad),max(0,y0-pad); X1,Y1=min(1191,x1+pad),min(1684,y1+pad)
    rgb=im[int(round(Y0*2)):int(round(Y1*2)),int(round(X0*2)):int(round(X1*2))]
    S=saliency(rgb)
    sy=rgb.shape[0]/S.shape[0]; sx=rgb.shape[1]/S.shape[1]
    rgba=np.asarray(Image.open(asset['files']['isolated_rgba']).convert('RGBA')).astype(np.float64)/255.; cp=asset['crop_pt']
    al=rgba[...,3]>0.5; ays,axs=np.nonzero(al); ta=cKDTree(np.column_stack([cp[0]+axs/3,cp[2]+ays/3]))
    lab2=rgb2lab(rgba[...,:3]); ok2=oklch(rgba[...,:3])
    cm=dilate_pt(cuefn(lab2,ok2,al,cp),3); cys,cxs=np.nonzero(cm); tc=cKDTree(np.column_stack([cp[0]+cxs/3,cp[2]+cys/3]))
    out=[]
    for (py,px,v) in peaks(S,k=200,win=3):
        X=X0+(px+0.5)*sx/2; Y=Y0+(py+0.5)*sy/2
        if ta.query((X,Y))[0]>4: continue
        out.append((round(X,1),round(Y,1),round(float(v),3),round(tc.query((X,Y))[0],1)))
        if len(out)==k: break
    return out, S, (X0,Y0,sx/2,sy/2)
def c_white(lab,ok,al,cp): return al&(lab[...,0]>80)&(ok[...,1]<0.05)
if __name__=='__main__':
    idx=json.load(open(sys.argv[2])); A={a['id']:a for a in idx['assets']}
    out,S,g=detail(sys.argv[1],A['detail_core3_lime_specimen'],c_white)
    print('core3 top peaks (X,Y,v,dist_to_grain_pt):',out)
    print('PASS' if any(o[3]<=0 for o in out[:2]) else 'FAIL')
