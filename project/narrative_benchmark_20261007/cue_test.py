import json, sys, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
ROOT=sys.argv[1]
idx=json.load(open(os.path.join(ROOT,'assets_index.json'))); S=idx['crop_scale']
A={a['id']:a for a in idx['assets']}
def lin(c):
    c=c/255.0; return np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4)
def Ls(l):
    Y=0.2126*l[...,0]+0.7152*l[...,1]+0.0722*l[...,2]; return np.where(Y>0.008856,116*np.cbrt(Y)-16,903.3*Y)
def oklab(l):
    r,g,b=l[...,0],l[...,1],l[...,2]
    L_=np.cbrt(0.4122214708*r+0.5363325363*g+0.0514459929*b); M_=np.cbrt(0.2119034982*r+0.6806995451*g+0.1073969566*b); S_=np.cbrt(0.0883024619*r+0.2817188376*g+0.6299787005*b)
    return np.stack([0.2104542553*L_+0.7936177850*M_-0.0040720468*S_,1.9779984951*L_-2.4285922050*M_+0.4505937099*S_,0.0259040371*L_+0.7827717662*M_-0.8086757660*S_],-1)
CUES={'core1_modern_building':['steel','groove','rust'],'detail_core3_lime_specimen':['white'],'detail_core4_three_cubes':['water','white','groove'],'support_core5_lab':['groove','white','water'],'detail_d1_seawater':['white','water'],'detail_d2_making':['white','heat']}
for aid,cues in CUES.items():
    d=os.path.join(ROOT,'assets',aid)
    ctx=np.asarray(Image.open(os.path.join(d,'context.png')).convert('RGB')).astype(float)
    iso=np.asarray(Image.open(os.path.join(d,'isolated.png')).convert('RGB')).astype(float)
    al=np.asarray(Image.open(os.path.join(d,'isolated_rgba.png')))[...,3]
    M=al>=128; lc=lin(ctx); L=Ls(lc); V=M&(np.abs(L-Ls(lin(iso)))<6)
    ok=oklab(lc); C=np.hypot(ok[...,1],ok[...,2]); h=(np.degrees(np.arctan2(ok[...,2],ok[...,1]))+360)%360
    cm=np.zeros_like(V)
    for c in cues:
        if c=='white': m=(L>=88)&(C<=0.04)
        if c=='groove': m=(L<=22)
        if c=='water': m=(h>=180)&(h<=240)&(C>=0.06)
        if c=='steel': m=(h>=200)&(h<=270)&(C>=0.02)&(L<50)
        if c=='rust': m=(h>=40)&(h<=90)&(C>=0.03)
        if c=='heat': m=(h>=20)&(h<=50)&(C>=0.10)
        cm|=m
    cm&=V
    w=V.astype(float)
    nb=ndi.gaussian_filter(L*w,2*S)/np.maximum(ndi.gaussian_filter(w,2*S),1e-6)
    hp=np.abs(L-nb)
    inner=ndi.binary_erosion(V,iterations=int(S))
    thr=np.percentile(hp[inner],98)
    top=inner&(hp>=thr)
    cd=ndi.binary_dilation(cm,iterations=int(S))
    frac=(top&cd).sum()/top.sum()
    print(aid, cues, 'cue_area_frac=%.3f'%(cm.sum()/V.sum()), 'top2%%_in_cue=%.2f'%frac, 'thr=%.1f'%thr)
