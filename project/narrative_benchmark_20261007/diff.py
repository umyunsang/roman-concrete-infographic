import numpy as np
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/r10/'
P=np.asarray(Image.open(R+'poster_2x.png').convert('RGB')).astype(np.int32)
M=np.asarray(Image.open(R+'map_only_2x.png').convert('RGB')).astype(np.int32)
print(P.shape,M.shape)
d=np.abs(P-M).sum(2)
print('frac>24', (d>24).mean(), 'max', d.max())
im=Image.fromarray((np.clip(d,0,255)).astype(np.uint8)).resize((1191,1684))
im.save('diff_1x.png')
np.save('d.npy', d.astype(np.int16))
