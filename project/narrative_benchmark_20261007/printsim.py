import numpy as np
from PIL import Image, ImageCms
ICC='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/PSOcoated_v3.icc'
_t=None
def sim(rgb):
    global _t
    if _t is None:
        srgb=ImageCms.createProfile('sRGB'); cmyk=ImageCms.getOpenProfile(ICC)
        t1=ImageCms.buildTransform(srgb,cmyk,'RGB','CMYK',renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC,flags=ImageCms.Flags.BLACKPOINTCOMPENSATION)
        t2=ImageCms.buildTransform(cmyk,srgb,'CMYK','RGB',renderingIntent=ImageCms.Intent.ABSOLUTE_COLORIMETRIC)
        _t=(t1,t2)
    im=Image.fromarray(rgb.astype(np.uint8),'RGB')
    c=ImageCms.applyTransform(im,_t[0]); r=ImageCms.applyTransform(c,_t[1])
    return np.array(r)
