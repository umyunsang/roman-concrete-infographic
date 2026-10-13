import numpy as np
from PIL import Image, ImageCms
Image.MAX_IMAGE_PIXELS=None
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/'
S=np.load('S_inv.npy').astype(np.int16); s12=np.load('src_cmyk.npy').astype(np.int16)
pso=ImageCms.getOpenProfile(B+'PSOcoated_v3.icc'); srgb=ImageCms.createProfile('sRGB')
tr=ImageCms.buildTransform(srgb,pso,'RGB','CMYK',renderingIntent=1)
s11=np.asarray(ImageCms.applyTransform(Image.open(B+'v8_11_map_print_bleed_5033x7087.png').convert('RGB'),tr)).astype(np.int16)
m=np.abs(s11-s12).sum(2)>30
print('px where v8_11 != v8_12:', m.sum())
print('print image err vs v8_12: %.1f ; vs v8_11: %.1f (sum of 4ch, 0-255)'%(np.abs(S-s12).sum(2)[m].mean(), np.abs(S-s11).sum(2)[m].mean()))
