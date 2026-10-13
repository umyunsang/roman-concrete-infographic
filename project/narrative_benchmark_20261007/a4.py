import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
W='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/'
bg = np.asarray(Image.open(W+'v8_11_map_print_bleed_5033x7087.png').convert('L')).astype(np.float64)
def bands(a):
    a=a-a.mean(); win=np.hanning(a.shape[0])[:,None]*np.hanning(a.shape[1])[None,:]
    F=np.abs(np.fft.fftshift(np.fft.fft2(a*win)))**2
    h,w=a.shape; yy,xx=np.mgrid[-h//2:h//2,-w//2:w//2]
    r=np.sqrt((yy/(h/2))**2+(xx/(w/2))**2)
    mid=F[(r>0.25)&(r<=0.5)].sum(); hi=F[(r>0.5)&(r<=1.0)].sum()
    return hi/mid
crops=[(1500,1800),(3000,2000),(5000,1200),(2200,3600),(6000,3500),(800,800)]
for (y,x) in crops:
    a=bg[y:y+512,x:x+512]
    # synthetic: downsample by 2 then upsample bicubic
    im=Image.fromarray(a.astype(np.uint8))
    up=np.asarray(im.resize((256,256),Image.BICUBIC).resize((512,512),Image.BICUBIC)).astype(np.float64)
    up15=np.asarray(im.resize((341,341),Image.BICUBIC).resize((512,512),Image.BICUBIC)).astype(np.float64)
    print('crop y%d x%d  hi/mid native %.3f | if from 150ppi %.3f | from 200ppi %.3f'%(y,x,bands(a),bands(up),bands(up15)))
