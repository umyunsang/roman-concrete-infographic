import sys; sys.path.insert(0,"/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/ov3")
from lib import *
P=2.0
m2=np.asarray(Image.open('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/r11/map_only_2x.png').convert('RGB'))
id2=np.load(W+'id2x.npy')
id2=np.pad(id2,((0,m2.shape[0]-id2.shape[0]),(0,m2.shape[1]-id2.shape[1])))
L2=np.load(W+'L2.npy').astype(np.float64)
def mask2(aid):
    A=ASSETS[aid]; m=np.isin(id2,[NID[o] for o in A['objects']])
    if A.get('object_regions') and aid.startswith('road_core'):
        x0,x1,y0,y1=A['bbox_visible_final_pt']; r=np.zeros_like(m); r[int(y0*P):int(np.ceil(y1*P))+1,int(x0*P):int(np.ceil(x1*P))+1]=True; m&=r
    return m
def crop2(m,pad=45):
    ys,xs=np.nonzero(m); p=int(pad*P)
    return (slice(max(ys.min()-p,0),min(ys.max()+p+1,m.shape[0])), slice(max(xs.min()-p,0),min(xs.max()+p+1,m.shape[1])))
def mhp(L,M,sig=3):
    s=sig*P; num=ndi.gaussian_filter(L*M,s); den=ndi.gaussian_filter(M.astype(float),s)
    return L-num/np.maximum(den,1e-6)
