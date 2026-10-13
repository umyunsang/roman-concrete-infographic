import numpy as np
from PIL import Image, ImageFilter
Image.MAX_IMAGE_PIXELS=None
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/'
F=Image.open(B+'print_frame_4x.png'); print(F.size, F.mode, F.info.get('dpi'))
F2=F.convert('RGB').resize((2416,3402),Image.LANCZOS)
P=Image.open('print_proof144aa.png')
R=Image.open('rgbpdf144aa.png').convert('RGB')
a=np.asarray(F2.filter(ImageFilter.GaussianBlur(3))).astype(float); b=np.asarray(P.filter(ImageFilter.GaussianBlur(3))).astype(float); c=np.asarray(R.filter(ImageFilter.GaussianBlur(3))).astype(float)
print('4x png vs print proof blurred diff mean %.2f max %.1f'%(np.abs(a-b).sum(2).mean(), np.abs(a-b).sum(2).max()))
print('4x png vs RGB pdf blurred diff mean %.2f max %.1f'%(np.abs(a-c).sum(2).mean(), np.abs(a-c).sum(2).max()))
