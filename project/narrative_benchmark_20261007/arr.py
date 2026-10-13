import numpy as np, colour, warnings
warnings.filterwarnings('ignore')
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
ov=np.array(Image.open(R+'obj_r11/full/full_overlay_pass.png')).astype(float)
S=2.9992
for y in [1195,1200]:
    r=int(y*S); c0=int(282*S); c1=int(289*S)
    a=ov[r,c0:c1,3]; print('press0 row',y,'width pt', round(a.sum()/255/S,2))
r=int(1200*S); c0=int(291*S); c1=int(298*S); print('press1 width', round(ov[r,c0:c1,3].sum()/255/S,2))
x0,x1,y0,y1=[int(v*S) for v in [283,288,1190,1205]]
sub=ov[y0:y1,x0:x1]; m=sub[...,3]>=250
rgb=np.median(sub[m][:,:3],axis=0)/255; lab=colour.XYZ_to_Lab(colour.sRGB_to_XYZ(rgb))
print('arrow core', '#%02X%02X%02X'%tuple(int(round(v*255)) for v in rgb), np.round(lab,1))
lead=np.array([30.7,-0.2,4.6])
print('dE00 arrow vs leader', round(float(colour.delta_E(lab,lead,method='CIE 2000')),2))
