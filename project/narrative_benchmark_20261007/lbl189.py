import numpy as np, json
from PIL import Image
from scipy import ndimage
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
P=np.array(Image.open(R+'r11/poster_2x.png').convert('RGB')).astype(int)
M=np.array(Image.open(R+'r11/map_only_2x.png').convert('RGB')).astype(int)
def ink(box):
    x0,y0,w,h=box
    X0,Y0,X1,Y1=int((x0-2)*2),int((y0-2)*2),int((x0+w+2)*2),int((y0+h+2)*2)
    d=np.abs(P[Y0:Y1,X0:X1]-M[Y0:Y1,X0:X1]).sum(-1)>60
    ys,xs=np.nonzero(d)
    return [xs.min()/2+x0-2, (xs.max()+1)/2+x0-2, ys.min()/2+y0-2, (ys.max()+1)/2+y0-2]
b=ink([438,1295,184,14]); print('790:189 ink', [round(v,1) for v in b])
# A07 mask from id map
S=1.9992
im=np.array(Image.open(R+'obj_r11/idpass/id_id_map.png'))
full=(im[...,0].astype(np.int64)<<16)|(im[...,1].astype(np.int64)<<8)|im[...,2]; fa=im[...,3]>0
inv=json.load(open(R+'obj_r11/inventory.json'))
def mask_of(name):
    o=[o for o in inv['objects'] if o['name']==name][0]
    bb=o['bbox_visible_own_pass_pt']
    # find code: most frequent code inside bbox matching bbox
    x0,x1,y0,y1=[int(v*S) for v in bb]
    sub=full[y0:y1,x0:x1][fa[y0:y1,x0:x1]]
    ks,cnt=np.unique(sub,return_counts=True)
    for k in ks[np.argsort(cnt)[::-1]]:
        m=(full==k)&fa; ys,xs=np.nonzero(m)
        b2=[xs.min()/S,(xs.max()+1)/S,ys.min()/S,(ys.max()+1)/S]
        if sum(abs(p-q) for p,q in zip(b2,bb))<1.5: return m
def boxdist(m, b):
    ys,xs=np.nonzero(m); px=(xs+.5)/S; py=(ys+.5)/S
    dx=np.maximum(0,np.maximum(b[0]-px,px-b[1])); dy=np.maximum(0,np.maximum(b[2]-py,py-b[3]))
    return float(np.hypot(dx,dy).min())
A07=None
for n in ['NB_lime_clast_specimen']+['NB_lime_clast_specimen_LIME0%d'%i for i in range(6)]:
    m=mask_of(n)
    if m is not None: A07=m if A07 is None else (A07|m)
print('d_own 790:189 -> A07', round(boxdist(A07,b),2))
# ground line end: overlay object at 382.2-418.2 x 1300-1301
gx1,gy=418.2,1300.5
dx=max(0,b[0]-gx1); dy=max(0,b[2]-gy, gy-b[3]); print('d to ground-line end', round((dx**2+dy**2)**.5,2))
# section segment nearest
dx=max(0,b[0]-407.2); print('d to section body (x 407.2)', round(dx,2))
# tower 
for n in ['D3_foundation','D3_heavy']:
    print('d to',n, round(boxdist(mask_of(n),b),2))
