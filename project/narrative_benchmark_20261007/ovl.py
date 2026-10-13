import numpy as np
from PIL import Image
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
a=np.array(Image.open(B+'idpass/id_id_overlay.png')).astype(int)
c=((a[...,0]-2)//4) + 64*((a[...,1]-2)//4) + 4096*((a[...,2]-2)//4)
c[a[...,3]==0]=-1
print(np.unique(c)[:40], (c>=0).sum())
np.save('idover.npy',c)
