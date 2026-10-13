import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
P=np.asarray(Image.open(R+'r10/poster_2x.png').convert('RGB')).astype(float)
M=np.asarray(Image.open(R+'r10/map_only_2x.png').convert('RGB')).astype(float)
def L709(a): return 0.2126*a[...,0]+0.7152*a[...,1]+0.0722*a[...,2]
LP=L709(P); LM=L709(M); D=np.abs(P-M).sum(2)
X0,Y0,X1,Y1=1000*2,1235*2,1100*2,1300*2
G=(D[Y0:Y1,X0:X1]>40)&(LP[Y0:Y1,X0:X1]<LM[Y0:Y1,X0:X1])
lm=LM[Y0:Y1,X0:X1]
paperL=np.percentile(lm,90)
print('paperL',paperL)
dist=ndi.distance_transform_edt(~G)
for d in (6,10,15,25):
    O=ndi.binary_opening(lm<paperL-d,iterations=1)
    k=np.argmin(np.where(O,dist,1e9)); qy,qx=np.unravel_index(k,O.shape)
    print('L drop',d,'gap pt',dist[qy,qx]/2,'at',((X0+qx)/2,(Y0+qy)/2), 'L there',lm[qy,qx])
# also lighter-than-paper (rim highlights)
O=ndi.binary_opening(lm>paperL+8,iterations=1)
if O.sum():
    k=np.argmin(np.where(O,dist,1e9)); qy,qx=np.unravel_index(k,O.shape); print('bright gap',dist[qy,qx]/2,((X0+qx)/2,(Y0+qy)/2))
