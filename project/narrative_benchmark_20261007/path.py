import json,numpy as np
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
inv=json.load(open(R+'inventory.json'))
S=1.9992
im=np.array(Image.open(R+'idpass/id_id_map.png'))
full=(im[...,0].astype(np.int64)<<16)|(im[...,1].astype(np.int64)<<8)|im[...,2]
fa=im[...,3]>0
def name_of(code):
    m=(full==code)&fa; ys,xs=np.nonzero(m)
    bb=[xs.min()/S,(xs.max()+1)/S,ys.min()/S,(ys.max()+1)/S]
    best=None
    for o in inv['objects']:
        b=o.get('bbox_visible_own_pass_pt')
        if not b or o['pass']!='map': continue
        e=sum(abs(p-q) for p,q in zip(b,bb))
        if best is None or e<best[0]: best=(e,o['name'])
    return best[1]
def path(p0,p1,step=0.25):
    L=np.hypot(p1[0]-p0[0],p1[1]-p0[1]); seq=[]
    for t in np.arange(0,L,step):
        x=p0[0]+(p1[0]-p0[0])*t/L; y=p0[1]+(p1[1]-p0[1])*t/L
        r,c=int(y*S),int(x*S)
        k=int(full[r,c]) if fa[r,c] else -1
        if not seq or seq[-1][0]!=k: seq.append([k,round(t,1)])
    names={}
    for k,_ in seq:
        if k not in names: names[k]=name_of(k) if k>=0 else 'none'
    return [(names[k],t) for k,t in seq]
print('harbor', path((197.85,1497.1),(222.1,1518.1)))
print('pompeii', path((724.05,1494.35),(723.8,1545.1)))
print('d2', path((128.1,1007.15),(140.1,1007.15)))
print('ground', path((382.2,1300.5),(418.2,1300.5)))
