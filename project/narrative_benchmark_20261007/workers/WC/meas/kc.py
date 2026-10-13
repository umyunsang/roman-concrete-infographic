import json, sys, numpy as np
from PIL import Image
R=sys.argv[1].rstrip('/')+'/'
idx=json.load(open(R+'assets_index.json')); A={a['id']:a for a in idx['assets']}
paper=np.array([0.0040323,0.03181737])
def lin(c):
    c=np.asarray(c,float)/255.0; return np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)
def Ls(l):
    Y=l@np.array([.2126,.7152,.0722]); return np.where(Y>.008856,116*np.cbrt(Y)-16,903.3*Y)
M1=np.array([[0.4122214708,0.5363325363,0.0514459929],[0.2119034982,0.6806995451,0.1073969566],[0.0883024619,0.2817188376,0.6299787005]])
M2=np.array([[0.2104542553,0.7936177850,-0.0040720468],[1.9779984951,-2.4285922050,0.4505937099],[0.0259040371,0.7827717662,-0.8086757660]])
def oklab(l): return np.cbrt(l@M1.T)@M2.T
for aid in sys.argv[2].split(','):
    a=A[aid]; f=a['files']
    ctx=np.asarray(Image.open(f['context']).convert('RGB')).astype(float)
    iso=np.asarray(Image.open(f['isolated']).convert('RGB')).astype(float)
    al=np.asarray(Image.open(f['isolated_rgba']))[...,3]
    lc=lin(ctx); Lc=Ls(lc); M=al>=128; V=M&(abs(Lc-Ls(lin(iso)))<6)
    ok=oklab(lc); C=np.hypot(ok[...,1],ok[...,2]); hd=(np.degrees(np.arctan2(ok[...,2],ok[...,1]))+360)%360
    d=np.linalg.norm(ok[...,1:]-paper,axis=-1)[V]
    blue=V&(hd>=180)&(hd<=270); water=blue&(C>=0.06)
    print(aid,'Kc(P90) %.4f  water frac %.3f  water area pt2 %.0f  V pt2 %.0f'%(np.percentile(d,90),water.sum()/V.sum(),water.sum()/9,V.sum()/9))
