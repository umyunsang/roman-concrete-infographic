import numpy as np
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
S=1.9992
im=np.array(Image.open(R+'idpass/id_id_map.png'))
full=(im[...,0].astype(np.int64)<<16)|(im[...,1].astype(np.int64)<<8)|im[...,2]
fa=im[...,3]>0
def inside_and_dist(code, x, y):
    m=(full==code)&fa
    r,c=int(y*S),int(x*S)
    ins=bool(m[r,c])
    ys,xs=np.nonzero(m); d=np.hypot((xs+.5)/S-x,(ys+.5)/S-y)
    # distance to outside (depth)
    return ins, round(float(d.min()),2)
print('harbor dot center in mole?', inside_and_dist(0xf20602,197.85,1497.1))
# depth inside: distance from dot center to nearest non-mole pixel
m=(full==0xf20602)&fa
ys,xs=np.nonzero(~m[int(1480*S):int(1515*S),int(185*S):int(215*S)])
d=np.hypot((xs+.5)/S+185-197.85,(ys+.5)/S+1480-1497.1); print('harbor dot center depth to mole edge', round(float(d.min()),2))
# pompeii white pile: use full map pass color
mp=np.array(Image.open(R+'full/full_map_pass.png')).astype(float)[...,:3]/255
S3=2.9992
x0,x1,y0,y1=700,740,1475,1505
sub=mp[int(y0*S3):int(y1*S3),int(x0*S3):int(x1*S3)]
def srgb2lin(c): return np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4)
lin=srgb2lin(sub)
M=np.array([[0.4124,0.3576,0.1805],[0.2126,0.7152,0.0722],[0.0193,0.1192,0.9505]])
XYZ=lin@M.T; Xn,Yn,Zn=0.95047,1,1.08883
f=lambda t: np.where(t>0.008856,np.cbrt(t),7.787*t+16/116)
fx,fy,fz=f(XYZ[...,0]/Xn),f(XYZ[...,1]/Yn),f(XYZ[...,2]/Zn)
L=116*fy-16; a=500*(fx-fy); b=200*(fy-fz)
white=(L>=88)&(np.hypot(a,b)<12)
from scipy import ndimage
lab,n=ndimage.label(white)
sizes=ndimage.sum(white,lab,range(1,n+1))
print('white comps', n, sorted([(int(s), ) for s in sizes],reverse=True)[:5])
big=np.argmax(sizes)+1
wm=lab==big
ys,xs=np.nonzero(wm)
px=(xs+.5)/S3+x0; py=(ys+.5)/S3+y0
print('pile bbox pt', round(px.min(),1),round(px.max(),1),round(py.min(),1),round(py.max(),1),'area pt2',round(wm.sum()/S3**2,1))
cx,cy=724.05,1494.35
d=np.hypot(px-cx,py-cy); print('pompeii dot center -> pile dist', round(float(d.min()),2), 'dot radius ~1.75 -> edge gap', round(float(d.min())-1.75,2))
print('pile mean L', round(float(L[wm].mean()),1))
