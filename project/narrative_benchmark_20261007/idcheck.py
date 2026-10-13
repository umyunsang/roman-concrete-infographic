import json, numpy as np
from PIL import Image
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/'
R=B+'nb_work/review_loop/obj_r11/'
inv=json.load(open(R+'inventory.json'))
a=np.asarray(Image.open(R+'idpass/id_id_map.png').convert('RGBA')).astype(int)
cols,counts=np.unique(a[a[...,3]>127][:,:3],axis=0,return_counts=True)
print(len(cols)); print(cols[:10], counts[:10])
# check residual from 16+32k
print(np.abs(((cols-16)%32)).max())
