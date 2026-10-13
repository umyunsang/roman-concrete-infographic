import json, sys, numpy as np
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx=json.load(open(R+'assets_index.json')); A={a['id']:a for a in idx['assets']}
paper=np.array([0.0040323,0.03181737])
def lin(c):
    c=np.asarray(c,float)/255.0; return np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)
def Ls(l):
    Y=l@np.array([.2126,.7152,.0722]); return np.where(Y>.008856,116*np.cbrt(Y)-16,903.3*Y)
def oklab(l):
    M1=np.array([[0.4122214708,0.5363325363,0.0514459929],[0.2119034982,0.6806995451,0.1073969566],[0.0883024619,0.2817188376,0.6299787005]])
    M2=np.array([[0.2104542553,0.7936177850,-0.0040720468],[1.9779984951,-2.4285922050,0.4505937099],[0.0259040371,0.7827717662,-0.8086757660]])
    return np.cbrt(l@M1.T)@M2.T
for aid in sys.argv[1:]:
    a=A[aid]; f=a['files']
    print('\n##',aid)
    for m in a['materials']:
        h=m['diffuse_hex']; rgb=[int(h[i:i+2],16) for i in (1,3,5)]
        o=oklab(lin(rgb)); print('  mat %-38s %s oklab L%.3f a%.3f b%.3f C%.3f dist_paper %.3f'%(m['material'],h,o[0],o[1],o[2],np.hypot(o[1],o[2]),np.linalg.norm(o[1:]-paper)))
    ctx=np.asarray(Image.open(f['context']).convert('RGB')).astype(float)
    iso=np.asarray(Image.open(f['isolated']).convert('RGB')).astype(float)
    al=np.asarray(Image.open(f['isolated_rgba']))[...,3]
    lc=lin(ctx); Lc=Ls(lc); Li=Ls(lin(iso)); M=al>=128; V=M&(abs(Lc-Li)<6)
    ok=oklab(lc); dist=np.linalg.norm(ok[...,1:]-paper,axis=-1)
    dv=dist[V]
    print('  Kc P90 %.4f; frac>0.0589 %.3f; P80 %.4f P85 %.4f'%(np.percentile(dv,90),(dv>0.0589).mean(),np.percentile(dv,80),np.percentile(dv,85)))
    # cluster by hue
    h=(np.degrees(np.arctan2(ok[...,2],ok[...,1]))+360)%360; C=np.hypot(ok[...,1],ok[...,2])
    hi=V&(dist>0.0589)
    hv=h[hi]; Cv=C[hi]
    for lo,hi_ in [(0,90),(90,180),(180,240),(240,300),(300,360)]:
        s=(hv>=lo)&(hv<hi_)
        if s.sum(): print('   hue %3d-%3d: %5.1f%% of V, median C %.3f, median L %.1f'%(lo,hi_,100*s.sum()/V.sum(),np.median(Cv[s]),np.median(Lc[hi][s])))
