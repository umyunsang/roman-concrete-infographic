import numpy as np
from PIL import Image, ImageCms
W='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/'
srgb=ImageCms.createProfile('sRGB'); pso=ImageCms.getOpenProfile(W+'PSOcoated_v3.icc')
fw=ImageCms.buildTransform(srgb,pso,'RGB','CMYK',renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC,flags=0)
fwb=ImageCms.buildTransform(srgb,pso,'RGB','CMYK',renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC,flags=ImageCms.Flags.BLACKPOINTCOMPENSATION)
for hx in ['#2E2A22','#3E3A31','#59524A','#983821','#1B5760','#8A5427','#FFF4DD','#E7DBC6']:
    rgb=tuple(int(hx[i:i+2],16) for i in (1,3,5))
    c=np.array(ImageCms.applyTransform(Image.new('RGB',(1,1),rgb),fw).getpixel((0,0)))/255*100
    cb=np.array(ImageCms.applyTransform(Image.new('RGB',(1,1),rgb),fwb).getpixel((0,0)))/255*100
    print(hx,'noBPC C%.1f M%.1f Y%.1f K%.1f TAC %.0f'%(*c,c.sum()),' | BPC C%.0f M%.0f Y%.0f K%.0f'%tuple(cb))
