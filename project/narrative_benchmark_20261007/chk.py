import sys, numpy as np
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/r9/'
P=np.asarray(Image.open(R+'poster_2x.png').convert('RGB')).astype(int)
M=np.asarray(Image.open(R+'map_only_2x.png').convert('RGB')).astype(int)
print(P.shape,M.shape)
d=np.abs(P-M).sum(2)
print('mean diff',d.mean(),'frac>24',(d>24).mean())
# rows of large diff
ys,xs=np.where(d>24)
print(len(ys))
# compare image mode
im=Image.open(R+'poster_2x.png'); print(im.mode, im.info.get('dpi'))
im=Image.open(R+'map_only_2x.png'); print(im.mode, im.info.get('dpi'))
