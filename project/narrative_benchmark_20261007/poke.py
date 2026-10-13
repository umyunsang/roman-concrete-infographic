import sys, json, numpy as np
from PIL import Image
from skimage import color, measure, morphology
A='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/assets'
idx=json.load(open('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/assets_index.json'))
crop={a['id']:a['crop_pt'] for a in idx['assets']}
for a in sys.argv[1:]:
    ctx=np.asarray(Image.open(f'{A}/{a}/context.png').convert('RGB')).astype(float)/255
    iso=np.asarray(Image.open(f'{A}/{a}/isolated_rgba.png')).astype(float)/255
    al=iso[...,3]; isorgb=iso[...,:3]
    Lc=color.rgb2lab(ctx); Li=color.rgb2lab(isorgb)
    bgmask=al<0.01
    terr=np.median(Lc[bgmask],axis=0)
    dci=color.deltaE_ciede2000(Lc,Li)
    dct=color.deltaE_ciede2000(Lc,np.broadcast_to(terr,Lc.shape))
    core=morphology.binary_erosion(al>0.95,morphology.disk(2))
    occl=core&(dci>10)
    poke=occl&(dct<6)
    lbl=measure.label(poke,connectivity=2)
    x0,x1,y0,y1=crop[a]
    print('==',a,'terrain Lab',terr.round(1),'core px',core.sum(),'occluded px',occl.sum(),'terrain-like px',poke.sum())
    regs=[r for r in measure.regionprops(lbl) if r.area>=9]
    regs.sort(key=lambda r:-r.area)
    for r in regs[:25]:
        cy,cx=r.centroid; by0,bx0,by1,bx1=r.bbox
        print(f'  area {r.area/9:.1f}pt2 at pt ({x0+cx/3:.1f},{y0+cy/3:.1f}) bbox pt x {x0+bx0/3:.1f}-{x0+bx1/3:.1f} y {y0+by0/3:.1f}-{y0+by1/3:.1f}  img px ({cx:.0f},{cy:.0f})')
