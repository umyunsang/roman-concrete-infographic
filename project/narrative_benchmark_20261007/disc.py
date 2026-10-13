from PIL import Image
import numpy as np, json
from scipy import ndimage as ndi
im=np.asarray(Image.open('../nb_work/review_loop/r9/poster_2x.png').convert('RGB')).astype(float)
mo=np.asarray(Image.open('../nb_work/review_loop/r9/map_only_2x.png').convert('RGB')).astype(float)
def lin(c):
    c=c/255.0
    return np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4)
def Yf(a): return 0.2126*lin(a[...,0])+0.7152*lin(a[...,1])+0.0722*lin(a[...,2])
Y=Yf(im); Ym=Yf(mo)
spec={t[0]:t for t in json.load(open('../nb_work/review_loop/text_spec_r9.json'))['texts']}
for id in ['790:102','790:105','790:110','790:111','790:106']:
    x,y,w,h=spec[id][1]
    X0,Y0,X1,Y1=int(x*2)-4,int(y*2)-2,int((x+w)*2)+4,int((y+h)*2)+2
    d=(Y[Y0:Y1,X0:X1]-Ym[Y0:Y1,X0:X1])>0.1
    g=np.sort(Y[Y0:Y1,X0:X1][d])[::-1]; dig=g[:max(1,len(g)//5)].mean()
    gm=ndi.binary_dilation(d,iterations=2)
    # disc pixels: red in map-only and not glyph
    M=mo[Y0:Y1,X0:X1]; red=(M[...,0]-M[...,1]>40)&~gm
    bg95=np.percentile(Y[Y0:Y1,X0:X1][red],95)
    print(id, spec[id][4][0][0], 'contrast digit/disc(p95) %.2f'%((dig+.05)/(bg95+.05)))
