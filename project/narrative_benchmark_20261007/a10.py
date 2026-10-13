import numpy as np
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS=None
RV='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
W='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/'
f4=Image.open(W+'print_frame_4x.png'); print('frame4x', f4.size, f4.mode)
poster=Image.open(RV+'r9/poster_2x.png').convert('RGB')
pr=Image.open('print_softproof_trim_2x.png')
# print frame 4x -> downsample to 2x and crop trim
f2=f4.convert('RGB').resize((f4.size[0]//2, f4.size[1]//2), Image.LANCZOS).crop((17,17,17+2382,17+3368))
regions=[('colosseum print loc',(330,890,450,990)),('colosseum design loc',(700,600,820,700)),('harbor print',(0,1420,90,1490)),('harbor design',(200,1440,300,1500)),('tyrrhenian print',(520,1580,660,1665)),('vesuvius print',(880,1470,1010,1550)),('vesuvius design',(990,1220,1110,1300)),('pompeii print',(730,1480,830,1540))]
tiles=[]
for name,(x0,y0,x1,y1) in regions:
    a=poster.crop((x0*2,y0*2,x1*2,y1*2)); b=pr.crop((x0*2,y0*2,x1*2,y1*2)); c=f2.crop((x0*2,y0*2,x1*2,y1*2))
    w,h=a.size; t=Image.new('RGB',(w*3+20,h+20),'white'); t.paste(a,(0,20)); t.paste(b,(w+10,20)); t.paste(c,(2*w+20,20))
    ImageDraw.Draw(t).text((4,4),name+'  [design | printPDF | frame4x]',fill='black'); tiles.append(t)
for i in range(0,len(tiles),2):
    grp=tiles[i:i+2]; H=sum(t.size[1] for t in grp)+10; Wm=max(t.size[0] for t in grp)
    o=Image.new('RGB',(Wm,H),'white'); y=0
    for t in grp: o.paste(t,(0,y)); y+=t.size[1]+10
    o.save('loc_%d.png'%(i//2))
print('ok')
