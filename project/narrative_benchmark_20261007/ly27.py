import json, numpy as np
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
T=json.load(open(R+'text_spec_r10.json'))['texts']
M=np.asarray(Image.open(R+'r10/map_only_2x.png').convert('RGB')).astype(np.int16)
sea=(M[...,2]>M[...,0]+15)
for t in T:
    x,y,w,h=t[1]
    sub=sea[int(y*2):int((y+h)*2),int(x*2):int((x+w)*2)]
    f=sub.mean()
    if 0.02<f<0.98: print('mixed land/sea box',t[0],t[4][0][0][:12],'sea frac %.2f'%f)
