import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage import color, measure, morphology
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx=json.load(open(B+'assets_index.json'))
mine=['shape_core1_marker','shape_core2_marker','shape_core3_marker','shape_core4_marker','shape_core5_marker','shape_d2_leader','shape_d3_section','shape_pin_harbor','shape_pin_pompeii']
A={a['id']:a for a in idx['assets']}
for i in mine:
    a=A[i]; f=a['files']
    rgba=np.asarray(Image.open(f['isolated_rgba'])).astype(float)/255
    ctx=np.asarray(Image.open(f['context']).convert('RGB')).astype(float)/255
    al=rgba[...,3]
    m=al>0.5
    lbl=measure.label(m,connectivity=2)
    props=measure.regionprops(lbl)
    x0,x1,y0,y1=a['crop_pt']
    print('==',i,'img',rgba.shape,'alpha>0.5 px',m.sum(),'alpha>0 px',(al>0).sum(),'ncomp',lbl.max())
    for p in sorted(props,key=lambda p:-p.area):
        r0,c0,r1,c1=p.bbox
        print('  comp area_pt2=%.2f bbox_pt x %.1f-%.1f y %.1f-%.1f  solidity %.3f ecc %.2f'%(p.area/9, x0+c0/3, x0+c1/3, y0+r0/3, y0+r1/3, p.solidity, p.eccentricity))
    # holes
    filled=ndi.binary_fill_holes(m); holes=filled&~m
    hl=measure.label(holes)
    hs=[p.area/9 for p in measure.regionprops(hl)]
    print('  holes pt2', [round(h,2) for h in hs if h>=0.1])
