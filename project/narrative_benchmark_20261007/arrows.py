import numpy as np, math
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/r10/'
im=np.asarray(Image.open(R+'map_only_2x.png').convert('RGB')).astype(int)
S=2
boxes={'1->2':((440,355,530,465),(137.5,768.5),'L'),'2->3':((185,895,275,1010),(503.5,1052.5),'R'),'4->5':((765,895,860,1010),(1072.5,837.5),'R')}
for k,((x0,y0,x1,y1),tgt,side) in boxes.items():
    sub=im[y0*S:y1*S,x0*S:x1*S]
    r,g,b=sub[...,0],sub[...,1],sub[...,2]
    m=(r>g+50)&(r>b+60)&(r>90)
    ys,xs=np.nonzero(m)
    X=xs/S+x0; Y=ys/S+y0
    cx,cy=X.mean(),Y.mean()
    C=np.cov(np.vstack([X-cx,Y-cy]))
    w,v=np.linalg.eigh(C); ax=v[:,np.argmax(w)]
    if (side=='L' and ax[0]>0) or (side=='R' and ax[0]<0): ax=-ax
    proj=(X-cx)*ax[0]+(Y-cy)*ax[1]
    tipi=np.argmax(proj); tip=(X[tipi],Y[tipi])
    ang=math.degrees(math.atan2(-ax[1],ax[0]))
    # tip-tail vector from extremes
    taili=np.argmin(proj); tail=(X[taili],Y[taili])
    ang_tt=math.degrees(math.atan2(-(tip[1]-tail[1]),tip[0]-tail[0]))
    vt=(tgt[0]-cx,tgt[1]-cy); angt=math.degrees(math.atan2(-vt[1],vt[0]))
    def diff(a,b):
        d=(a-b+180)%360-180; return abs(d)
    print(f'{k}: n={len(X)} centroid ({cx:.1f},{cy:.1f}) bbox x {X.min():.1f}-{X.max():.1f} y {Y.min():.1f}-{Y.max():.1f}')
    print(f'   PCA dir {ang:.1f}deg, tip-tail dir {ang_tt:.1f}deg (tip {tip[0]:.1f},{tip[1]:.1f}), target dir {angt:.1f}deg, dist {math.hypot(*vt):.0f}pt -> diff PCA {diff(ang,angt):.1f}, tip-tail {diff(ang_tt,angt):.1f}')
