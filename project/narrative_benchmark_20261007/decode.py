import json, numpy as np
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
inv=json.load(open(R+'inventory.json'))
names=[o['name'] for o in inv['objects']]
print('sorted?', names==sorted(names), len(names))
def dec(p):
    a=np.asarray(Image.open(p).convert('RGBA')).astype(np.int64)
    k=np.rint((a[...,:3]-2)/4).astype(np.int64)
    code=k[...,0]+64*k[...,1]+4096*k[...,2]
    code[a[...,3]<128]=0
    return code
m=dec(R+'idpass/id_id_map.png'); o=dec(R+'idpass/id_id_overlay.png')
final=np.where(o>0,o,m)
print(m.shape, m.max(), o.max())
# object->asset
obj2asset={}
for a in inv['assets']:
    for nm in a.get('objects',[]): obj2asset[nm]=a['id']
assets=sorted(set(obj2asset.values()))
aidx={a:i+1 for i,a in enumerate(assets)}
lut=np.zeros(len(names)+1,dtype=np.int16)
for i,nm in enumerate(names): lut[i+1]=aidx.get(obj2asset.get(nm),0)
np.save('final_obj.npy',final.astype(np.int16)); np.save('map_obj.npy',m.astype(np.int16)); np.save('ovl_obj.npy',o.astype(np.int16))
np.save('final_asset.npy',lut[final]); np.save('map_asset.npy',lut[m])
json.dump({'names':names,'assets':assets,'obj2asset':obj2asset},open('ids.json','w'),ensure_ascii=False)
# check visible areas vs inventory
pxpt=m.shape[1]/1191
fa=lut[final]
for a in inv['assets']:
    if a['id'] in ['support_harbor','landmark_vesuvius','landmark_aqueduct']:
        print(a['id'], a['area_visible_final_pt2'], (fa==aidx[a['id']]).sum()/pxpt**2)
