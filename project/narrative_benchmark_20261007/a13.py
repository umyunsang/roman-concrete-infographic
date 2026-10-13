import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
RV='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
W='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/'
bg=Image.open(W+'v8_11_map_print_bleed_5033x7087.png').convert('L')
# resample bg to 4 px/pt grid aligned with design pt coords: px_bg = (pt+8.5)/0.2400159
s=0.2400159
mo=Image.open(RV+'r9/map_only_2x.png').convert('L')
mo4=np.asarray(mo.resize((2382*2,3368*2),Image.BICUBIC)).astype(np.float64)  # 4px/pt
# bg -> 4px/pt : scale factor 4*s
W4=int(1208*4); H4=int(1701*4)
bg4=np.asarray(bg.resize((W4,H4),Image.LANCZOS)).astype(np.float64)
off=int(8.5*4)
def xcorr(a,b):
    a=a-a.mean(); b=b-b.mean()
    F=np.fft.fft2(a)*np.conj(np.fft.fft2(b))
    c=np.fft.ifft2(F/ (np.abs(F)+1e-9)).real
    i=np.unravel_index(c.argmax(),c.shape)
    dy=i[0] if i[0]<a.shape[0]//2 else i[0]-a.shape[0]
    dx=i[1] if i[1]<a.shape[1]//2 else i[1]-a.shape[1]
    return dx/4,dy/4,c.max()
for (x,y) in [(100,100),(560,120),(1000,100),(100,800),(560,800),(1000,800),(100,1500),(560,1500),(1000,1500),(300,500),(800,1200)]:
    a=bg4[off+y*4:off+(y+128)*4, off+x*4:off+(x+128)*4]
    b=mo4[y*4:(y+128)*4, x*4:(x+128)*4]
    dx,dy,pk=xcorr(a,b)
    print('region pt (%4d,%4d): print-bg content shift vs design = dx %.2f pt, dy %.2f pt (peak %.2f)'%(x,y,-dx,-dy,pk))
