import json, numpy as np
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
inv=json.load(open(R+'inventory.json'))
objs=[o['name'] for o in inv['objects']]
assert objs==sorted(objs), 'not sorted'
oid={n:i+1 for i,n in enumerate(objs)}
def dec(p):
    a=np.array(Image.open(p).convert('RGBA')).astype(int)
    k=np.rint((a[...,:3]-2)/4).astype(int)
    code=k[...,0]+64*k[...,1]+4096*k[...,2]
    code[a[...,3]<128]=0
    return code
m=dec(R+'idpass/id_id_map.png'); o=dec(R+'idpass/id_id_overlay.png')
final=np.where(o>0,o,m)
np.save('m.npy',m); np.save('o.npy',o); np.save('final.npy',final)
json.dump(oid,open('oid.json','w'))
# asset of each object
a2o={}
for a in inv['assets']:
    a2o[a['id']]=a.get('objects',[])
json.dump(a2o,open('a2o.json','w'),ensure_ascii=False)
print(m.shape, len(objs))
# verify with bbox
px=m.shape[1]/1191
for n in ['T_cypress','T_pine.004','R_via_appia','L02_tiber']:
    i=oid[n]; ys,xs=np.where(final==i)
    print(n, xs.min()/px, (xs.max()+1)/px, ys.min()/px,(ys.max()+1)/px, len(xs)/px**2, [ob for ob in inv['objects'] if ob['name']==n][0]['bbox_visible_final_pt'])
