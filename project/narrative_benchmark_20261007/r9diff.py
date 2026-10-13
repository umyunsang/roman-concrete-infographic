import numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
a=np.asarray(Image.open(R+'r9/map_only_2x.png').convert('RGB')).astype(float)
b=np.asarray(Image.open(R+'r10/map_only_2x.png').convert('RGB')).astype(float)
d=np.abs(a-b).sum(2)
m=d>30
m=ndi.binary_opening(m,iterations=1)
lab,n=ndi.label(ndi.binary_dilation(m,iterations=10))
print('changed regions',n)
for s in ndi.find_objects(lab):
    y0,y1=s[0].start/2,s[0].stop/2; x0,x1=s[1].start/2,s[1].stop/2
    if (x1-x0)*(y1-y0)>30: print(f'x{x0:.0f}-{x1:.0f} y{y0:.0f}-{y1:.0f}')
# specific: ⑤ region
for name,(x0,y0,x1,y1) in {'c5':(1060,898,1140,918),'c4':(765,1115,805,1131)}.items():
    print(name, d[y0*2:y1*2,x0*2:x1*2].mean())
im=Image.fromarray((np.clip(d,0,255)).astype(np.uint8)).resize((1191,1684)); im.save('r9r10diff.png')
