import sys
from PIL import Image
import numpy as np
im=np.array(Image.open(sys.argv[1]).convert('RGB')).astype(int)
def mask(x0,y0,x1,y1,bg,thr=28):
    sub=im[int(y0*2):int(y1*2),int(x0*2):int(x1*2)]
    return np.abs(sub-np.array(bg)).sum(axis=2)>thr
def cols(x0,y0,x1,y1,bg,thr=28):
    m=mask(x0,y0,x1,y1,bg,thr)
    return m.sum(axis=0)
def rows(x0,y0,x1,y1,bg,thr=28):
    m=mask(x0,y0,x1,y1,bg,thr)
    return m.sum(axis=1)
def bgsample(x0,y0,x1,y1):
    sub=im[int(y0*2):int(y1*2),int(x0*2):int(x1*2)].reshape(-1,3)
    vals,counts=np.unique(sub//4,axis=0,return_counts=True)
    return vals[counts.argmax()]*4+2
import json
# Privernum: label text x 899-1026, y1020-1078; object right
b=bgsample(960,1080,1010,1100); print('bg',b)
c=cols(960,1000,1140,1100,b,40)
xs=[960+i/2 for i,v in enumerate(c) if v>3]
print('privernum: nonbg columns from',xs[:3],'...')
# Print column profile coarse
print(' '.join('%.0f:%d'%(960+i/2,v) for i,v in enumerate(c) if i%4==0))
# Ruin observation scene: label y1250 box; object above
b2=bgsample(860,1262,980,1275); print('bg2',b2)
r=rows(866,1120,965,1265,b2,40)
print(' '.join('%.1f:%d'%(1120+i/2,v) for i,v in enumerate(r) if i>=220))
