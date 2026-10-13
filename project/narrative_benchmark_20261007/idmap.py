import json, numpy as np
from PIL import Image
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
inv=json.load(open(B+'inventory.json'))
objs=inv['objects']
a=np.array(Image.open(B+'idpass/id_id_map.png')).astype(int)
code=((a[...,0]-2)//4) + 64*((a[...,1]-2)//4) + 4096*((a[...,2]-2)//4)
code[a[...,3]==0]=-1
np.save('idcode.npy',code)
k=1.9992
u=np.unique(code)
print(len(u), u[:10], u[-5:])
# compare bbox for several codes with object bboxes
res=[]
for c in u[u>=0][:200]:
    ys,xs=np.nonzero(code==c)
    bb=[xs.min()/k,(xs.max()+1)/k,ys.min()/k,(ys.max()+1)/k]
    # find best matching object
    best=None
    for i,o in enumerate(objs):
        ob=o.get('bbox_visible_final_pt')
        if not ob: continue
        err=max(abs(ob[j]-bb[j]) for j in range(4))
        if best is None or err<best[0]: best=(err,i,o['name'])
    res.append((c,best))
for r in res[:15]: print(r)
offs=[r[1][1]-r[0] for r in res if r[1][0]<3]
print('offset stats', np.unique(offs, return_counts=True))
