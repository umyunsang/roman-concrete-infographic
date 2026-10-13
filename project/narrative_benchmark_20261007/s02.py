import sys,json; sys.path.insert(0,'.')
from m import *
d=json.load(open('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/text_spec_r9.json'))
T=d['texts']
for src,img in [('poster',P()),('map',M())]:
    H,W,_=img.shape
    mask=np.ones((H,W),bool)
    for t in T:
        x,y,w,h=t[1]; pad=15 if t[2]!=0 else 4
        mask[max(0,int((y-pad)*2)):int((y+h+pad)*2), max(0,int((x-pad)*2)):int((x+w+pad)*2)]=False
    L=np.empty((H,W))
    for i in range(0,H,256):
        L[i:i+256]=Lstar(img[i:i+256])
    obj=(L<84)&mask
    dark=(L<20)&mask
    print(src,'obj px',obj.sum(),'dark px',dark.sum(),'ratio %.3f%%'%(100*dark.sum()/obj.sum()))
    if src=='map':
        np.save(OUT+'L_map.npy',L.astype(np.float32))
        ys,xs=np.nonzero(dark)
        # cluster dark px by 20pt grid
        from collections import Counter
        c=Counter(zip((xs//80)*40,(ys//80)*40))
        print(sorted(c.items(),key=lambda kv:-kv[1])[:15])
    else:
        np.save(OUT+'L_poster.npy',L.astype(np.float32))
