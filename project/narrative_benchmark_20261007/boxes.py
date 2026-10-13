import sys, json
from PIL import Image, ImageDraw
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
src=sys.argv[1]; x0,y0,x1,y1=map(float,sys.argv[2:6]); out=sys.argv[6]; Z=float(sys.argv[7])
im=Image.open(R+'r10/'+src).convert('RGB')
sc=im.size[0]/1191
c=im.crop((int(x0*sc),int(y0*sc),int(x1*sc),int(y1*sc))).resize((int((x1-x0)*Z),int((y1-y0)*Z)),Image.LANCZOS)
d=ImageDraw.Draw(c)
for t in json.load(open(R+'text_spec_r10.json'))['texts']:
    bx,by,bw,bh=t[1]
    if bx+bw<x0 or bx>x1 or by+bh<y0 or by>y1: continue
    d.rectangle([(bx-x0)*Z,(by-y0)*Z,(bx+bw-x0)*Z,(by+bh-y0)*Z],outline=(0,90,255),width=1)
# grid every 10pt
for gx in range(int(x0//10*10),int(x1)+1,10):
    if gx>=x0: d.line([((gx-x0)*Z,0),((gx-x0)*Z,6)],fill=(255,0,0))
for gy in range(int(y0//10*10),int(y1)+1,10):
    if gy>=y0: d.line([(0,(gy-y0)*Z),(6,(gy-y0)*Z)],fill=(255,0,0))
c.save(out); print(out,c.size)
