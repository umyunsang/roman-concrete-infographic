import numpy as np
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/r10/'
im=np.asarray(Image.open(R+'map_only_2x.png').convert('RGB')).astype(int)
S=2
bg=np.array([0xE4,0xD9,0xC4])
def objbox(x0,y0,x1,y1,thr=28):
    sub=im[int(y0*S):int(y1*S),int(x0*S):int(x1*S)]
    m=np.abs(sub-bg).sum(2)>thr
    ys,xs=np.nonzero(m)
    return m, xs/S+x0, ys/S+y0
def mindist(box,x0,y0,x1,y1,thr=28):
    bx,by,bw,bh=box
    m,X,Y=objbox(x0,y0,x1,y1,thr)
    dx=np.maximum(0,np.maximum(bx-X,X-(bx+bw)))
    dy=np.maximum(0,np.maximum(by-Y,Y-(by+bh)))
    d=np.hypot(dx,dy); i=np.argmin(d)
    return d[i],(X[i],Y[i]),len(X)
# label blocks (union of title + sub lines) and search windows for the object
cases={
 'lab (오늘의 실험실)':((982.5,618,180,31.6),(985,652,1165,790)),
 'privernum':((899,1020,127,58.5),(1000,985,1130,1100)),
 'site scene (유적 관찰 장면)':((866,1250,96,14),(860,1110,980,1249)),
 'breakwater label':((385,1591,145,14),(390,1495,500,1590)),
 'pantheon label':((298,496,84,11),(383,440,470,530)),
 'kiln label':((36,701,38,11),(75,620,200,735)),
}
for k,(box,win) in cases.items():
    for thr in (28,40):
        d,p,n=mindist(box,*win,thr=thr)
        print(f'{k:28s} thr{thr}: nearest object px {d:.1f}pt at ({p[0]:.1f},{p[1]:.1f}) n={n}')
