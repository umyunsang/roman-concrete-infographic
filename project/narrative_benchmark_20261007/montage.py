import sys, json
from PIL import Image, ImageDraw
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/r10/'
P=Image.open(R+'poster_2x.png').convert('RGB'); M=Image.open(R+'map_only_2x.png').convert('RGB')
out=sys.argv[1]; regs=json.loads(sys.argv[2]); scale=float(sys.argv[3]) if len(sys.argv)>3 else 1.0
tiles=[]
for x0,y0,x1,y1 in regs:
    b=(int(x0*2),int(y0*2),int(x1*2),int(y1*2))
    a=P.crop(b); m=M.crop(b); W,H=a.size
    t=Image.new('RGB',(W*2+6,H),(255,0,0)); t.paste(a,(0,0)); t.paste(m,(W+6,0))
    if scale!=1: t=t.resize((int(t.width*scale),int(t.height*scale)),Image.LANCZOS)
    tiles.append(t)
Wt=max(t.width for t in tiles); Ht=sum(t.height+6 for t in tiles)
o=Image.new('RGB',(Wt,Ht),(0,0,255)); y=0
for t in tiles: o.paste(t,(0,y)); y+=t.height+6
o.save(out)
