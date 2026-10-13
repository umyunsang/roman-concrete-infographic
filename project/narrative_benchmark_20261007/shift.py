import numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/r10/'
P=np.asarray(Image.open(R+'poster_2x.png').convert('L')).astype(float)
M=np.asarray(Image.open(R+'map_only_2x.png').convert('L')).astype(float)
X0,Y0,X1,Y1=250*2,460*2,420*2,545*2
p=P[Y0:Y1,X0:X1]; m=M[Y0:Y1,X0:X1]
ink=np.abs(p-m)>12
bx=np.zeros_like(ink); bx[(494-460)*2:(509-460)*2,(296-250)*2:(384-250)*2]=True; ink&=bx
paper=np.median(m)
obj=m<paper-22   # objects/outlines darker than paper (field patches, Pantheon, shadows)
obj=ndi.binary_opening(obj,iterations=1)
dt=ndi.distance_transform_edt(~obj)/2  # pt
ys,xs=np.nonzero(ink)
print('paper',paper,'ink px',len(xs),'ink x %.1f-%.1f y %.1f-%.1f'%(250+xs.min()/2,250+xs.max()/2,460+ys.min()/2,460+ys.max()/2))
best=[]
for dx in range(-6,7):
    for dy in range(-8,9):
        yy=ys+dy*2; xx=xs+dx*2
        ok=(yy>=0)&(yy<dt.shape[0])&(xx>=0)&(xx<dt.shape[1])
        g=dt[yy[ok],xx[ok]].min()
        best.append((g,dx,dy))
cur=[b for b in best if b[1]==0 and b[2]==0][0]
print('current min gap ink->object: %.2f pt'%cur[0])
for b in sorted(best,key=lambda b:(-b[0],abs(b[1])+abs(b[2])))[:12]: print('dx %+d dy %+d -> min gap %.2f pt'%(b[1],b[2],b[0]))
for dx,dy in [(3,0),(2,0),(0,3),(0,4),(0,-3),(2,2)]:
    print('candidate',dx,dy,[ '%.2f'%b[0] for b in best if b[1]==dx and b[2]==dy])
