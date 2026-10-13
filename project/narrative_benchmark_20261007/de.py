import numpy as np
from PIL import Image, ImageCms
W='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/'
srgb=ImageCms.createProfile('sRGB'); lab=ImageCms.createProfile('LAB', colorTemp=5000); pso=ImageCms.getOpenProfile(W+'PSOcoated_v3.icc')
s2l=ImageCms.buildTransform(srgb,lab,'RGB','LAB',renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC)
c2l=ImageCms.buildTransform(pso,lab,'CMYK','LAB',renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC)
c2lA=ImageCms.buildTransform(pso,lab,'CMYK','LAB',renderingIntent=ImageCms.Intent.ABSOLUTE_COLORIMETRIC)
def L(img,t):
    p=ImageCms.applyTransform(img,t).getpixel((0,0))
    return np.array([p[0]*100/255, p[1]-128, p[2]-128],float)
def de00(l1,l2):
    L1,a1,b1=l1; L2,a2,b2=l2
    C1=np.hypot(a1,b1); C2=np.hypot(a2,b2); Cb=(C1+C2)/2
    G=0.5*(1-np.sqrt(Cb**7/(Cb**7+25**7))); a1p=(1+G)*a1; a2p=(1+G)*a2
    C1p=np.hypot(a1p,b1); C2p=np.hypot(a2p,b2)
    h1=np.degrees(np.arctan2(b1,a1p))%360; h2=np.degrees(np.arctan2(b2,a2p))%360
    dL=L2-L1; dC=C2p-C1p
    dh=h2-h1
    if C1p*C2p==0: dh=0
    elif dh>180: dh-=360
    elif dh<-180: dh+=360
    dH=2*np.sqrt(C1p*C2p)*np.sin(np.radians(dh/2))
    Lb=(L1+L2)/2; Cbp=(C1p+C2p)/2
    hb=(h1+h2)/2 if abs(h1-h2)<=180 else (h1+h2+360)/2
    if C1p*C2p==0: hb=h1+h2
    T=1-0.17*np.cos(np.radians(hb-30))+0.24*np.cos(np.radians(2*hb))+0.32*np.cos(np.radians(3*hb+6))-0.20*np.cos(np.radians(4*hb-63))
    dth=30*np.exp(-((hb-275)/25)**2); Rc=2*np.sqrt(Cbp**7/(Cbp**7+25**7))
    Sl=1+0.015*(Lb-50)**2/np.sqrt(20+(Lb-50)**2); Sc=1+0.045*Cbp; Sh=1+0.015*Cbp*T; Rt=-np.sin(np.radians(2*dth))*Rc
    return np.sqrt((dL/Sl)**2+(dC/Sc)**2+(dH/Sh)**2+Rt*(dC/Sc)*(dH/Sh))
file_cmyk={'#2E2A22':(0.565,0.624,0.733,0.91),'#3E3A31':(0.549,0.525,0.592,0.757),'#59524A':(0.494,0.478,0.486,0.561),'#983821':(0.082,0.851,0.992,0.392),'#1B5760':(0.847,0.31,0.353,0.522),'#8A5427':(0.161,0.608,0.914,0.455),'#FFF4DD':(0,0.043,0.149,0),'#E7DBC6':(0.094,0.125,0.22,0.004)}
for hx,c in file_cmyk.items():
    rgb=tuple(int(hx[i:i+2],16) for i in (1,3,5))
    l1=L(Image.new('RGB',(1,1),rgb),s2l)
    l2=L(Image.new('CMYK',(1,1),tuple(int(round(v*255)) for v in c)),c2l)
    print('%s design Lab %5.1f %5.1f %5.1f | print(rel) Lab %5.1f %5.1f %5.1f | dE00 %.2f'%(hx,*l1,*l2,de00(l1,l2)))
# PSO paper white & black
pw=L(Image.new('CMYK',(1,1),(0,0,0,0)),c2lA); bk=L(Image.new('CMYK',(1,1),(255,255,255,255)),c2lA)
print('paper abs Lab', pw, 'max black abs', bk)
