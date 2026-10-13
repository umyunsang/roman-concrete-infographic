import numpy as np, json
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/assets/landmark_aqueduct/'
a=np.array(Image.open(R+'isolated_rgba.png'))[...,3]>0
H,W=a.shape
gaps=[];ops=[]
for y in range(0,H,3):
    row=a[y]
    xs=np.nonzero(row)[0]
    if len(xs)<2: continue
    # runs
    d=np.diff(row.astype(int))
    starts=list(np.nonzero(d==1)[0]+1); ends=list(np.nonzero(d==-1)[0]+1)
    if row[0]: starts=[0]+starts
    if row[-1]: ends=ends+[W]
    runs=list(zip(starts,ends))
    for (s0,e0),(s1,e1) in zip(runs[:-1],runs[1:]):
        g=(s1-e0)/3
        if g<12: gaps.append(g)
    for s,e in runs: ops.append((e-s)/3)
gaps=np.array(gaps); ops=np.array(ops)
print('transparent gaps between opaque runs (pt): n',len(gaps),'median',np.median(gaps),'p25',np.percentile(gaps,25),'p75',np.percentile(gaps,75),'p90',np.percentile(gaps,90),'max',gaps.max())
print('share of gaps >=4pt',(gaps>=4).mean())
print('opaque run (pier) median pt',np.median(ops[ops<15]))
