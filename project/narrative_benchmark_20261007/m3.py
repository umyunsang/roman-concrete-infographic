import json, numpy as np, sys
from PIL import Image
from skimage import color
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx=json.load(open(B+'assets_index.json')); A={a['id']:a for a in idx['assets']}
def dump(aid, X0,X1,Y0,Y1, which='isolated_rgba'):
    a=A[aid]; x0,x1,y0,y1=a['crop_pt']
    im=np.asarray(Image.open(a['files'][which]).convert('RGBA')).astype(float)/255
    c0=int(round((X0-x0)*3)); c1=int(round((X1-x0)*3)); r0=int(round((Y0-y0)*3)); r1=int(round((Y1-y0)*3))
    sub=im[r0:r1,c0:c1]
    L=color.rgb2lab(sub[...,:3])[...,0]
    al=sub[...,3]
    print('##',aid,which,'x %.1f-%.1f y %.1f-%.1f'%(X0,X1,Y0,Y1),'(rows=y, cols=x; L*; alpha<0.98 marked with ~)')
    for r in range(sub.shape[0]):
        print(' '.join(('%3d'%L[r,c])+('~' if al[r,c]<0.98 else ' ') for c in range(sub.shape[1])))
dump('shape_pin_harbor',195.5,200.5,1494.8,1499.2)
dump('shape_d2_leader',125.8,131.0,1004.8,1009.2)
dump('shape_pin_pompeii',721.8,726.5,1491.8,1496.6)
