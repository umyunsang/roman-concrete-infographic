import numpy as np
from PIL import Image, ImageCms
Image.MAX_IMAGE_PIXELS=None
W='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/'
pso=ImageCms.getOpenProfile(W+'PSOcoated_v3.icc'); srgb=ImageCms.createProfile('sRGB')
t=ImageCms.buildTransform(pso,srgb,'CMYK','RGB',renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC,flags=0)
img=Image.open('print_img_300.tif')
vm=np.load('vmask.npy')
def lin(c):
    c=c/255.0; return np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4)
def Y(a): l=lin(a); return 0.2126*l[...,0]+0.7152*l[...,1]+0.0722*l[...,2]
def dil(m,n):
    for _ in range(n): m = m | np.roll(m,1,0) | np.roll(m,-1,0) | np.roll(m,1,1) | np.roll(m,-1,1)
    return m
moved={'790:115 베수비오 화산':(913,1490,73,46),'790:119 폼페이':(757,1494,43,28),'790:120 항구':(11,1442,31,22),'790:124 티레니아해':(558,1609,67,41),'797:79 판테온':(344,552,90,16),'797:80 티베르강':(130,372,51,33),'802:78 콜로세움':(362,924,51,34)}
s=300/72; o=8.5
for k,(x,y,w,h) in moved.items():
    X0=int((x+o-20)*s); Y0=int((y+o-20)*s); X1=int((x+w+o+20)*s); Y1=int((y+h+o+20)*s)
    bg=np.asarray(ImageCms.applyTransform(img.crop((X0,Y0,X1,Y1)),t)).astype(float)
    yb=Y(bg)
    m=vm[Y0:Y1,X0:X1]
    # restrict to the label's own box
    box=np.zeros_like(m); box[int(20*s):int((20+h)*s), int(20*s):int((20+w)*s)]=True
    m=m&box
    halo=dil(m,4)
    ground=np.median(yb)
    frac=(np.abs(yb[halo]-ground)>0.08).mean()
    print('%-16s print box pt (%d,%d,%d,%d)  ground Y %.3f  halo px off-ground(|dY|>0.08) %.1f%%'%(k,x,y,w,h,ground,frac*100))
