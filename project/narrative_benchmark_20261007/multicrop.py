import sys
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
src=sys.argv[1]
im=Image.open(src)
for spec in sys.argv[2:]:
    x0,y0,x1,y1,name=spec.split(',')
    c=im.crop((int(float(x0)*2),int(float(y0)*2),int(float(x1)*2),int(float(y1)*2)))
    c.save(name+'.png'); print(name, c.size)
