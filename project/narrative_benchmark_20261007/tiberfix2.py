import sys, json, numpy as np
sys.path.insert(0,'.')
from fake import *
from scipy.spatial import cKDTree
from PIL import Image
from masks import srgb2lab
P=np.array(Image.open(BASE_P:='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/r11/poster_2x.png').convert('RGB')).astype(float)
x,y,w,h=108.4,434.6,51.1,29.5
X0,Y0,X1,Y1=int((x-2)*2),int((y-2)*2),int((x+w+2)*2),int((y+h+2)*2)
L=srgb2lab(P[Y0:Y1,X0:X1])[...,0]
ys,xs=np.nonzero(L<65); ink=np.stack([(X0+xs+0.5)/2,(Y0+ys+0.5)/2],1)
def pts_of(cond):
    ys,xs=np.nonzero(cond); return np.stack([(xs+0.5)/S,(ys+0.5)/S],1)
# river visible mask (L02 + marks over river) ; all other object masks (any asset except ground)
codes_river=[name2idx['L02_tiber']+1]
yy=(np.arange(H)*code.shape[0]/H).astype(int); xx=(np.arange(W)*code.shape[1]/W).astype(int)
sub=(slice(int(380*S),int(560*S)),slice(int(60*S),int(300*S)))
c3=code[yy][:,xx][sub]
river=np.isin(c3,codes_river)
ground_code=name2idx['T_land']+1
others=(c3>=1)&(c3!=ground_code)&~river&~np.isin(c3,[name2idx['W_water_marks']+1])
off=np.array([60*S,380*S])/S
rp=pts_of(river)+[60,380]; op=pts_of(others)+[60,380]
tr=cKDTree(rp); to=cKDTree(op)
for dx in range(0,41,4):
  for dy in (-8,-4,0,4,8):
    p=ink+[dx,dy]
    do=tr.query(p)[0].min(); dt=to.query(p)[0].min()
    if 6<=do<=16: print('dx',dx,'dy',dy,'d_river',round(do,1),'d_nearest_other_object(incl fields)',round(dt,1))
print('orig', round(tr.query(ink)[0].min(),1), round(to.query(ink)[0].min(),1))
