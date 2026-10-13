import sys, json, numpy as np
sys.path.insert(0,'.')
from fake import *
from scipy.spatial import cKDTree
from PIL import Image
P=np.array(Image.open('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/r11/poster_2x.png').convert('RGB')).astype(float)
TS={t[0]:t for t in json.load(open('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/text_spec_r11.json'))['texts']}
ov=np.load('idover.npy')
yy=(np.arange(H)*code.shape[0]/H).astype(int); xx=(np.arange(W)*code.shape[1]/W).astype(int)
C3=code[yy][:,xx]; O3=ov[yy][:,xx]
def vis_pts(aid, objs=None):
    names=objs or A[aid]['objects']
    codes=[name2idx[n]+1 for n in names if n in name2idx]
    m=np.isin(C3,codes)&(O3<1)
    # overlay assets
    m|=np.isin(O3,codes)
    ys,xs=np.nonzero(m); return np.stack([(xs+0.5)/S,(ys+0.5)/S],1)
def ink(node,Lthr=65,pad=2):
    x,y,w,h=TS[node][1]
    X0,Y0,X1,Y1=int((x-pad)*2),int((y-pad)*2),int((x+w+pad)*2),int((y+h+pad)*2)
    L=srgb2lab(P[Y0:Y1,X0:X1])[...,0]; ys,xs=np.nonzero(L<Lthr)
    return np.stack([(X0+xs+0.5)/2,(Y0+ys+0.5)/2],1)
node=sys.argv[1]; own=sys.argv[2]; others=sys.argv[3].split(',')
objs_own=sys.argv[4].split(',') if len(sys.argv)>4 else None
p=ink(node)
d=cKDTree(vis_pts(own,objs_own)).query(p)[0]; print(node,'d_own(vis)',own,round(d.min(),2))
for o in others:
    q=vis_pts(o)
    if len(q)==0: print(o,'none'); continue
    print('  d_other(vis)',o,round(cKDTree(q).query(p)[0].min(),2))
