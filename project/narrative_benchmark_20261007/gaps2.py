import numpy as np
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/r10/'
im=np.asarray(Image.open(R+'map_only_2x.png').convert('RGB')).astype(int)
S=2
def bgat(x,y):
    return np.median(im[int(y*S)-4:int(y*S)+4,int(x*S)-4:int(x*S)+4].reshape(-1,3),0)
def mindist(box,win,bgpt,thr=28):
    bx,by,bw,bh=box; x0,y0,x1,y1=win
    bg=bgat(*bgpt)
    sub=im[int(y0*S):int(y1*S),int(x0*S):int(x1*S)]
    m=np.abs(sub-bg).sum(2)>thr
    ys,xs=np.nonzero(m); X=xs/S+x0; Y=ys/S+y0
    dx=np.maximum(0,np.maximum(bx-X,X-(bx+bw))); dy=np.maximum(0,np.maximum(by-Y,Y-(by+bh)))
    d=np.hypot(dx,dy); i=np.argmin(d)
    return d[i],(X[i],Y[i]),len(X),bg
cases={
 'lab (오늘의 실험실) -> bench':((982.5,618,180,31.6),(985,652,1165,790),(1000,655)),
 'privernum -> wall':((899,1020,127,58.5),(1000,985,1130,1100),(1000,1060)),
 'site scene -> ruin':((866,1250,96,14),(860,1110,980,1249),(980,1245)),
 'breakwater label -> block':((385,1591,145,14),(390,1495,500,1590),(395,1588)),
 'pantheon label -> pantheon':((298,496,84,11),(383,440,470,530),(386,520)),
 'pantheon label -> field(left)':((298,496,84,11),(240,470,297.9,530),(290,525)),
 'kiln label -> kiln':((36,701,38,11),(75,620,200,735),(78,700)),
}
for k,(box,win,bgp) in cases.items():
    d,p,n,bg=mindist(box,win,bgp)
    print(f'{k:32s} bg #{int(bg[0]):02X}{int(bg[1]):02X}{int(bg[2]):02X}: nearest obj px {d:.1f}pt at ({p[0]:.1f},{p[1]:.1f}) n={n}')
