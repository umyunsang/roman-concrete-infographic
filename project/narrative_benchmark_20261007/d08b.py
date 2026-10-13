import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx={a['id']:a for a in json.load(open(R+'assets_index.json'))['assets']}
oid=json.load(open('oid.json')); a2o=json.load(open('a2o.json'))
inv={v:k for k,v in oid.items()}
final=np.load('final.npy')
a=idx['support_harbor']; x0,x1,y0,y1=a['crop_pt']
al=np.array(Image.open(a['files']['isolated_rgba']))[...,3]>=128
h,w=al.shape; vv,uu=np.mgrid[0:h,0:w]
f=final[np.clip(((y0+(vv+0.5)/3)*2).astype(int),0,final.shape[0]-1),np.clip(((x0+(uu+0.5)/3)*2).astype(int),0,final.shape[1]-1)]
m=al&np.isin(f,[oid[o] for o in a2o['road_ostiensis']])
lab,n=ndi.label(m)
for s in ndi.find_objects(lab):
    print('harbor covered by road at x %.1f-%.1f y %.1f-%.1f'%(x0+s[1].start/3,x0+s[1].stop/3,y0+s[0].start/3,y0+s[0].stop/3))
# which harbor objects near
for o in a2o['support_harbor']:
    print(o, [ob for ob in json.load(open(R+'inventory.json'))['objects'] if ob['name']==o][0]['bbox_visible_final_pt'])
