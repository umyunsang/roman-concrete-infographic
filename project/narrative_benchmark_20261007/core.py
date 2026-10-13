import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
S={t[0]:t for t in json.load(open(R+'text_spec_r10.json'))['texts']}
ink=np.load('ink.npy')
M=np.asarray(Image.open(R+'r10/map_only_2x.png').convert('RGB')).astype(np.int16)
red=(M[...,0]-M[...,1]>40)&(M[...,0]>100)&(M[...,1]<110)
cores={1:('790:102','790:146','790:147','790:148'),2:('790:105','790:152','790:153','790:154'),3:('790:110','790:158','790:159','790:160'),4:('790:111','790:164','790:165','790:166'),5:('790:106','790:170','790:171','790:172')}
def inkbox(tid,ytrim=None):
    x,y,w,h=S[tid][1]
    x0,y0,x1,y1=int(x*2)-4,int(y*2),int((x+w)*2)+4,int((y+h)*2)
    sub=ink[y0:y1,x0:x1]; ys,xs=np.nonzero(sub)
    return (xs.min()+x0)/2,(ys.min()+y0)/2,(xs.max()+x0+1)/2,(ys.max()+y0+1)/2
def lines(tid):
    x,y,w,h=S[tid][1]
    x0,y0,x1,y1=int(x*2)-4,int(y*2)-2,int((x+w)*2)+4,int((y+h)*2)+4
    sub=ink[y0:y1,x0:x1]; rows=sub.sum(1)>0
    lab,n=ndi.label(rows)
    out=[]
    for i in range(1,n+1):
        r=np.nonzero(lab==i)[0]
        if len(r)<4: continue
        cols=np.nonzero(sub[r.min():r.max()+1].any(0))[0]
        out.append(((cols.min()+x0)/2,(r.min()+y0)/2,(cols.max()+x0+1)/2,(r.max()+y0+1)/2))
    return out
res={}
for k,(d,t1,t2,b) in cores.items():
    # title lines: title boxes are 24.5 tall; use line detection restricted to the box rows
    L1=lines(t1); L2=lines(t2); B=lines(b)
    # underline: red pixels in map_only between title2 box bottom and body top
    x,y,w,h=S[t2][1]
    ya,yb=int((y+h-6)*2),int((S[b][1][1]+2)*2)
    xa,xb=int((x-5)*2),int((x+w+10)*2)
    sub=red[ya:yb,xa:xb]; ys,xs=np.nonzero(sub)
    ul=((xs.min()+xa)/2,(ys.min()+ya)/2,(xs.max()+xa+1)/2,(ys.max()+ya+1)/2)
    print('CORE',k)
    print('  title1 lines',L1); print('  title2 lines',L2); print('  underline',ul); print('  body lines',B)
    t1b=max(l[3] for l in L1); t2top=min(l[1] for l in L2); t2b=max(l[3] for l in L2)
    g1=t2top-t1b; g2=ul[1]-t2b; g3=B[0][1]-ul[3]
    t2w=L2[0][2]-L2[0][0]; bw=max(l[2]-l[0] for l in B)
    print(f'  gaps: t1->t2 {g1:.1f}  t2->ul {g2:.1f}  ul->body {g3:.1f}  ul len {ul[2]-ul[0]:.1f} t2 ink w {t2w:.1f} body max w {bw:.1f}  ul left {ul[0]} t2 left {L2[0][0]}')
    print('  left x per line: t2',L2[0][0],'body',[l[0] for l in B])
    res[k]=dict(L1=L1,L2=L2,B=B,ul=ul,g=[g1,g2,g3])
json.dump(res,open('core_ink.json','w'))
