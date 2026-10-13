import sys
from PIL import Image, ImageDraw
src,x0,y0,x1,y1,k,out=sys.argv[1],*map(int,sys.argv[2:6]),int(sys.argv[6]),sys.argv[7]
im=Image.open(src).convert('RGB').crop((x0,y0,x1,y1)); im=im.resize((im.width*k,im.height*k),Image.NEAREST)
d=ImageDraw.Draw(im)
for yy in range(y0 - y0%10 + 10, y1, 10):
    Y=(yy-y0)*k; d.line([(0,Y),(im.width,Y)],fill=(255,0,0) if yy%50==0 else (255,180,180),width=1); d.text((2,Y+1),str(yy),fill=(200,0,0))
for xx in range(x0 - x0%10 + 10, x1, 10):
    X=(xx-x0)*k; d.line([(X,0),(X,im.height)],fill=(0,0,255) if xx%50==0 else (180,180,255),width=1); d.text((X+1,2),str(xx),fill=(0,0,200))
im.save(out); print(out, im.size)
