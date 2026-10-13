import numpy as np, json
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
im=np.asarray(Image.open(R+'r10/map_only_2x.png').convert('L')).astype(float)
S=2
rows=[]
for t in json.load(open(R+'text_spec_r10.json'))['texts']:
    bx,by,bw,bh=t[1]
    sub=im[int(by*S):int((by+bh)*S),int(bx*S):int((bx+bw)*S)]
    gy,gx=np.gradient(sub)
    edge=(np.hypot(gx,gy)>12).mean()
    rows.append((sub.std(),edge,t[0],''.join(s[0] for s in t[4]).replace('\n','/')[:24],sub.mean()))
for r in sorted(rows,reverse=True)[:14]:
    print('std %5.1f edge %.3f mean %5.1f %s %s'%(r[0],r[1],r[4],r[2],r[3]))
