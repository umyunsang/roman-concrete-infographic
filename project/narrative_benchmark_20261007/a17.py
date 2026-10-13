import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
W='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/'
bg=np.asarray(Image.open(W+'v8_11_map_print_bleed_5033x7087.png').convert('RGB')).astype(np.float64)
L=bg.mean(axis=2)
print('profile from edge inward (mean luminance per row/col, px 0..50; trim at 35.4):')
for name,arr in (('top',L.mean(axis=1)[:60]),('bottom',L.mean(axis=1)[::-1][:60]),('left',L.mean(axis=0)[:60]),('right',L.mean(axis=0)[::-1][:60])):
    print(name, ' '.join('%.0f'%v for v in arr[:50]))
# local discontinuity: max abs row-to-row diff in first 60 rows vs interior typical
for name,arr2 in (('top',L[:80,:]),('bottom',L[::-1][:80,:]),('left',L[:,:80].T),('right',L[:,::-1][:,:80].T)):
    d=np.abs(np.diff(arr2,axis=0)).mean(axis=1)
    print(name,'row-diff', ' '.join('%.1f'%v for v in d[:50]))
