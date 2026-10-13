import sys
from PIL import Image
# crop.py src x0 x1 y0 y1 (pt) scale out  ; src px/pt inferred from width/1191
src,x0,x1,y0,y1,sc,out=sys.argv[1],*map(float,sys.argv[2:7]),sys.argv[7]
im=Image.open(src); s=im.width/1191
c=im.crop((int(x0*s),int(y0*s),int(x1*s),int(y1*s)))
c=c.resize((int((x1-x0)*sc),int((y1-y0)*sc)),Image.LANCZOS)
c.save(out)
