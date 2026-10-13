import json, numpy as np
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
t=json.load(open(R+'text_spec_r11.json'))['texts']
P=np.asarray(Image.open(R+'r11/poster_2x.png').convert('RGB')).astype(float)[:3367,:2381]
d=np.load('diff.npy')[:3367,:2381]
L=0.299*P[...,0]+0.587*P[...,1]+0.114*P[...,2]
red=(P[...,0]-P[...,1]>40)&(P[...,0]>100)&(L<170)
cand=((L<140)|red)&(d>40)
S=2381/1191
lab=np.zeros(L.shape,np.int16); meta=[]
for i,tx in enumerate(t):
    nid,(x,y,w,h),rot=tx[0],tx[1],tx[2]
    txt=''.join(r[0] for r in tx[4])
    m=2
    xa,xb=int((x-m)*S),int((x+w+m)*S); ya,yb=int((y-m)*S),int((y+h+m)*S)
    xa,ya=max(xa,0),max(ya,0)
    sub=cand[ya:yb,xa:xb]
    lab[ya:yb,xa:xb][sub & (lab[ya:yb,xa:xb]==0)]=i+1
    meta.append({'i':i+1,'id':nid,'box':[x,y,w,h],'rot':rot,'txt':txt.replace('\n','/'),'npx':int(sub.sum())})
np.save('textlab.npy',lab); json.dump(meta,open('textmeta.json','w'),ensure_ascii=False)
print(len(meta))
