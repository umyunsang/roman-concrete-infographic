from PIL import Image
import numpy as np, json, sys
D='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11'
inv=json.load(open(D+'/inventory.json'))
im=np.array(Image.open(D+'/idpass/id_id_map.png'))
s=inv['id_pass']['id_px_per_pt']
key=im[...,0].astype(np.int64)*65536+im[...,1].astype(np.int64)*256+im[...,2]
u,inv_idx,cnt=np.unique(key.reshape(-1),return_inverse=True,return_counts=True)
lab=inv_idx.reshape(key.shape)
objs=[o for o in inv['objects'] if o['pass']=='map']
res={}
H,W=key.shape
ys,xs=np.mgrid[0:H,0:W]
for k in range(len(u)):
    m=lab==k
    yy=ys[m]; xx=xs[m]
    bb=[xx.min()/s,(xx.max()+1)/s,yy.min()/s,(yy.max()+1)/s]
    area=m.sum()/s/s
    best=None
    for o in objs:
        b=o['bbox_visible_final_pt']
        if b is None: continue
        d=sum(abs(b[i]-bb[i]) for i in range(4))+abs(o['area_visible_final_pt2']-area)/50
        if best is None or d<best[0]: best=(d,o['name'])
    res[int(u[k])]=(best[1],round(best[0],2),round(area,1))
json.dump(res,open('idmap.json','w'),ensure_ascii=False,indent=0)
bad=[(k,v) for k,v in res.items() if v[1]>8]
print(len(res), 'bad', bad[:40])
names=[v[0] for v in res.values()]
import collections
print([n for n,c in collections.Counter(names).items() if c>1])
