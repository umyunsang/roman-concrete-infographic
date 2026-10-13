import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
spec={t[0]:t for t in json.load(open(R+'text_spec_r10.json'))['texts']}
P=np.asarray(Image.open(R+'r10/poster_2x.png').convert('RGB')).astype(np.float32)
L=0.299*P[...,0]+0.587*P[...,1]+0.114*P[...,2]
gx=np.zeros_like(L);gy=np.zeros_like(L)
gx[:,1:-1]=(L[:,2:]-L[:,:-2])/2; gy[1:-1,:]=(L[2:,:]-L[:-2,:])/2
G=np.hypot(gx,gy)
ink=np.load('ink.npy')
# rubric ink = L<140 ; use diff-ink union
inkr=ink|(L<140)
dil=ndi.binary_dilation(inkr,iterations=4)
for tid,name in [('790:148','CORE1'),('790:154','CORE2'),('790:160','CORE3'),('790:166','CORE4'),('790:172','CORE5'),('790:175','DET 해수'),('790:178','DET 제작'),('790:181','DET 구조'),('790:184','DET 메움')]:
    x,y,w,h=spec[tid][1]
    x0,y0,x1,y1=[int(round(v*2)) for v in (x-1,y-1,x+w+1,y+h+1)]
    m=~dil[y0:y1,x0:x1]
    gv=G[y0:y1,x0:x1][m]; lv=L[y0:y1,x0:x1][m]
    print(f"{name:10s} {tid} tex%={100*(gv>12).mean():.2f} p95-p5={np.percentile(lv,95)-np.percentile(lv,5):.1f}  Lmin={lv.min():.0f} Lmean={lv.mean():.0f}")
