import numpy as np, json
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
IDX=json.load(open(R+'obj_r11/assets_index.json'))
A={a['id']:a for a in IDX['assets']}
def lin(c):
    c=c/255.0
    return np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4)
def Lstar_rgb(rgb):
    l=lin(rgb.astype(float))
    Y=0.2126*l[...,0]+0.7152*l[...,1]+0.0722*l[...,2]
    return Y2L(Y)
def Y2L(Y):
    return np.where(Y>0.008856,116*np.cbrt(Y)-16,903.3*Y)
def L2Y(L):
    L=np.asarray(L,float)
    return np.where(L>8,((L+16)/116)**3,L/903.3)
def lab(rgb):
    l=lin(rgb.astype(float))
    M=np.array([[0.4124564,0.3575761,0.1804375],[0.2126729,0.7151522,0.0721750],[0.0193339,0.1191920,0.9503041]])
    XYZ=l@M.T
    Xn,Yn,Zn=0.95047,1.0,1.08883
    def f(t): return np.where(t>0.008856,np.cbrt(t),7.787*t+16/116)
    fx,fy,fz=f(XYZ[...,0]/Xn),f(XYZ[...,1]/Yn),f(XYZ[...,2]/Zn)
    return np.stack([116*fy-16,500*(fx-fy),200*(fy-fz)],-1)
def de00(l1,l2):
    L1,a1,b1=l1;L2,a2,b2=l2
    C1=np.hypot(a1,b1);C2=np.hypot(a2,b2);Cb=(C1+C2)/2
    G=0.5*(1-np.sqrt(Cb**7/(Cb**7+25**7)))
    a1p=(1+G)*a1;a2p=(1+G)*a2
    C1p=np.hypot(a1p,b1);C2p=np.hypot(a2p,b2)
    h1p=np.degrees(np.arctan2(b1,a1p))%360;h2p=np.degrees(np.arctan2(b2,a2p))%360
    dLp=L2-L1;dCp=C2p-C1p
    dh=h2p-h1p
    if C1p*C2p==0: dh=0
    elif dh>180: dh-=360
    elif dh<-180: dh+=360
    dHp=2*np.sqrt(C1p*C2p)*np.sin(np.radians(dh/2))
    Lbp=(L1+L2)/2;Cbp=(C1p+C2p)/2
    if C1p*C2p==0: hbp=h1p+h2p
    elif abs(h1p-h2p)<=180: hbp=(h1p+h2p)/2
    elif h1p+h2p<360: hbp=(h1p+h2p+360)/2
    else: hbp=(h1p+h2p-360)/2
    T=1-0.17*np.cos(np.radians(hbp-30))+0.24*np.cos(np.radians(2*hbp))+0.32*np.cos(np.radians(3*hbp+6))-0.20*np.cos(np.radians(4*hbp-63))
    dth=30*np.exp(-((hbp-275)/25)**2)
    Rc=2*np.sqrt(Cbp**7/(Cbp**7+25**7))
    Sl=1+0.015*(Lbp-50)**2/np.sqrt(20+(Lbp-50)**2)
    Sc=1+0.045*Cbp;Sh=1+0.015*Cbp*T
    Rt=-np.sin(np.radians(2*dth))*Rc
    return float(np.sqrt((dLp/Sl)**2+(dCp/Sc)**2+(dHp/Sh)**2+Rt*(dCp/Sc)*(dHp/Sh)))
def load(aid):
    a=A[aid];f=a['files']
    ctx=np.array(Image.open(f['context']).convert('RGB'))
    iso=np.array(Image.open(f['isolated_rgba']))
    return a,ctx,iso
def hexL(h):
    h=h.lstrip('#');rgb=np.array([int(h[i:i+2],16) for i in (0,2,4)])
    return float(Lstar_rgb(rgb[None,None,:])[0,0])
