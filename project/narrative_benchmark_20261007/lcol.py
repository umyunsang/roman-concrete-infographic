import numpy as np, colour, warnings
warnings.filterwarnings('ignore')
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
ov=np.array(Image.open(R+'obj_r11/full/full_overlay_pass.png')).astype(float)
S=2.9992
def core(box,name):
    x0,x1,y0,y1=[int(v*S) for v in box]
    sub=ov[y0:y1,x0:x1]; m=sub[...,3]>=250
    rgb=np.median(sub[m][:,:3],axis=0)/255
    lab=colour.XYZ_to_Lab(colour.sRGB_to_XYZ(rgb))
    print(name, int(m.sum()), '#%02X%02X%02X'%tuple(int(round(v*255)) for v in rgb), np.round(lab,1)); return lab
a=core([128,140,1005,1009],'d2 line')
b=core([125,131,1004,1010],'d2 dot')
c=core([374,390,1230,1234],'d3 lead04')
d=core([314,321,1230,1234],'d3 lead03')
e=core([720,728,1500,1545],'pompeii line')
f=core([195,224,1494,1520],'harbor line+dot')
g=core([382,419,1299,1302],'ground line')
for x,n in [(b,'d2dot'),(c,'d3'),(e,'pomp'),(f,'harb'),(g,'ground')]:
    print('dE00 d2line vs',n, round(float(colour.delta_E(a,x,method='CIE 2000')),2))
# granule coverage by overlay
idm=np.array(Image.open(R+'obj_r11/idpass/id_id_map.png')); ido=np.array(Image.open(R+'obj_r11/idpass/id_id_overlay.png'))
full=(idm[...,0].astype(np.int64)<<16)|(idm[...,1].astype(np.int64)<<8)|idm[...,2]
g=(full==0xce0202)&(idm[...,3]>0)
cov=g&(ido[...,3]>0)
print('D2_lime04 px',int(g.sum()),'covered by overlay',int(cov.sum()), 'visible frac', round(1-cov.sum()/g.sum(),3))
