import json, numpy as np
from PIL import Image
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/'
R=B+'nb_work/review_loop/obj_r11/'
inv=json.load(open(R+'inventory.json'))
a=np.asarray(Image.open(R+'idpass/id_id_map.png').convert('RGBA')).astype(int)
s=1.9992
objs=inv['objects']
for idx,o in enumerate(objs):
    if o['pass']!='map' or not o.get('bbox_visible_final_pt'): continue
    x0,x1,y0,y1=o['bbox_visible_final_pt']
    sub=a[int(y0*s):int(y1*s)+1,int(x0*s):int(x1*s)+1]
    sub=sub[sub[...,3]>127][:,:3]
    if len(sub)==0: continue
    c,n=np.unique(sub,axis=0,return_counts=True)
    top=c[np.argmax(n)]
    if o['name'] in ('L07_vesuvius','L08_pompeii','B_pons1','NB_marine_breakwater','C5_researchers','L05_aqua_claudia') or idx<8:
        print(idx,o['name'],top, n.max(), o['area_visible_final_pt2']*s*s)
