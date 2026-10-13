import sys, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
sys.path.insert(0,'.')
from clr import *
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/assets/'
print('sect_heavy vs tower_heavy dE00', round(float(de00(lab(h2r('#A79880')),lab(h2r('#A9987C')))),2), 'D2', round(szafD(h2r('#A79880'),h2r('#A9987C'),2),2))
x=np.array(Image.open(B+'detail_d3_tower/isolated_rgba.png')).astype(float); rgb=x[...,:3]; a=x[...,3]
full=a>=254
mats={'tower_foundation':'#8C806E','tower_heavy':'#A9987C','stone_light':'#EBDDCA','tower_middle':'#C8B491','secondary':'#615A4E','pozzolan':'#A4876D'}
P=lab(rgb[full])
D=np.stack([ramp_min_de(P,h) for h in mats.values()],1)
cls=np.argmin(D,1); dmin=D.min(1)
lab_img=-np.ones(a.shape,int); lab_img[full]=cls
names=list(mats)
res={}
for i,n in enumerate(names):
    m=(lab_img==i)&(dmin.reshape(-1) if False else True)
    mm=np.zeros(a.shape,bool); mm[full]=(cls==i)&(dmin<3)
    mm=ndi.binary_erosion(mm,iterations=3)
    if mm.sum()<30: print(n,'n',int(mm.sum())); continue
    L=lab(rgb[mm])[:,0]; lo,hi=np.percentile(L,[60,90]); lit=rgb[mm][(L>=lo)&(L<=hi)].mean(0)
    res[n]=lit
    print(f'{n:16s} n {int(mm.sum()):6d} lit {hx(lit)} oklch {oklch(lit).round(3)} L {lab(lit)[0]:.1f}')
sect={'stone_light':'#CFC2B2','tower_middle':'#AC9B7C','tower_foundation':'#786E5E'}
for n,hv in sect.items():
    if n in res:
        o1=oklch(h2r(hv)); o2=oklch(res[n])
        dh=abs((o1[2]-o2[2]+180)%360-180)
        print(f'11 {n}: section {hv} vs tower {hx(res[n])}: dh {dh:.2f}  dC {abs(o1[1]-o2[1]):.4f}  Cs {o1[1]:.3f} {o2[1]:.3f}')
