import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage import measure
A='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/assets/header_gate'
iso=np.asarray(Image.open(f'{A}/isolated_rgba.png')).astype(float)/255
al=iso[...,3]
x0,y0=345.2,7.0
m=al>0.5
filled=ndi.binary_fill_holes(m)
print('mask px',m.sum(),'filled',filled.sum())
# openings: background regions not connected to border, and also arches open at bottom? find bg comps
bg=~m
lbl=measure.label(bg,connectivity=1)
for r in measure.regionprops(lbl):
    if r.area<9: continue
    by0,bx0,by1,bx1=r.bbox
    touches = by0==0 or bx0==0 or by1==m.shape[0] or bx1==m.shape[1]
    print('bg comp area %.1f pt2 bbox pt x %.1f-%.1f y %.1f-%.1f touches_border %s solidity %.3f'%(r.area/9,x0+bx0/3,x0+bx1/3,y0+by0/3,y0+by1/3,touches,r.solidity))
# arch openings: columns profile - for x columns in arch ranges, find top of opening (first bg px from top below y px 470)
def opening_profile(xa,xb):
    prof=[]
    for x in range(xa,xb):
        col=m[460:665,x]
        idx=np.where(~col)[0]
        prof.append((x, 460+idx[0] if len(idx) else None))
    return prof
for name,(xa,xb) in {'left':(150,395),'center':(520,985),'right':(1110,1355)}.items():
    p=[(x,y) for x,y in opening_profile(xa,xb) if y is not None]
    xs=[x for x,_ in p]; ys=[y for _,y in p]
    xl,xr=min(xs),max(xs); top=min(ys)
    # springing: y where the opening reaches the vertical sides -> take y at the extreme columns
    print(name,'opening x px %d-%d (pt %.1f-%.1f) width %.1fpt crown y px %d (pt %.1f)'%(xl,xr,x0+xl/3,x0+xr/3,(xr-xl+1)/3,top,y0+top/3), 'side y at edges', ys[0], ys[-1], ' (pt %.1f %.1f)'%(y0+ys[0]/3,y0+ys[-1]/3))
    # crown x
    cx=[x for x,y in p if y==top]; print('   crown x px',cx[0],cx[-1])
