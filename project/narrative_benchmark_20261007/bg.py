from PIL import Image
import numpy as np, json
from scipy import ndimage as ndi
im=np.asarray(Image.open('../nb_work/review_loop/r9/poster_2x.png').convert('RGB')).astype(float)
mo=np.asarray(Image.open('../nb_work/review_loop/r9/map_only_2x.png').convert('RGB')).astype(float)
def lum709(a): return 0.2126*a[...,0]+0.7152*a[...,1]+0.0722*a[...,2]
L=lum709(im); Lm=lum709(mo)
def lin(c):
    c=c/255.0
    return np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4)
Y=0.2126*lin(im[...,0])+0.7152*lin(im[...,1])+0.0722*lin(im[...,2])
spec=json.load(open('../nb_work/review_loop/text_spec_r9.json'))['texts']
rows=[]
for t in spec:
    id,box,rot,al,segs=t
    x,y,w,h=box
    pad=8
    x0,y0,x1,y1=[int(round(v*2)) for v in (x,y,x+w,y+h)]
    X0,Y0,X1,Y1=max(0,x0-pad),max(0,y0-pad),min(2382,x1+pad),min(3368,y1+pad)
    d=L[Y0:Y1,X0:X1]-Lm[Y0:Y1,X0:X1]
    txt=np.abs(d)>25
    if txt.sum()==0:
        print(id,'NO INK'); continue
    yy,xx=np.nonzero(txt)
    ix0,iy0,ix1,iy1=xx.min()+X0,yy.min()+Y0,xx.max()+X0+1,yy.max()+Y0+1
    # ink box +2pt (4px)
    bx0,by0,bx1,by1=max(0,ix0-4),max(0,iy0-4),min(2382,ix1+4),min(3368,iy1+4)
    reg=Lm[by0:by1,bx0:bx1]
    # glyph mask in poster: difference dilated by 2px
    dd=np.abs(L[by0:by1,bx0:bx1]-Lm[by0:by1,bx0:bx1])>12
    gm=ndi.binary_dilation(dd,iterations=2)
    bgp=L[by0:by1,bx0:bx1][~gm]
    std_mo=reg.std()
    std_bg=bgp.std()
    # contrast
    Yb=Y[by0:by1,bx0:bx1]
    glyph=Yb[dd]
    if glyph.size==0: continue
    gs=np.sort(glyph); ink=gs[:max(1,len(gs)//5)].mean()
    bgY=np.percentile(Yb[~gm],5) if (~gm).sum()>0 else np.nan
    bgY50=np.percentile(Yb[~gm],50)
    cr=(bgY+0.05)/(ink+0.05); cr50=(bgY50+0.05)/(ink+0.05)
    rng=np.percentile(reg,99)-np.percentile(reg,1)
    rows.append((id,segs[-1][0].replace('\n','/')[:22],rot,(ix0/2,iy0/2,ix1/2,iy1/2),round(std_mo,2),round(std_bg,2),round(rng,1),round(cr,2),round(cr50,2)))
for r in rows:
    flag=''
    if r[4]>6 or r[5]>6: flag+=' STD>6'
    if r[7]<4.5: flag+=' CR<4.5'
    print(r,flag)
