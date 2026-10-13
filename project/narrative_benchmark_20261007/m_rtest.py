import sys, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
sys.path.insert(0,'.')
from clr import *
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/assets/'
ACC=h2r('#983821')
def load(p):
    x=np.array(Image.open(p)).astype(float); return x[...,:3], x[...,3]
iso,ia=load(B+'shape_core1_marker/isolated_rgba.png')
for v in ['asis','nocav']:
    rgb,a=load(f'rtest/core1_{v}.png')
    print(v, rgb.shape, 'iso', iso.shape)
    m=a>=254
    # badge region top-left 120x120, underline rows 170-195
    bm=m.copy(); bm[120:]=False
    um=m.copy(); um[:150]=False
    b1=ndi.binary_erosion(bm,iterations=1)
    bmed=np.median(rgb[b1],0); umed=np.median(rgb[um],0)
    Lb=lab(rgb[b1])[:,0]
    print(f'  badge med {hx(bmed)} L {lab(bmed)[0]:.1f} range p5-p95 {np.percentile(Lb,5):.1f}-{np.percentile(Lb,95):.1f} dE(acc) {float(de00(lab(bmed),lab(ACC))):.2f}')
    print(f'  underline med {hx(umed)} L {lab(umed)[0]:.1f} dE(acc) {float(de00(lab(umed),lab(ACC))):.2f}  ul vs badge dE {float(de00(lab(umed),lab(bmed))):.2f}')
    if v=='asis':
        # compare against isolated
        h=min(rgb.shape[0],iso.shape[0]); w=min(rgb.shape[1],iso.shape[1])
        both=(a[:h,:w]>=254)&(ia[:h,:w]>=254)
        print('  asis vs isolated meanabs on full-alpha', np.abs(rgb[:h,:w][both]-iso[:h,:w][both]).mean().round(2), both.sum())
    if v=='nocav':
        tl=s2l(h2r('#B44327')); k=s2l(bmed)/tl
        print('  nocav k per ch', k.round(3))
        need=s2l(ACC)/k
        print('  diffuse needed for #983821 without cavity:', hx(l2s(need)), 'scale', (need/tl).round(3))
for v in ['asis','nocav']:
    rgb,a=load(f'rtest/sect_{v}.png')
    m=a>=254
    print('sect',v)
    # rows of layers in crop: S_sect0 y 1221-1245 -> (y-1208.7)*3
    for nm,(y0,y1,x0,x1) in {'S_sect0':(1221,1245,390.7,401.2),'S_sect1':(1245,1272,388.2,403.2),'S_sect2':(1272,1300.5,386.2,405.7),'S_sect3':(1300.5,1315.6,384.7,407.2)}.items():
        Y0=int((y0-1208.7)*3)+4; Y1=int((y1-1208.7)*3)-4; X0=int((x0-302.6)*3)+4; X1=int((x1-302.6)*3)-4
        reg=rgb[Y0:Y1,X0:X1]; L=lab(reg.reshape(-1,3))[:,0]
        print(f'   {nm} med {hx(np.median(reg.reshape(-1,3),0))} L p5 {np.percentile(L,5):.1f} p50 {np.percentile(L,50):.1f} p95 {np.percentile(L,95):.1f} range {np.percentile(L,95)-np.percentile(L,5):.1f}')
    # leaders: full alpha medians per leader rows
    for nm,(y,x0,x1) in {'S_lead04':(1232.0,373.7,390.7),'S_lead06':(1258.5,365.2,388.2),'S_lead03':(1232.0,314.6,320.1),'S_sect_ground':(1300.5,409,418.2)}.items():
        Y=int(round((y-1208.7)*3)); X0=int((x0-302.6)*3); X1=int((x1-302.6)*3)
        seg=rgb[Y-2:Y+3,X0:X1]; sa=a[Y-2:Y+3,X0:X1]
        px=seg[sa>=254]
        if len(px): print(f'   {nm} full-alpha med {hx(np.median(px,0))} L {lab(np.median(px,0))[0]:.1f} n {len(px)}')
for v in ['asis','nocav']:
    rgb,a=load(f'rtest/pomp_{v}.png')
    m=a>=254
    dot=m.copy(); dot[int((1496.6-1480.3)*3):]=False
    line=m.copy(); line[:int((1497.5-1480.3)*3)]=False
    print('pomp',v,'dot',hx(np.median(rgb[dot],0)),'line',hx(np.median(rgb[line],0)),'dE',round(float(de00(lab(np.median(rgb[dot],0)),lab(np.median(rgb[line],0)))),2))
