import json, sys, numpy as np
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx={a['id']:a for a in json.load(open(R+'assets_index.json'))['assets']}
oid=json.load(open('oid.json'))
final=np.load('final.npy'); PX=final.shape[1]/1191
aid=sys.argv[1]; cx,cy,half,sc=map(float,sys.argv[2:6]); out=sys.argv[6]
a=idx[aid]; x0,x1,y0,y1=a['crop_pt']
ctx=np.array(Image.open(a['files']['context']).convert('RGB')).astype(float)
al=np.array(Image.open(a['files']['isolated_rgba']))[...,3]>=128
h,w=al.shape
vv,uu=np.mgrid[0:h,0:w]
X=x0+(uu+0.5)/3; Y=y0+(vv+0.5)/3
f=final[np.clip((Y*PX).astype(int),0,final.shape[0]-1), np.clip((X*PX).astype(int),0,final.shape[1]-1)]
land=(f==oid['T_land'])&al
img=ctx.copy()
img[land]=img[land]*0.3+np.array([255,0,0])*0.7
# outline of al
from scipy import ndimage as ndi
edge=al&~ndi.binary_erosion(al)
img[edge]=[0,0,255]
u0=int((cx-half-x0)*3); u1=int((cx+half-x0)*3); v0=int((cy-half-y0)*3); v1=int((cy+half-y0)*3)
u0=max(0,u0);v0=max(0,v0);u1=min(w,u1);v1=min(h,v1)
c=Image.fromarray(img[v0:v1,u0:u1].astype(np.uint8))
c=c.resize((int(c.width*sc/3),int(c.height*sc/3)),Image.NEAREST)
c.save(out); print(c.size, 'origin pt', x0+u0/3, y0+v0/3)
