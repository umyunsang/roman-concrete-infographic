import json, sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx=json.load(open(R+'assets_index.json')); A={a['id']:a for a in idx['assets']}
def lin(c):
    c=c/255.0; return np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)
def Ls(l):
    Y=l@np.array([.2126,.7152,.0722]); return np.where(Y>.008856,116*np.cbrt(Y)-16,903.3*Y)
def oklab(l):
    M1=np.array([[0.4122214708,0.5363325363,0.0514459929],[0.2119034982,0.6806995451,0.1073969566],[0.0883024619,0.2817188376,0.6299787005]])
    M2=np.array([[0.2104542553,0.7936177850,-0.0040720468],[1.9779984951,-2.4285922050,0.4505937099],[0.0259040371,0.7827717662,-0.8086757660]])
    return np.cbrt(l@M1.T)@M2.T
for aid in sys.argv[1:]:
    a=A[aid]; f=a['files']
    ctx=np.asarray(Image.open(f['context']).convert('RGB')).astype(float)
    iso=np.asarray(Image.open(f['isolated']).convert('RGB')).astype(float)
    al=np.asarray(Image.open(f['isolated_rgba']))[...,3]
    M=al>=128
    Lc=Ls(lin(ctx)); Li=Ls(lin(iso)); dL=Lc-Li
    V=M&(np.abs(dL)<6)
    notV=M&~V
    inner=ndi.binary_erosion(M,iterations=3)
    edge=M&~inner
    okc=oklab(lin(ctx)); oki=oklab(lin(iso))
    dab=np.linalg.norm(okc[...,1:]-oki[...,1:],axis=-1)
    nv_in=notV&inner
    shadow=nv_in&(dL<0)&(dab<0.03)
    other=nv_in&~shadow
    S=3
    print(aid,'M=%d notV=%d (%.4f) edge=%d inner=%d | inner: darker-same-hue(shadow)=%d other(colour change/occlusion)=%d'%(M.sum(),notV.sum(),notV.sum()/M.sum(),(notV&edge).sum(),nv_in.sum(),shadow.sum(),other.sum()))
    print('   areas pt2: notV %.1f, edge %.1f, shadow %.1f, other %.1f'%(notV.sum()/9,(notV&edge).sum()/9,shadow.sum()/9,other.sum()/9))
    lab,n=ndi.label(other)
    if n:
        sz=ndi.sum(np.ones_like(lab),lab,range(1,n+1)); order=np.argsort(-sz)[:6]
        for i in order:
            ys,xs=np.where(lab==i+1)
            cc=ctx[lab==i+1].mean(0); ci=iso[lab==i+1].mean(0)
            print('   blob %4d px bbox x%d-%d y%d-%d (pt x%.1f-%.1f y%.1f-%.1f) ctx rgb %s iso rgb %s'%(sz[i],xs.min(),xs.max(),ys.min(),ys.max(),a['crop_pt'][0]+xs.min()/3,a['crop_pt'][0]+xs.max()/3,a['crop_pt'][2]+ys.min()/3,a['crop_pt'][2]+ys.max()/3,cc.round(),ci.round()))
    # write diag image
    out=np.zeros(ctx.shape,np.uint8)+40
    out[V]=(ctx[V]*0.5).astype(np.uint8)
    out[notV&edge]=[255,255,0]; out[shadow]=[0,120,255]; out[other]=[255,0,0]
    Image.fromarray(out).resize((out.shape[1]*2,out.shape[0]*2),Image.NEAREST).save(aid+'_visdiag.png')
