import json, numpy as np
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
inv=json.load(open(R+'inventory.json'))
names=[o['name'] for o in inv['objects']]
print(names==sorted(names), len(names))
def dec(p):
    a=np.asarray(Image.open(p)).astype(np.float64)
    k=np.rint((a[...,:3]-2)/4).astype(np.int64)
    code=k[...,0]+64*k[...,1]+4096*k[...,2]
    code[a[...,3]<=127.5]=0
    return code
mc=dec(R+'idpass/id_id_map.png'); oc=dec(R+'idpass/id_id_overlay.png')
final=np.where(oc>0,oc,mc)
np.save('id2x.npy', final.astype(np.int32))
# check bbox
pxpt=final.shape[1]/1191
for i,n in enumerate(names):
    if n in ('T_cypress','R_via_appia','T_land','L10_sea'):
        ys,xs=np.nonzero(final==i+1)
        print(n, xs.min()/pxpt, (xs.max()+1)/pxpt, ys.min()/pxpt,(ys.max()+1)/pxpt, inv['objects'][i]['bbox_visible_final_pt'])
# upscale to 3x
H3,W3=5051,3572
s2=final.shape[1]/1191; s3=W3/1191
yy=np.minimum(((np.arange(H3)+0.5)/s3*s2).astype(int), final.shape[0]-1)
xx=np.minimum(((np.arange(W3)+0.5)/s3*s2).astype(int), final.shape[1]-1)
id3=final[yy][:,xx]
np.save('id3x.npy', id3.astype(np.int16))
json.dump(names, open('names.json','w'))
