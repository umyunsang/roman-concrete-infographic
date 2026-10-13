import numpy as np, json, sys
from PIL import Image
RL='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/assets/'
def oklch(rgb):
    c=np.where(rgb<=0.04045,rgb/12.92,((rgb+0.055)/1.055)**2.4)
    M1=np.array([[0.4122214708,0.5363325363,0.0514459929],[0.2119034982,0.6806995451,0.1073969566],[0.0883024619,0.2817188376,0.6299787005]])
    lms=np.cbrt(c@M1.T)
    M2=np.array([[0.2104542553,0.7936177850,-0.0040720468],[1.9779984951,-2.4285922050,0.4505937099],[0.0259040371,0.7827717662,-0.8086757660]])
    lab=lms@M2.T; L=lab[...,0]; C=np.hypot(lab[...,1],lab[...,2]); h=np.degrees(np.arctan2(lab[...,2],lab[...,1]))%360
    return L,C,h
for aid in ['core2_hot_mixing']:
    im=np.asarray(Image.open(RL+aid+'/isolated_rgba.png').convert('RGBA')).astype(float)/255
    m=im[...,3]>0.5; L,C,h=oklch(im[...,:3])
    water=m&(C>0.04)&(h>170)&(h<260); red=m&(C>0.10)&((h<45)|(h>340))
    print(aid,'mask px',m.sum(),'water-hue px',water.sum(),'pt2',water.sum()/9,'saturated red px',red.sum())
    # reference: water material #3F9DAA
    ref=np.array([[0x3F,0x9D,0xAA]])/255; print('ref water oklch',[float(x[0]) for x in oklch(ref)])
    ref=np.array([[0xD1,0x5B,0x36]])/255; print('ref heat oklch',[float(x[0]) for x in oklch(ref)])
