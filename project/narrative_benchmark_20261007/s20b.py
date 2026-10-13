import sys,json; sys.path.insert(0,'.')
from m import *
from scipy import ndimage as ndi
d=json.load(open('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/text_spec_r9.json'))
T=d['texts']
Lp=np.load(OUT+'L_poster.npy'); Lm=np.load(OUT+'L_map.npy')
P_=P(); M_=M()
diff=np.abs(P_-M_).sum(-1)
H,W=Lp.shape
for t in T:
    tid,(x,y,w,h),rot=t[0],t[1],t[2]
    if y<235 and 355<x<835: continue
    txt=''.join(s[0] for s in t[4]).replace('\n','/')
    pad=15 if rot!=0 else 6
    x0=max(0,int((x-pad)*2)); y0=max(0,int((y-pad)*2)); x1=min(W,int((x+w+pad)*2)); y1=min(H,int((y+h+pad)*2))
    sp=Lp[y0:y1,x0:x1]; sm=Lm[y0:y1,x0:x1]; sd=diff[y0:y1,x0:x1]
    glyph=(sd>60)&(sp<60)
    if glyph.sum()==0: continue
    Lb=lab(M_[y0:y1,x0:x1].reshape(-1,3)).reshape(sm.shape+(3,))
    hh=(np.degrees(np.arctan2(Lb[...,2],Lb[...,1]))+360)%360; C=np.hypot(Lb[...,1],Lb[...,2])
    water=(hh>170)&(hh<270)&(C>4)
    obj=(sm>=55)&(sm<84)&~water
    dist=ndi.distance_transform_edt(~glyph)
    dd=dist[obj]
    if dd.size==0: continue
    mind=dd.min()/2
    if mind<4:
        n=(dd<8).sum()
        # location of closest obj px
        oy,ox=np.nonzero(obj); k=np.argmin(dist[obj])
        print(tid, txt[:24], 'min %.2f pt'%mind, 'n<4pt',n, 'closest obj px at pt (%.1f,%.1f) L=%.1f'%((x0+ox[k])/2,(y0+oy[k])/2, sm[oy[k],ox[k]]))
