import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/'
a=np.asarray(Image.open(B+'v8_12_map_print_bleed_5033x7087.png').convert('RGB')).astype(np.int16)
H,W=a.shape[:2]
# right: find n such that cols W-n..W-1 mirror cols W-n-1 ... W-2n
for n in (12,14,15,16,17,18,20):
    m=np.abs(a[:,W-n:]-a[:,W-n-1:W-2*n-1:-1]).mean()
    m2=np.abs(a[:,W-n:]-a[:,W-n-n:W-n][:, ::-1]).mean()
    print('right n',n,'mirror err (excl axis) %.2f  (incl) %.2f'%(m,m2))
for n in (10,12,14,16):
    m=np.abs(a[:n]-a[n+n-1:n-1:-1]).mean(); m2=np.abs(a[:n]-a[n:2*n][::-1]).mean()
    print('top n',n,'%.2f %.2f'%(m,m2))
f=300/72
for n in (12,16): print(n,'px from media edge = %.2f mm ; outside trim by %.2f mm'%(n*25.4/300, 3*1-0+ (8.5*25.4/72 - 3) - n*25.4/300 + 0))
print('trim at %.2f px from edge'%(8.5*f))
