import sys; sys.path.insert(0,'lib')
from m import *
a,rgb,al,ctx=load('ground_land')
lw=np.load('ground_lw.npy'); mask=al>127
x0,x1,y0,y1=a['crop_pt']
# final poster with text, 2x
P=np.asarray(Image.open('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/r11/poster_2x.png').convert('RGB')).astype(float)
print('poster2x',P.shape)
H,W=lw.shape
# sample poster at each crop pixel
yy,xx=np.mgrid[0:H,0:W]
px_=np.clip(((x0+(xx+0.5)/3)*2).astype(int),0,P.shape[1]-1); py_=np.clip(((y0+(yy+0.5)/3)*2).astype(int),0,P.shape[0]-1)
Pc=P[py_,px_]
vis=mask&(np.abs(Pc-rgb).max(-1)<=8)
lwv=lw&vis
lb,nb=ndi.label(lwv); sz=ndi.sum(lwv,lb,range(1,nb+1)); com=ndi.center_of_mass(lwv,lb,range(1,nb+1))
T=json.load(open('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/text_spec_r11.json'))['texts']
LIME_IDS=['790:108','790:109','790:112','790:113','790:154','790:159','790:160','790:165','790:166','790:178','790:183','790:184','790:186','790:187','790:188','790:189','790:127','790:90','790:172','798:78','797:78','790:123','790:126','790:174','790:175','790:177','790:171']
boxes={t[0]:t[1] for t in T if t[0] in LIME_IDS}
def dist(bx,x,y):
    X,Y,Wb,Hb=bx; dx=max(X-x,0,x-(X+Wb)); dy=max(Y-y,0,y-(Y+Hb)); return (dx*dx+dy*dy)**0.5
near=[]
for k,(s,c) in enumerate(zip(sz,com)):
    if s<9: continue
    x=x0+c[1]/3; y=y0+c[0]/3
    # use blob pixel min distance
    ys,xs=np.where(lb==k+1)
    best=(1e9,None)
    for tid,bx in boxes.items():
        d=min(dist(bx,x0+xx_/3,y0+yy_/3) for xx_,yy_ in zip(xs[::max(1,len(xs)//50)],ys[::max(1,len(ys)//50)]))
        if d<best[0]: best=(d,tid)
    if best[0]<=60: near.append((round(s/9,1),round(x),round(y),best[1],round(best[0],1)))
print('visible lw blobs >=1pt2:', int((sz>=9).sum()), ' total pt2', round(sz[sz>=9].sum()/9,1))
print('within 60pt of lime-concept text:', len(near), 'total pt2', round(sum(n[0] for n in near),1))
for n in sorted(near,key=lambda t:-t[0])[:30]: print(n)
np.save('lw_near.npy',np.array([[n[1],n[2],n[0]] for n in near]))
