import sys
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/r10/'
src=sys.argv[1]; out=sys.argv[2]; x0,y0,x1,y1=map(float,sys.argv[3:7]); sc=float(sys.argv[7]) if len(sys.argv)>7 else 1
im=Image.open(R+src).convert('RGB').crop((int(x0*2),int(y0*2),int(x1*2),int(y1*2)))
if sc!=1: im=im.resize((int(im.width*sc),int(im.height*sc)),Image.LANCZOS)
im.save(out)
