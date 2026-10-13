from PIL import Image
import numpy as np, json
im=np.asarray(Image.open('../nb_work/review_loop/r9/poster_2x.png').convert('RGB')).astype(float)
mo=np.asarray(Image.open('../nb_work/review_loop/r9/map_only_2x.png').convert('RGB')).astype(float)
def lum(a): return 0.2126*a[...,0]+0.7152*a[...,1]+0.0722*a[...,2]
L=lum(im); Lm=lum(mo)
spec={t[0]:t for t in json.load(open('../nb_work/review_loop/text_spec_r9.json'))['texts']}
for a in ['790:146','790:152','790:158','790:164','790:170']:
    x,y,w,h=spec[a][1]
    Y0,Y1=int(y*2)+4,int((y+h)*2)-4
    # disc right edge: redness profile in map-only along rows, max over rows of red fraction
    X0,X1=int(x*2)-40,int(x*2)+30
    M=mo[Y0:Y1,X0:X1]; red=np.clip(((M[...,0]-M[...,1])-0)/ (np.percentile(M[...,0]-M[...,1],99)+1e-6),0,1)
    colred=red.max(0)
    # find last column where colred>=0.5 then interpolate
    idx=np.nonzero(colred>=0.5)[0]; i=idx.max()
    fr=colred[i+1]/1.0 if i+1<len(colred) else 0
    disc_r=(X0+i+0.5+ (colred[i]-0.5)/(colred[i]-colred[i+1]+1e-9) )/2
    # text left: darkness profile from diff
    D=np.clip((Lm[Y0:Y1,X0:X1]-L[Y0:Y1,X0:X1])/ (np.percentile(Lm[Y0:Y1,X0:X1]-L[Y0:Y1,X0:X1],99.5)+1e-6),0,1)
    D[:, :int(disc_r*2)-X0+2]=0
    cold=D.max(0)
    j=np.nonzero(cold>=0.5)[0].min()
    txt_l=(X0+j-0.5+(0.5-cold[j-1])/(cold[j]-cold[j-1]+1e-9))/2
    print(a, spec[a][4][0][0][:6], 'disc right %.2f  text left %.2f  gap %.2f'%(disc_r,txt_l,txt_l-disc_r))
