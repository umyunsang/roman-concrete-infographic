import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
im=Image.open(R+'full/full_map_pass.png'); print(im.size, im.mode)
W,H=im.size; s=W/1191.0; print('px/pt',s, H/1684.0)
def patch(x,y,r=8):
    x0=int((x-r)*s); y0=int((y-r)*s); x1=int((x+r)*s); y1=int((y+r)*s)
    a=np.asarray(im.crop((x0,y0,x1,y1)).convert('RGBA')).astype(float)
    return a,x0,y0
def bil(a,u,v):
    u0=int(np.floor(u)); v0=int(np.floor(v)); fu=u-u0; fv=v-v0
    return (a[v0,u0]*(1-fu)*(1-fv)+a[v0,u0+1]*fu*(1-fv)+a[v0+1,u0]*(1-fu)*fv+a[v0+1,u0+1]*fu*fv)
def edge_dist(x,y,metric,thr,r=8,nang=720):
    a,x0,y0=patch(x,y,r)
    f=metric(a)
    cu=x*s-x0; cv=y*s-y0
    print('  metric at center', round(float(bil(f,cu-0.5,cv-0.5)),1))
    best=(99,None)
    for ang in np.linspace(0,2*np.pi,nang,endpoint=False):
        prev=None
        for t in np.arange(0,(r-1)*s,0.05):
            u=cu+np.cos(ang)*t-0.5; v=cv+np.sin(ang)*t-0.5
            val=bil(f,u,v)
            if val>thr:
                if t/s<best[0]: best=(t/s,np.degrees(ang))
                break
    return best
# harbor: sea has B-R >> 0, mole beige B-R << 0
br=lambda a: a[...,2]-a[...,0]
print('harbor sample colors around:')
a,x0,y0=patch(198.0,1497.0,6)
for dy in (-3,-2,-1,0,1,2,3):
    print(dy,[tuple(int(c) for c in a[int((1497+dy)*s)-y0, int((198+dx)*s)-x0][:3]) for dx in (-3,-2,-1,0,1,2,3)])
print('harbor edge (B-R > 0 is sea):', edge_dist(198.0,1497.0,br,0.0))
