import numpy as np, json
from PIL import Image, ImageCms
Image.MAX_IMAGE_PIXELS=None
RV='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
W='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/'
srgb=ImageCms.createProfile('sRGB'); pso=ImageCms.getOpenProfile(W+'PSOcoated_v3.icc')
tb=ImageCms.buildTransform(pso,srgb,'CMYK','RGB',renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC,flags=ImageCms.Flags.BLACKPOINTCOMPENSATION)
tn=ImageCms.buildTransform(pso,srgb,'CMYK','RGB',renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC,flags=0)
vec=np.asarray(Image.open('print_vec_300.tif'))
img=Image.open('print_img_300.tif')
bgB=np.asarray(ImageCms.applyTransform(img,tb)).astype(np.float64)
bgN=np.asarray(ImageCms.applyTransform(img,tn)).astype(np.float64)
vm=np.load('vmask.npy')
def lin(c):
    c=c/255.0; return np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4)
def Y(rgb): l=lin(np.asarray(rgb,dtype=np.float64)); return 0.2126*l[...,0]+0.7152*l[...,1]+0.0722*l[...,2]
def wcag(y1,y2): a,b=max(y1,y2),min(y1,y2); return (a+0.05)/(b+0.05)
def apca(txt,bg):
    def ys(c):
        c=np.asarray(c,dtype=np.float64)/255; y=0.2126729*c[0]**2.4+0.7151522*c[1]**2.4+0.0721750*c[2]**2.4
        return y+(0.022-y)**1.414 if y<0.022 else y
    yt,yb=ys(txt),ys(bg)
    if yb>yt: S=(yb**0.56-yt**0.57)*1.14; return 0 if abs(S)<0.1 else (S-0.027)*100
    S=(yb**0.65-yt**0.62)*1.14; return 0 if abs(S)<0.1 else (S+0.027)*100
spec=json.load(open(RV+'text_spec_r9.json'))['texts']
moved={'790:115':(913,1490,73,46),'790:119':(757,1494,43,28),'790:120':(11,1442,31,22),'790:124':(558,1609,67,41),'797:79':(344,552,90,16),'797:80':(130,372,51,33),'802:78':(362,924,51,34)}
s=300/72; o=8.5
def dil(m,n):
    for _ in range(n): m = m | np.roll(m,1,0) | np.roll(m,-1,0) | np.roll(m,1,1) | np.roll(m,-1,1)
    return m
res=[]
for t in spec:
    x,y,w,h = moved.get(t[0], t[1])
    x0=int((x+o)*s)-6; y0=int((y+o)*s)-6; x1=int((x+w+o)*s)+7; y1=int((y+h+o)*s)+7
    m=vm[y0:y1,x0:x1]
    if m.sum()==0: print('no ink', t[0]); continue
    core = m & ~dil(~m,1)  # eroded interior
    cm = vec[y0:y1,x0:x1][core if core.sum()>20 else m]
    # dominant cmyk
    vals,cnt=np.unique(cm.reshape(-1,4),axis=0,return_counts=True); cmyk=vals[cnt.argmax()]
    tc_B=np.array(ImageCms.applyTransform(Image.new('CMYK',(1,1),tuple(int(v) for v in cmyk)),tb).getpixel((0,0)),float)
    tc_N=np.array(ImageCms.applyTransform(Image.new('CMYK',(1,1),tuple(int(v) for v in cmyk)),tn).getpixel((0,0)),float)
    halo = dil(m,4) & ~m   # 1pt halo at 300dpi ~4px
    hb=bgB[y0:y1,x0:x1][halo]; hn=bgN[y0:y1,x0:x1][halo]
    yb=Y(hb); yn=Y(hn)
    ytB=float(Y(tc_B)); ytN=float(Y(tc_N))
    light = ytB>0.5
    # quick: darkest 2% (dark text) / lightest 2% (light text)
    qB = np.percentile(yb, 98 if light else 2); qN=np.percentile(yn, 98 if light else 2)
    medB = float(np.median(yb)); medN=float(np.median(yn))
    medrgb = np.median(hb,axis=0)
    size=max(sg[2] for sg in t[4]); bold=any('Bold' in sg[1] for sg in t[4])
    large = size>=18 or (size>=14 and bold)
    need=3.0 if large else 4.5
    r=dict(id=t[0], txt=''.join(sg[0] for sg in t[4]).replace('\n','/')[:16], hex=t[4][-1][5], size=size, cmyk=tuple(round(v/2.55) for v in cmyk),
           q2_B=wcag(ytB,qB), med_B=wcag(ytB,medB), q2_N=wcag(ytN,qN), med_N=wcag(ytN,medN), lc=apca(tc_B,medrgb), need=need, tB=tc_B)
    res.append(r)
res.sort(key=lambda r:r['q2_B']/r['need'])
for r in res[:30]:
    print('%-7s %-16s %s %4.1fpt need %.1f | q2%% BPC %.2f noBPC %.2f | median BPC %.2f noBPC %.2f | Lc %.1f | cmyk %s proof %s'%(r['id'],r['txt'],r['hex'],r['size'],r['need'],r['q2_B'],r['q2_N'],r['med_B'],r['med_N'],r['lc'],r['cmyk'],tuple(int(v) for v in r['tB'])))
json.dump([{k:(v if not isinstance(v,np.ndarray) else v.tolist()) for k,v in r.items()} for r in res], open('contrast.json','w'), default=float)
