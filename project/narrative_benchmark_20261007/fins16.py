import numpy as np, json, sys
from PIL import Image
from scipy import ndimage as ndi
from skimage import color, measure, morphology
A='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/assets'
idx=json.load(open('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/assets_index.json'))
crop={a['id']:a['crop_pt'] for a in idx['assets']}
vine=color.rgb2lab(np.array([[[0xA9,0xBC,0x87]]])/255)[0,0]
for a in sys.argv[1:]:
    arr=np.asarray(Image.open(f'{A}/{a}/isolated_rgba.png')).astype(float)/255
    m=arr[...,3]>0.5
    lab=color.rgb2lab(arr[...,:3])
    f=ndi.binary_fill_holes(m)
    op=morphology.binary_opening(f,morphology.disk(3))
    r=f&~op
    lbl=measure.label(r,connectivity=2)
    x0,x1,y0,y1=crop[a]
    out=[]
    for p in measure.regionprops(lbl):
        L=p.major_axis_length/3
        if L<3: continue
        cols=lab[lbl==p.label]
        med=np.median(cols,0)
        green = med[1]< -5   # posts are green (a*<0)
        out.append((round(L,1),round(p.area/9,2),round(x0+p.centroid[1]/3,1),round(y0+p.centroid[0]/3,1),green,med.round(1).tolist()))
    ng=[o for o in out if not o[4]]
    print('==',a,'residues>=3pt',len(out),'non-green',len(ng))
    for o in sorted(ng,key=lambda o:-o[0])[:12]: print('   len %.1fpt area %.2fpt2 at (%.1f,%.1f) lab %s'%(o[0],o[1],o[2],o[3],o[5]))
