import sys; sys.path.insert(0,"/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/ov3")
from lib import *
m2=np.asarray(Image.open('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/r11/map_only_2x.png').convert('RGB'))
id2=np.load(W+'id2x.npy')
L2=Lstar(m2)
np.save('L2.npy',L2.astype(np.float32))
# alignment test: road appia mask edges vs L gradient
for nm,(x0,x1,y0,y1) in [('R_via_appia',(900,1100,930,1000)),('T_pine.004',(840,900,1285,1355)),('R_via_ostiensis',(100,400,1000,1460)),('L10_sea',(500,1100,1330,1450))]:
    ys=slice(y0*2,y1*2); xs=slice(x0*2,x1*2)
    best=[]
    for dy in range(-3,4):
        for dx in range(-3,4):
            m=(id2==NID[nm]).astype(float)
            m=np.roll(np.roll(m,dy,0),dx,1)[ys,xs]
            l=L2[ys,xs]
            # contrast of means inside vs outside near edge
            e=ndi.binary_dilation(m>0,iterations=2)&~ndi.binary_erosion(m>0,iterations=2)
            inn=(m>0)&e; out=(~(m>0))&e
            best.append((abs(l[inn].mean()-l[out].mean()),dy,dx))
    best.sort(reverse=True); print(nm,best[:3])
