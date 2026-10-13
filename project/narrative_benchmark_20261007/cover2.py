import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx=json.load(open(R+'assets_index.json'))
oid=json.load(open('oid.json')); a2o=json.load(open('a2o.json'))
final=np.load('final.npy'); PX=final.shape[1]/1191
land=oid['T_land']
mine='road_core_se road_core_se_2 road_appia road_ostiensis water_sea water_tiber tree_t_cypress tree_t_pine_004 tree_t_pine_022 trees_s trees_se'.split()
for a in idx['assets']:
    aid=a['id']
    if aid not in mine: continue
    x0,x1,y0,y1=a['crop_pt']
    al=np.array(Image.open(a['files']['isolated_rgba']))[...,3]>=128
    h,w=al.shape
    vv,uu=np.mgrid[0:h,0:w]
    f=final[np.clip(((y0+(vv+0.5)/3)*PX).astype(int),0,final.shape[0]-1), np.clip(((x0+(uu+0.5)/3)*PX).astype(int),0,final.shape[1]-1)]
    for er in (3,6):
        core=ndi.binary_erosion(al,iterations=er)
        L=(f==land)&core
        lab,n=ndi.label(L)
        sizes=ndi.sum(L,lab,range(1,n+1))/9 if n else np.array([0.])
        big=[]
        for k in np.argsort(-sizes)[:5]:
            if sizes[k]<1: break
            yy,xx=np.nonzero(lab==k+1); big.append((round(x0+xx.mean()/3,1),round(y0+yy.mean()/3,1),round(float(sizes[k]),1), round((xx.max()-xx.min()+1)/3,1), round((yy.max()-yy.min()+1)/3,1)))
        print(aid,'erode%dpx'%er,'core_pt2=%.0f'%(core.sum()/9),'land=%.1f pt2 (%.3f%%)'%(L.sum()/9,100*L.sum()/max(1,core.sum())),'blobs>=1:',big)
