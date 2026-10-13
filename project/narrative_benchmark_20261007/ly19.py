import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
S={t[0]:t for t in json.load(open(R+'text_spec_r10.json'))['texts']}
ink=np.load('ink.npy')
def lines(tid):
    x,y,w,h=S[tid][1]
    x0,y0,x1,y1=int(x*2)-4,int(y*2)-1,int((x+w)*2)+4,int((y+h)*2)+2
    sub=ink[y0:y1,x0:x1]; rows=sub.sum(1)>0
    lab,n=ndi.label(rows); out=[]
    for i in range(1,n+1):
        r=np.nonzero(lab==i)[0]
        if len(r)<5: continue
        cols=np.nonzero(sub[r.min():r.max()+1].any(0))[0]
        out.append(((cols.min()+x0)/2,(r.min()+y0)/2,(r.max()+y0+1)/2))
    return out
blocks={'BASIC L':['790:80','790:98'],'BASIC R':['790:81','790:99'],'제작':['790:177','790:178'],'구조':['790:180','790:181'],'메움':['790:183','790:184'],'해수':['790:174','790:175'],'프리베르눔':['790:109','790:112','790:113'],'실험실':['790:192','790:193'],'항구':['790:121','790:123','790:126'],'폼페이':['790:122','790:125','790:127']}
for b,ids in blocks.items():
    ls=[];
    for i in ids: ls+=[(i,)+l for l in lines(i)]
    lefts=[l[1] for l in ls]
    print(b, ' '.join('%s:%.1f'%(l[0][-3:],l[1]) for l in ls), ' range %.1f'%(max(lefts)-min(lefts)))
