import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
S={t[0]:t for t in json.load(open(R+'text_spec_r10.json'))['texts']}
ink=np.load('ink.npy'); g=np.load('grad.npy').astype(np.float32)
M=np.asarray(Image.open(R+'r10/map_only_2x.png').convert('RGB')).astype(np.int16)
groups={'석회가마':['797:78'],'판테온':['797:79'],'실험실':['790:192','790:193'],'시편캡션':['798:78','798:79'],'프리베르눔':['790:109','790:112','790:113'],'유적관찰':['790:190'],'확대모형캡션':['790:189'],'방파제캡션':['790:128'],'제작원리':['790:177','790:178'],'구조원리':['790:180','790:181'],'메움원리':['790:183','790:184'],'해수원리':['790:174','790:175'],'물이스밈':['790:186'],'칼슘이동':['790:187'],'결정이메움':['790:188'],'아피아가도':['790:107']}
for name,ids in groups.items():
    xs=[];ys=[]
    for i in ids:
        x,y,w,h=S[i][1]; xs+=[x,x+w]; ys+=[y,y+h]
    x0,y0,x1,y1=min(xs),min(ys),max(xs),max(ys)
    m=110
    X0,Y0,X1,Y1=max(int((x0-m)*2),0),max(int((y0-m)*2),0),min(int((x1+m)*2),2382),min(int((y1+m)*2),3368)
    win=M[Y0:Y1,X0:X1]
    obj=(g[Y0:Y1,X0:X1]>12)
    src=np.zeros(obj.shape,bool)
    for i in ids:
        x,y,w,h=S[i][1]
        a,b,c,d=int((x-2)*2),int((y-2)*2),int((x+w+2)*2),int((y+h+2)*2)
        src[b-Y0:d-Y0,a-X0:c-X0]=ink[b:d,a:c]
    # other text ink as competitor
    oth=ink[Y0:Y1,X0:X1]&~ndi.binary_dilation(src,iterations=6)
    dt=ndi.distance_transform_edt(~src)
    lab,n=ndi.label(ndi.binary_dilation(obj,iterations=3))
    items=[]
    for i in range(1,n+1):
        mm=(lab==i)&obj
        if mm.sum()<25: continue
        yy,xx=np.nonzero(mm)
        items.append((dt[mm].min()/2,'obj',(xx.min()+X0)/2,(yy.min()+Y0)/2,(xx.max()+X0)/2,(yy.max()+Y0)/2))
    lab2,n2=ndi.label(ndi.binary_dilation(oth,iterations=8))
    for i in range(1,n2+1):
        mm=(lab2==i)&oth
        if mm.sum()<25: continue
        yy,xx=np.nonzero(mm)
        items.append((dt[mm].min()/2,'TEXT',(xx.min()+X0)/2,(yy.min()+Y0)/2,(xx.max()+X0)/2,(yy.max()+Y0)/2))
    items.sort()
    print(name, 'box',(x0,y0,x1,y1))
    for it in items[:6]: print('    d=%.1f %s (%.0f,%.0f)-(%.0f,%.0f)'%it)
