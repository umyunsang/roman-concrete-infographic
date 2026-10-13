import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx=json.load(open(R+'assets_index.json'))
oid=json.load(open('oid.json'))
final=np.load('final.npy'); PX=final.shape[1]/1191
land=oid['T_land']
blobs=[]
for a in idx['assets']:
    aid=a['id']
    if aid in ('ground_land',) or aid.startswith('shape_') or aid in ('header_gate','basic_recipe','basic_sources'): continue
    x0,x1,y0,y1=a['crop_pt']
    al=np.array(Image.open(a['files']['isolated_rgba']))[...,3]>=128
    h,w=al.shape
    vv,uu=np.mgrid[0:h,0:w]
    f=final[np.clip(((y0+(vv+0.5)/3)*PX).astype(int),0,final.shape[0]-1), np.clip(((x0+(uu+0.5)/3)*PX).astype(int),0,final.shape[1]-1)]
    core=ndi.binary_erosion(al,iterations=3)
    L=(f==land)&core
    lab,n=ndi.label(L)
    if not n: continue
    sizes=ndi.sum(L,lab,range(1,n+1))/9
    for k in np.where(sizes>=2)[0]:
        yy,xx=np.nonzero(lab==k+1)
        # widths
        blobs.append(dict(asset=aid,x=round(x0+xx.mean()/3,1),y=round(y0+yy.mean()/3,1),area=round(float(sizes[k]),1),w=round((xx.max()-xx.min()+1)/3,1),h=round((yy.max()-yy.min()+1)/3,1)))
blobs.sort(key=lambda b:-b['area'])
json.dump(blobs,open('blobs_all.json','w'))
from collections import Counter
print(len(blobs), Counter(b['asset'] for b in blobs))
for b in blobs[:40]: print(b)
