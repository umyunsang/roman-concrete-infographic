from PIL import Image
import numpy as np, json
im=np.asarray(Image.open('../nb_work/review_loop/r9/poster_2x.png').convert('RGB')).astype(float)
mo=np.asarray(Image.open('../nb_work/review_loop/r9/map_only_2x.png').convert('RGB')).astype(float)
def lum(a): return 0.2126*a[...,0]+0.7152*a[...,1]+0.0722*a[...,2]
L=lum(im); Lm=lum(mo)
spec=json.load(open('../nb_work/review_loop/text_spec_r9.json'))['texts']
for t in spec:
    id,box,rot,al,segs=t
    if rot!=0 or segs[0][5]=='#FFF4DD' or segs[0][0] in '+→': continue
    x,y,w,h=box
    X0,Y0,X1,Y1=int(x*2)-3,int(y*2)-1,int((x+w)*2)+3,int((y+h)*2)+1
    d=np.abs(L[Y0:Y1,X0:X1]-Lm[Y0:Y1,X0:X1])>30
    rows=d.any(1); i=0; out=[]
    while i<len(rows):
        if rows[i]:
            j=i
            while j<len(rows) and rows[j]: j+=1
            if j-i>=5: out.append(((Y0+i)/2,(Y0+j)/2))
            i=j
        else: i+=1
    text=''.join(s[0] for s in segs)
    exp=text.count('\n')+1
    tops=[o[0] for o in out]
    pitch=[round(b-a,1) for a,b in zip(tops,tops[1:])]
    bots=[o[1] for o in out]
    pb=[round(b-a,1) for a,b in zip(bots,bots[1:])]
    flag='' if len(out)==exp else '  <-- MISMATCH'
    if exp>1 or flag: print(id,repr(text[:24]),'expected',exp,'found',len(out),'top pitch',pitch,'bottom pitch',pb,flag)
