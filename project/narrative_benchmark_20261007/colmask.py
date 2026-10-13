import numpy as np, json
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from skimage import color, measure, morphology
A='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/assets/landmark_colosseum/'
im=np.asarray(Image.open(A+'isolated_rgba.png')).astype(float)
al=im[...,3]/255; rgb=im[...,:3]/255
lab=color.rgb2lab(rgb)
C=np.hypot(lab[...,1],lab[...,2])
# podium sample: around crop px (200,1150)
for p in [(100,1000),(300,1250),(1400,1050),(800,1330)]:
    x,y=p; print('pod?',p,lab[y,x].round(1),C[y,x].round(1),al[y,x])
for p in [(600,1000),(800,700),(300,600)]:
    x,y=p; print('wall?',p,lab[y,x].round(1),C[y,x].round(1))
