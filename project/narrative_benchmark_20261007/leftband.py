import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/'
a=np.asarray(Image.open(B+'v8_12_map_print_bleed_5033x7087.png').convert('RGB')).astype(np.float32)
L=a.mean(2)
H,W=L.shape
for (y0,y1) in [(500,1500),(1500,2500),(3000,4000),(4500,5500),(6000,6700),(6800,7087)]:
    print('left rows %d-%d:'%(y0,y1), ' '.join('%.0f'%L[y0:y1,c].mean() for c in range(0,24,2)), '| col 40: %.0f'%L[y0:y1,40].mean())
for (y0,y1) in [(500,1500),(3000,4000),(6000,6700)]:
    print('right rows %d-%d:'%(y0,y1), ' '.join('%.0f'%L[y0:y1,W-1-c].mean() for c in range(0,24,2)))
print('bottom rows by distance:', ' '.join('%.0f'%L[H-1-r].mean() for r in range(0,24,2)))
