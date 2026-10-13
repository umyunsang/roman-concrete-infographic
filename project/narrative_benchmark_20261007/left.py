from PIL import Image
import numpy as np, json
im=np.asarray(Image.open('../nb_work/review_loop/r9/poster_2x.png').convert('RGB')).astype(float)
mo=np.asarray(Image.open('../nb_work/review_loop/r9/map_only_2x.png').convert('RGB')).astype(float)
def lum(a): return 0.2126*a[...,0]+0.7152*a[...,1]+0.0722*a[...,2]
L=lum(im); Lm=lum(mo)
spec={t[0]:t for t in json.load(open('../nb_work/review_loop/text_spec_r9.json'))['texts']}
blocks=[['790:80','790:98'],['790:81','790:99'],['790:109','790:112','790:113'],['790:121','790:123','790:126'],['790:122','790:125','790:127'],['790:192','790:193'],['790:174','790:175'],['790:177','790:178'],['790:180','790:181'],['790:183','790:184']]
def lines(id):
    x,y,w,h=spec[id][1]
    X0,Y0,X1,Y1=int(x*2)-3,int(y*2)-1,int((x+w)*2)+3,int((y+h)*2)+1
    d=np.abs(L[Y0:Y1,X0:X1]-Lm[Y0:Y1,X0:X1])>40
    rows=d.any(1)
    out=[];i=0
    while i<len(rows):
        if rows[i]:
            j=i
            while j<len(rows) and rows[j]: j+=1
            if j-i>=6:
                seg=d[i:j]; xx=np.nonzero(seg.any(0))[0]
                out.append(((Y0+i)/2,(Y0+j)/2,(X0+xx.min())/2,(X0+xx.max()+1)/2))
            i=j
        else: i+=1
    return out
for bl in blocks:
    s=[]
    for id in bl:
        for ln in lines(id):
            s.append((id,ln))
    lefts=[ln[2] for _,ln in s]
    print(bl, 'lefts', lefts, 'spread', max(lefts)-min(lefts))
    for id,ln in s: print('   ',id, 'y %.1f-%.1f  x %.1f-%.1f  ink h %.1f'%ln[:2]+ln[2:]  if False else '    %s y %.1f-%.1f x %.1f-%.1f'%(id,*ln))
