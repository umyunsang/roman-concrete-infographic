import numpy as np
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS=None
RV='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
W='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/'
bg=Image.open(W+'v8_11_map_print_bleed_5033x7087.png').convert('RGB')
mo=Image.open(RV+'r9/map_only_2x.png').convert('RGB')
regs=[(140,480,240,560),(820,360,900,420),(330,1000,400,1070),(280,1080,340,1190)]
tiles=[]
for (x0,y0,x1,y1) in regs:
    a=mo.crop((x0*2,y0*2,x1*2,y1*2)).resize(((x1-x0)*4,(y1-y0)*4),Image.LANCZOS)
    # bg pt->px: px = (pt+8.5)/0.2400159
    s=1/0.2400159
    b=bg.crop((int((x0+8.5)*s),int((y0+8.5)*s),int((x1+8.5)*s),int((y1+8.5)*s))).resize(((x1-x0)*4,(y1-y0)*4),Image.LANCZOS)
    w,h=a.size; t=Image.new('RGB',(2*w+10,h),'white'); t.paste(a,(0,0)); t.paste(b,(w+10,0)); tiles.append(t)
H=sum(t.size[1] for t in tiles)+10*len(tiles); Wm=max(t.size[0] for t in tiles)
o=Image.new('RGB',(Wm,H),'white'); y=0
for t in tiles: o.paste(t,(0,y)); y+=t.size[1]+10
o.thumbnail((1400,2400)); o.save('mapdiff.png'); print(o.size)
