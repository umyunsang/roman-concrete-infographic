import sys, numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
for f in sys.argv[1:]:
    a=np.asarray(Image.open(f).convert('L'),np.float32)
    if a.shape[1]>1000: a=a[:, 4994:5074]
    j=40
    d=np.abs(np.diff(a,axis=1)).mean(0)
    bright=((a[:,j]-np.maximum(a[:,j-2],a[:,j+2]))>12).mean()*100
    print(f.split('/')[-1], a.shape, 'steps 37..43', d[37:44].round(2), 'col means 38..42', a.mean(0)[38:43].round(1), 'hairline%%', round(bright,3))
