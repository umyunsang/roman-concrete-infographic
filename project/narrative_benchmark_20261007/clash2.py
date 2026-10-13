import sys, json, numpy as np
sys.path.insert(0,'.')
exec(open('bind_vis.py').read().split("node=sys.argv[1]")[0])
p=ink('790:181')
q=vis_pts('trees_s')
tr=cKDTree(q); d,i=tr.query(p)
print('ink pts within 0.5pt of tree mask:',(d<0.5).sum(),'of',len(p))
close=p[d<1.0]; print('close ink pts (pt):', close[:20])
print('tree pts near:', q[i[d<1.0]][:10])
# which tree object?
names=A['trees_s']['objects']
for n in names:
    qq=vis_pts('trees_s',[n]); 
    if len(qq)==0: continue
    dd=cKDTree(qq).query(p)[0].min(); print(n, round(dd,2), 'bbox', qq.min(0).round(1), qq.max(0).round(1))
