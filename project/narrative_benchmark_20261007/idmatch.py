import json, numpy as np
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
inv=json.load(open(R+'inventory.json'))
S=1.9992
def region_ids(png, box):
    im=np.array(Image.open(R+'idpass/'+png))
    x0,x1,y0,y1=[int(round(v*S)) for v in box]
    sub=im[y0:y1,x0:x1]
    cols={}
    a=sub[...,3]>0
    rgb=sub[...,:3][a]
    keys=(rgb[:,0].astype(np.int64)<<16)|(rgb[:,1].astype(np.int64)<<8)|rgb[:,2]
    ks,cnt=np.unique(keys,return_counts=True)
    full=(im[...,0].astype(np.int64)<<16)|(im[...,1].astype(np.int64)<<8)|im[...,2]
    fa=im[...,3]>0
    out=[]
    for k,c in zip(ks,cnt):
        m=(full==k)&fa
        ys,xs=np.nonzero(m)
        bb=[xs.min()/S,(xs.max()+1)/S,ys.min()/S,(ys.max()+1)/S]
        # match
        best=None
        for o in inv['objects']:
            b=o.get('bbox_visible_own_pass_pt') or o.get('bbox_visible_final_pt')
            if not b: continue
            e=sum(abs(p-q) for p,q in zip(b,bb))
            if best is None or e<best[0]: best=(e,o['name'],o['pass'])
        out.append((hex(k),c,[round(v,1) for v in bb],best))
    return out
if __name__=='__main__':
    import sys
    png=sys.argv[1]; box=[float(v) for v in sys.argv[2:6]]
    for r in region_ids(png,box): print(r)
