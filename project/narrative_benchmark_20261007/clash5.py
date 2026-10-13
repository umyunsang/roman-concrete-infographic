import numpy as np
from PIL import Image
import sys; sys.path.insert(0,'.')
from masks import srgb2lab
P=np.array(Image.open('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/r11/poster_2x.png').convert('RGB')).astype(float)
M=np.array(Image.open('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/r11/map_only_2x.png').convert('RGB')).astype(float)
# text-only difference: pixels where poster differs from map_only
y0,y1,x0,x1=int(1365.9*2),int(1393.9*2),int(250*2),int(415*2)
d=np.abs(P[y0:y1,x0:x1]-M[y0:y1,x0:x1]).sum(-1)
ys,xs=np.nonzero(d>30)
print('text ink (poster-map diff>30) x range pt',(x0+xs.min())/2,(x0+xs.max())/2,'y',(y0+ys.min())/2,(y0+ys.max())/2)
