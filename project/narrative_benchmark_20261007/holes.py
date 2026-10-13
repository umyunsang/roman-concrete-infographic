import numpy as np, json, sys
from PIL import Image
from scipy import ndimage as ndi
from skimage import color, measure
idx=json.load(open('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/assets_index.json'))
crop={a['id']:a['crop_pt'] for a in idx['assets']}
for a in sys.argv[1:]:
    A=f'/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/assets/{a}'
    ctx=np.asarray(Image.open(f'{A}/context.png').convert('RGB')).astype(float)/255
    iso=np.asarray(Image.open(f'{A}/isolated_rgba.png')).astype(float)/255
    al=iso[...,3]>0.5
    Lc=color.rgb2lab(ctx); Li=color.rgb2lab(iso[...,:3])
    terr=np.median(Lc[iso[...,3]<0.01],axis=0)
    dci=color.deltaE_ciede2000(Lc,Li)
    dct=color.deltaE_ciede2000(Lc,np.broadcast_to(terr,Lc.shape))
    # pixels inside iso mask whose context colour is closer to terrain than to iso colour and lighter than iso (terrain is lighter)
    cand=al&(dci>6)&(dct<dci)&(Lc[...,0]>Li[...,0])
    lbl=measure.label(cand,connectivity=2)
    x0,x1,y0,y1=crop[a]
    out=[]
    for r in measure.regionprops(lbl):
        if r.area<9: continue
        m=lbl==r.label
        ring=ndi.binary_dilation(m,iterations=3)&~m
        enclosed=al[ring].mean()
        cy,cx=r.centroid
        out.append((r.area/9,enclosed,x0+cx/3,y0+cy/3, float(np.median(dct[m])), float(np.median(dci[m]))))
    out.sort(key=lambda o:-o[0])
    print('==',a,len(out))
    for o in out[:15]: print('  area %.2f pt2 enclosed %.2f at (%.1f,%.1f) dE_terr %.1f dE_iso %.1f'%o)
