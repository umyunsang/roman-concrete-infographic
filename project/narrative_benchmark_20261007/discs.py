import numpy as np
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/r10/'
im=np.asarray(Image.open(R+'poster_2x.png').convert('RGB')).astype(int)
S=2
target=np.array([0x98,0x38,0x21])
nums={'1':(534.5,389.5),'2':(64,751.5),'3':(415,1035.6),'4':(645,1035.6),'5':(989,820.5)}
titles={'1':(553,382,149,24.5),'2':(82.5,744,135,24.5),'3':(433.5,1028,165,24.5),'4':(663.5,1028,153,24.5),'5':(1007.5,813,155,24.5)}
for k,(nx,ny) in nums.items():
    cx,cy=nx+4,ny+6
    x0,y0,x1,y1=int((cx-20)*S),int((cy-20)*S),int((cx+20)*S),int((cy+20)*S)
    sub=im[y0:y1,x0:x1]
    d=np.abs(sub-target).sum(2)
    m=d<70
    ys,xs=np.nonzero(m)
    bx0,bx1=(xs.min()+x0)/S,(xs.max()+x0+1)/S
    by0,by1=(ys.min()+y0)/S,(ys.max()+y0+1)/S
    # title first line ink: dark pixels in title row
    tx,ty,tw,th=titles[k]
    X0,Y0,X1,Y1=int((bx1+0.5)*S),int(ty*S),int((tx+tw)*S),int((ty+th)*S)
    t=im[Y0:Y1,X0:X1]
    dark=(t.sum(2)<250)
    cols=np.nonzero(dark.any(0))[0]
    ink0=(cols.min()+X0)/S
    rows=np.nonzero(dark.any(1))[0]
    print(f'disc {k}: x {bx0:.1f}-{bx1:.1f} (w {bx1-bx0:.1f}) y {by0:.1f}-{by1:.1f} (h {by1-by0:.1f}); title ink x0 {ink0:.1f}, ink y {(rows.min()+Y0)/S:.1f}-{(rows.max()+Y0+1)/S:.1f}; gap {ink0-bx1:.1f}pt; disc cy {(by0+by1)/2:.1f}')
