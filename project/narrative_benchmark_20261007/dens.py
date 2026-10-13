import json, numpy as np
from PIL import Image, ImageFilter
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
T=json.load(open(R+'text_spec_r10.json'))['texts']
im=Image.open(R+'r10/poster_1x.png').convert('RGB')
A=np.asarray(im.filter(ImageFilter.GaussianBlur(0.8))).astype(np.float32)
L=0.299*A[...,0]+0.587*A[...,1]+0.114*A[...,2]
gx=np.zeros_like(L);gy=np.zeros_like(L)
gx[:,1:-1]=(L[:,2:]-L[:,:-2])/2; gy[1:-1,:]=(L[2:,:]-L[:-2,:])/2
G=np.hypot(gx,gy)
raw=np.asarray(im).astype(np.int16)
cyan=raw[...,2]>raw[...,0]+15
obj=(G>8)|cyan
H,W=obj.shape
txt=np.zeros_like(obj)
for t in T:
    x,y,w,h=t[1]; txt[int(y):int(np.ceil(y+h)),int(x):int(np.ceil(x+w))]=True
# coastline per column: first row (from top, y>=240) where cyan dominates contiguous sea below
coast=np.full(W,H)
for x in range(W):
    col=cyan[:,x]
    # find first y>=1300 where following 30 rows mostly cyan
    for y in range(1250,H-30):
        if col[y:y+30].mean()>0.8: coast[x]=y;break
C=(584,783)
cells=[]
n=20
gy_=list(range(240,H,n)); gx_=list(range(0,W,n))
E=np.zeros((len(gy_),len(gx_)),bool); valid=np.zeros_like(E); ratio=np.zeros(E.shape)
for i,y in enumerate(gy_):
    for j,x in enumerate(gx_):
        y1=min(y+n,H); x1=min(x+n,W)
        if y1>coast[x:x1].min(): continue
        valid[i,j]=True
        hasT=txt[y:y1,x:x1].any()
        r=(obj[y:y1,x:x1]&~txt[y:y1,x:x1]).mean()
        ratio[i,j]=r if not hasT else np.nan
        cx,cy=x+n/2,y+n/2
        if (not hasT) and r<0.02 and np.hypot(cx-C[0],cy-C[1])<=450: E[i,j]=True
# largest rectangle of True in E
best=(0,None)
rows,cols=E.shape
h=np.zeros(cols,int)
for i in range(rows):
    h=np.where(E[i],h+1,0)
    st=[]
    for j in range(cols+1):
        cur=h[j] if j<cols else 0
        start=j
        while st and st[-1][1]>=cur:
            s,hh=st.pop()
            area=hh*(j-s)
            if area>best[0]: best=(area,(i-hh+1,s,i,j-1))
            start=s
        st.append((start,cur))
a,(i0,j0,i1,j1)=best
print('LY-25 largest empty rect cells',a,'area pt2',a*n*n,'x %d-%d y %d-%d'%(gx_[j0],gx_[j1]+n,gy_[i0],gy_[i1]+n))
print('empty cells within 450:',E.sum())
# LY-26
land=ratio[valid & ~np.isnan(ratio)]
cores=json.load(open('cores.json'))
for k,v in cores.items():
    x0,y0,x1,y1=v[4]
    X0,Y0,X1,Y1=int(x0-30),int(y0-30),int(np.ceil(x1+30)),int(np.ceil(y1+30))
    ring=np.zeros_like(obj); ring[max(Y0,0):Y1,max(X0,0):X1]=True; ring[int(y0):int(np.ceil(y1)),int(x0):int(np.ceil(x1))]=False
    ring&=~txt
    r=obj[ring].mean()
    pct=(land<=r).mean()*100
    print('CORE',k,'ring ratio %.3f percentile %.1f'%(r,pct))
print('land cell ratio p50 %.3f p75 %.3f p90 %.3f'%tuple(np.percentile(land,[50,75,90])))
