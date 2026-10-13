import numpy as np, json
from PIL import Image
from skimage import color, measure
A='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/assets/fields_sw'
ctx=np.asarray(Image.open(f'{A}/context.png').convert('RGB')).astype(float)/255
iso=np.asarray(Image.open(f'{A}/isolated_rgba.png')).astype(float)/255
al=iso[...,3]
Lc=color.rgb2lab(ctx); Li=color.rgb2lab(iso[...,:3])
terr=np.median(Lc[al<0.01],axis=0)
dci=color.deltaE_ciede2000(Lc,Li); dct=color.deltaE_ciede2000(Lc,np.broadcast_to(terr,Lc.shape))
# class map: 1 = plate-like (matches iso), 2 = terrain-like
cls=np.zeros(al.shape,int)
cls[(al>0.5)&(dci<5)]=1
cls[(al>0.5)&(dct<8)&(dci>8)]=2
x0,y0=0.0,1036.9
def px(xpt,ypt): return int(round((xpt-x0)*3)), int(round((ypt-y0)*3))
# region of poke
for name,(a,b,c,d) in {'poke':(185,216,1072,1106),'vine':(50,68,1258,1272)}.items():
    X0,Y0=px(a,c); X1,Y1=px(b,d)
    sub=cls[Y0:Y1,X0:X1]
    print(name,'plate px',(sub==1).sum()/9,'pt2 terrain-inside-iso px',(sub==2).sum()/9,'pt2')
    # transitions along rows and cols within 3pt (9px) windows
    best=0; where=None
    for axis in (0,1):
        arr=sub if axis==0 else sub.T
        for i,row in enumerate(arr):
            seq=[v for v in row]
            for s in range(0,len(seq)-9):
                w=[v for v in seq[s:s+9] if v>0]
                tr=sum(1 for k in range(1,len(w)) if w[k]!=w[k-1])
                if tr>best: best=tr; where=(axis,i,s)
    print(' max transitions in 3pt segment (rows/cols):',best,where)
    # components of terrain-like inside iso
    lbl=measure.label(sub==2,connectivity=2)
    for r in measure.regionprops(lbl):
        if r.area>=4: 
            cy,cx=r.centroid; print('  comp area %.2f pt2 at pt (%.1f,%.1f) bbox %s'%(r.area/9,x0+(X0+cx)/3,y0+(Y0+cy)/3,r.bbox))
    Image.fromarray((np.stack([sub==2,sub==1,np.zeros_like(sub)],-1)*255).astype(np.uint8)).resize((sub.shape[1]*6,sub.shape[0]*6),Image.NEAREST).save(f'cls_{name}.png')
