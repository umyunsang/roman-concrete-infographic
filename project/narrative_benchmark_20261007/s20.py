import sys,json; sys.path.insert(0,'.')
from m import *
from scipy import ndimage as ndi
d=json.load(open('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/text_spec_r9.json'))
T=d['texts']
Lp=np.load(OUT+'L_poster.npy'); Lm=np.load(OUT+'L_map.npy')
P_=P(); M_=M()
diff=np.abs(P_-M_).sum(-1)
H,W=Lp.shape
rows=[]
for t in T:
    tid,(x,y,w,h),rot=t[0],t[1],t[2]
    txt=''.join(s[0] for s in t[4]).replace('\n','/')
    pad=15 if rot!=0 else 6
    x0=max(0,int((x-pad)*2)); y0=max(0,int((y-pad)*2)); x1=min(W,int((x+w+pad)*2)); y1=min(H,int((y+h+pad)*2))
    sp=Lp[y0:y1,x0:x1]; sm=Lm[y0:y1,x0:x1]; sd=diff[y0:y1,x0:x1]
    glyph=(sd>60)&(sp<60)
    if glyph.sum()==0: rows.append((tid,txt,'no glyph')); continue
    obj=(sm>=55)&(sm<84)
    # distance from each obj px to nearest glyph px
    dist=ndi.distance_transform_edt(~glyph)
    dd=dist[obj]
    mind=dd.min()/2 if dd.size else 99
    n4=(dd<8).sum()
    # background under glyph in map
    under=np.median(sm[glyph])
    rows.append((tid,txt[:22],round(mind,2),int(n4),round(float(under),1)))
for r in sorted(rows,key=lambda r:(r[2] if isinstance(r[2],float) else 99)):
    print(r)
