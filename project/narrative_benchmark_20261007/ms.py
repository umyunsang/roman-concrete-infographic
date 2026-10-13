import json, numpy as np, math
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
M=np.asarray(Image.open(R+'r10/map_only_2x.png').convert('RGB')).astype(np.int16)
red=(M[...,0]-M[...,1]>45)&(M[...,0]>90)&(M[...,1]<100)&(M[...,2]<100)
cores=json.load(open('cores.json'))
for k,v in cores.items():
    x0,y0,x1,y1=v[4]; red[int((y0-3)*2):int((y1+3)*2),int((x0-3)*2):int((x1+3)*2)]=False
# also exclude ③ cube, ④ cubes (brown) -> they are brown not red; check clusters
lab,n=ndi.label(ndi.binary_dilation(red,iterations=2))
C={k:(v[0],v[1]) for k,v in cores.items()}
for i in range(1,n+1):
    mm=(lab==i)&red
    if mm.sum()<300: continue
    ys,xs=np.nonzero(mm); xs=xs/2; ys=ys/2
    cx,cy=xs.mean(),ys.mean()
    # principal axis
    cov=np.cov(np.vstack([xs-cx,ys-cy])); w,V=np.linalg.eigh(cov); ax=V[:,1]
    proj=(xs-cx)*ax[0]+(ys-cy)*ax[1]
    # width perpendicular at each end: arrow head wider
    perp=(xs-cx)*(-ax[1])+(ys-cy)*ax[0]
    lo=proj<np.percentile(proj,25); hi=proj>np.percentile(proj,75)
    wl=np.ptp(perp[lo]); wh=np.ptp(perp[hi])
    print('cluster bbox (%.0f,%.0f)-(%.0f,%.0f) n=%d center (%.1f,%.1f) axis (%.2f,%.2f) width low-end %.1f high-end %.1f'%(xs.min(),ys.min(),xs.max(),ys.max(),mm.sum(),cx,cy,ax[0],ax[1],wl,wh))
