import json, numpy as np
from PIL import Image
ROOT='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
IDX=json.load(open(ROOT+'obj_r11/assets_index.json'))
INV=json.load(open(ROOT+'obj_r11/inventory.json'))
NAMES=[o['name'] for o in INV['objects']]
def asset(aid):
    return next(a for a in IDX['assets'] if a['id']==aid)
def srgb2lin(c):
    c=np.asarray(c,dtype=np.float64)/255.0
    return np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4)
def Lstar_from_Y(Y):
    Y=np.asarray(Y)
    f=np.where(Y>216/24389,np.cbrt(Y),(24389/27*Y+16)/116)
    return 116*f-16
def Y_from_L(L):
    L=np.asarray(L,dtype=float)
    f=(L+16)/116
    return np.where(f**3>216/24389,f**3,(116*f-16)/(24389/27))
def rgb2L(rgb):
    lin=srgb2lin(rgb)
    Y=0.2126*lin[...,0]+0.7152*lin[...,1]+0.0722*lin[...,2]
    return Lstar_from_Y(Y)
M_XYZ=np.array([[0.4124564,0.3575761,0.1804375],[0.2126729,0.7151522,0.0721750],[0.0193339,0.1191920,0.9503041]])
WP=np.array([0.95047,1.0,1.08883])
def rgb2lab(rgb):
    lin=srgb2lin(rgb)
    xyz=lin@M_XYZ.T
    t=xyz/WP
    f=np.where(t>216/24389,np.cbrt(t),(24389/27*t+16)/116)
    L=116*f[...,1]-16; a=500*(f[...,0]-f[...,1]); b=200*(f[...,1]-f[...,2])
    return np.stack([L,a,b],-1)
def de76(l1,l2): return float(np.linalg.norm(np.asarray(l1)-np.asarray(l2)))
def de00(lab1,lab2):
    L1,a1,b1=lab1; L2,a2,b2=lab2
    C1=np.hypot(a1,b1); C2=np.hypot(a2,b2); Cb=(C1+C2)/2
    G=0.5*(1-np.sqrt(Cb**7/(Cb**7+25**7)))
    a1p=(1+G)*a1; a2p=(1+G)*a2
    C1p=np.hypot(a1p,b1); C2p=np.hypot(a2p,b2)
    h1p=np.degrees(np.arctan2(b1,a1p))%360; h2p=np.degrees(np.arctan2(b2,a2p))%360
    dLp=L2-L1; dCp=C2p-C1p
    dh=h2p-h1p
    if C1p*C2p==0: dh=0
    elif dh>180: dh-=360
    elif dh<-180: dh+=360
    dHp=2*np.sqrt(C1p*C2p)*np.sin(np.radians(dh/2))
    Lbp=(L1+L2)/2; Cbp=(C1p+C2p)/2
    if C1p*C2p==0: hbp=h1p+h2p
    elif abs(h1p-h2p)<=180: hbp=(h1p+h2p)/2
    elif h1p+h2p<360: hbp=(h1p+h2p+360)/2
    else: hbp=(h1p+h2p-360)/2
    T=1-0.17*np.cos(np.radians(hbp-30))+0.24*np.cos(np.radians(2*hbp))+0.32*np.cos(np.radians(3*hbp+6))-0.20*np.cos(np.radians(4*hbp-63))
    dth=30*np.exp(-((hbp-275)/25)**2)
    RC=2*np.sqrt(Cbp**7/(Cbp**7+25**7))
    SL=1+0.015*(Lbp-50)**2/np.sqrt(20+(Lbp-50)**2)
    SC=1+0.045*Cbp; SH=1+0.015*Cbp*T
    RT=-np.sin(np.radians(2*dth))*RC
    return float(np.sqrt((dLp/SL)**2+(dCp/SC)**2+(dHp/SH)**2+RT*(dCp/SC)*(dHp/SH)))
def rgb2oklch(rgb):
    lin=srgb2lin(rgb)
    l=0.4122214708*lin[...,0]+0.5363325363*lin[...,1]+0.0514459929*lin[...,2]
    m=0.2119034982*lin[...,0]+0.6806995451*lin[...,1]+0.1073969566*lin[...,2]
    s=0.0883024619*lin[...,0]+0.2817188376*lin[...,1]+0.6299787005*lin[...,2]
    l_,m_,s_=np.cbrt(l),np.cbrt(m),np.cbrt(s)
    L=0.2104542553*l_+0.7936177850*m_-0.0040720468*s_
    a=1.9779984951*l_-2.4285922050*m_+0.4505937099*s_
    b=0.0259040371*l_+0.7827717662*m_-0.8086757660*s_
    return np.stack([L,np.hypot(a,b),np.degrees(np.arctan2(b,a))%360],-1)
def load_ctx(aid):
    a=asset(aid)
    ctx=np.array(Image.open(a['files']['context']).convert('RGB'))
    iso=np.array(Image.open(a['files']['isolated_rgba']))
    x0,x1,y0,y1=a['crop_pt']
    h,w=ctx.shape[:2]
    sx=w/(x1-x0); sy=h/(y1-y0)
    return a,ctx,iso,(x0,x1,y0,y1),(sx,sy)
_idcache={}
def idpass(kind):
    if kind not in _idcache:
        im=np.array(Image.open(ROOT+f'obj_r11/idpass/id_id_{kind}.png')).astype(int)
        ids=np.where(im[...,3]>0,(im[...,0]-2)//4+64*((im[...,1]-2)//4),0)
        _idcache[kind]=ids
    return _idcache[kind]
def id_on_ctx(kind,crop,scale,shape):
    ids=idpass(kind)
    x0,x1,y0,y1=crop; sx,sy=scale; h,w=shape
    s=INV['id_pass']['id_px_per_pt']
    jj=np.arange(w); ii=np.arange(h)
    ptx=x0+(jj+0.5)/sx; pty=y0+(ii+0.5)/sy
    px=np.clip((ptx*s).astype(int),0,ids.shape[1]-1); py=np.clip((pty*s).astype(int),0,ids.shape[0]-1)
    return ids[py][:,px]
def oid(name): return NAMES.index(name)+1
