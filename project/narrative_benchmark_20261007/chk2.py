import json, numpy as np
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
P=np.asarray(Image.open(R+'r9/poster_2x.png').convert('RGB')).astype(int)
M=np.asarray(Image.open(R+'r9/map_only_2x.png').convert('RGB')).astype(int)
T=json.load(open(R+'text_spec_r9.json'))['texts']
mask=np.zeros(P.shape[:2],bool)
for t in T:
    x,y,w,h=t[1]
    mask[max(0,int((y-6)*2)):int((y+h+6)*2), max(0,int((x-6)*2)):int((x+w+6)*2)]=True
d=np.abs(P-M).sum(2)
out=~mask
print('outside text: mean',d[out].mean(),'p99',np.percentile(d[out],99),'frac>24',(d[out]>24).mean())
print('signed mean diff P-M outside', (P-M)[out].mean(0))
# where outside diff>24
ys,xs=np.where((d>24)&out)
if len(ys):
    H,_=np.histogram(ys//200,bins=range(0,18)); print('rows/100pt',H)
    Hx,_=np.histogram(xs//200,bins=range(0,13)); print('cols/100pt',Hx)
