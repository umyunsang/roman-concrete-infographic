import sys, json, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from skimage import measure, morphology
A='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx=json.load(open(A+'assets_index.json'))
ids=sys.argv[1:]
S=3
for a in idx['assets']:
    if a['id'] not in ids: continue
    cx0,cx1,cy0,cy1=a['crop_pt']
    im=np.asarray(Image.open(a['files']['isolated_rgba']))
    obj=im[...,3]>=128
    f=ndi.binary_fill_holes(obj)
    op=morphology.binary_opening(f, morphology.disk(3))   # radius 1pt = 3px
    r=f&~op
    lbl=measure.label(r,connectivity=2)
    c=[]
    for p in measure.regionprops(lbl):
        L=p.major_axis_length/S
        if L>=3:
            y0,x0,y1,x1=p.bbox
            c.append((round(L,1), round(p.area/9,2), round(p.minor_axis_length/S,2), round(cx0+x0/S,1),round(cx0+x1/S,1),round(cy0+y0/S,1),round(cy0+y1/S,1)))
    c.sort(reverse=True)
    print(a['id'],'fin candidates',len(c))
    for x in c[:25]: print('   len %.1fpt area %.2fpt2 width %.2fpt  x %.1f-%.1f y %.1f-%.1f'%x)
    # overlay
    vis=Image.open(a['files']['isolated']).convert('RGB'); d=ImageDraw.Draw(vis)
    for x in c:
        X0=(x[3]-cx0)*S; X1=(x[4]-cx0)*S; Y0=(x[5]-cy0)*S; Y1=(x[6]-cy0)*S
        d.rectangle([X0-2,Y0-2,X1+2,Y1+2],outline=(255,0,0),width=2)
    vis.save('fins_%s.png'%a['id'])
