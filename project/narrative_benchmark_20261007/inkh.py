from PIL import Image
import numpy as np, json
im=np.asarray(Image.open('../nb_work/review_loop/r9/poster_2x.png').convert('RGB')).astype(float)
mo=np.asarray(Image.open('../nb_work/review_loop/r9/map_only_2x.png').convert('RGB')).astype(float)
def lum(a): return 0.2126*a[...,0]+0.7152*a[...,1]+0.0722*a[...,2]
L=lum(im); Lm=lum(mo)
spec={t[0]:t for t in json.load(open('../nb_work/review_loop/text_spec_r9.json'))['texts']}
for id in ['790:82','790:86','790:146','790:170','790:174','790:148','790:121','790:112','790:113','790:189','790:116']:
    x,y,w,h=spec[id][1]
    X0,Y0,X1,Y1=int(x*2),int(y*2)-2,int((x+w)*2),int((y+h)*2)+2
    d=np.abs(L[Y0:Y1,X0:X1]-Lm[Y0:Y1,X0:X1])>30
    # per-column ink extents -> median of syllable heights: use row profile coverage>2% of max
    prof=d.sum(1)
    rows=np.nonzero(prof>0.05*prof.max())[0]
    # first line only: take contiguous from first
    r0=rows[0]; r1=r0
    while r1+1<len(prof) and prof[r1+1]>0.05*prof.max(): r1+=1
    print(id, spec[id][4][-1][0][:12], spec[id][4][-1][2],'pt  ink band %.1f pt  ratio %.3f em'%((r1-r0+1)/2,(r1-r0+1)/2/spec[id][4][-1][2]))
