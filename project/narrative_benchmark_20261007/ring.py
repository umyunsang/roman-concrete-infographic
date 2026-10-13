import numpy as np, colour, warnings
warnings.filterwarnings('ignore')
from PIL import Image
from scipy import ndimage
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
M=np.array(Image.open(R+'r11/map_only_2x.png').convert('RGB')).astype(float)/255
H,W=M.shape[:2]
yy,xx=np.mgrid[0:H,0:W]
px=(xx+.5)/2; py=(yy+.5)/2
segs=[(390.7,401.2,1221,1245),(388.2,403.2,1245,1272),(386.2,405.7,1272,1300.5),(384.7,407.2,1300.5,1315.6)]
sl=(slice(int(1200*2),int(1340*2)),slice(int(360*2),int(430*2)))
col=np.zeros((H,W),bool)
for x0,x1,y0,y1 in segs: col|=(px>=x0)&(px<=x1)&(py>=y0)&(py<=y1)
c=col[sl]; sub=M[sl]
er=ndimage.binary_erosion(c,iterations=2)
d6=ndimage.binary_dilation(c,iterations=12); d2=ndimage.binary_dilation(c,iterations=4)
ring=d6&~d2
lab=lambda rgb: colour.XYZ_to_Lab(colour.sRGB_to_XYZ(rgb))
cm=lab(np.median(sub[er],axis=0)); rm=lab(np.median(sub[ring],axis=0))
print('column median Lab',np.round(cm,1),'ring',np.round(rm,1),'dL',round(cm[0]-rm[0],1),'dE00',round(float(colour.delta_E(cm,rm,method='CIE 2000')),1))
