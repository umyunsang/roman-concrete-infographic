import sys, json, numpy as np
from PIL import Image
sys.path.insert(0,'.')
from masks import srgb2lab, srgb2oklch
from scipy import ndimage as ndi
import warnings; warnings.filterwarnings('ignore')
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
inv=json.load(open(B+'inventory.json')); objs=inv['objects']
name2idx={o['name']:i for i,o in enumerate(objs)}
IDX=json.load(open(B+'assets_index.json')); A={a['id']:a for a in IDX['assets']}
code=np.load('idcode.npy')
img=np.array(Image.open('full3x.png')).astype(float)
H,W=img.shape[:2]; S=W/1191.0
def assetmask(aid):
    codes=[name2idx[n]+1 for n in A[aid]['objects']]
    m2=np.isin(code,codes)&(np.load("idover.npy")<1)
    # upsample nearest to 3x
    yy=(np.arange(H)*code.shape[0]/H).astype(int); xx=(np.arange(W)*code.shape[1]/W).astype(int)
    return m2[yy][:,xx]
def othermask(aid):
    mine=[name2idx[n]+1 for n in A[aid]['objects']]
    m2=(code>=1)&~np.isin(code,mine)
    yy=(np.arange(H)*code.shape[0]/H).astype(int); xx=(np.arange(W)*code.shape[1]/W).astype(int)
    return m2[yy][:,xx]
def comps(mask, minpx=1):
    lbl,n=ndi.label(mask)
    out=[]
    for i,sl in enumerate(ndi.find_objects(lbl)):
        m=lbl[sl]==i+1
        npx=m.sum()
        if npx<minpx: continue
        ys,xs=np.nonzero(m)
        pts=np.stack([xs,ys],1).astype(float)/S
        c=pts-pts.mean(0)
        ev,_=np.linalg.eigh(np.cov(c.T)) if len(pts)>2 else (np.array([0,0]),None)
        L=4*np.sqrt(max(ev[1],0)); area=npx/S/S
        w=area/max(L,1e-6)
        cx=(sl[1].start+sl[1].stop)/2/S; cy=(sl[0].start+sl[0].stop)/2/S
        out.append(dict(cx=round(cx,1),cy=round(cy,1),area=round(area,2),len=round(L,2),wid=round(w,2),sl=sl,i=i+1))
    return out,lbl
if __name__=='__main__':
    aid=sys.argv[1]
    am=assetmask(aid)
    print(aid,'visible pt2',am.sum()/S/S)
    np.save(aid+'_vis3x.npy',am)
