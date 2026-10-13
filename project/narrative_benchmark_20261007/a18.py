import numpy as np
from PIL import Image, ImageDraw, ImageCms
Image.MAX_IMAGE_PIXELS=None
W='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/'
pso=ImageCms.getOpenProfile(W+'PSOcoated_v3.icc'); srgb=ImageCms.createProfile('sRGB')
t=ImageCms.buildTransform(pso,srgb,'CMYK','RGB',renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC,flags=0)
r=Image.open('print_cmyk_300.tif')
Wd,H=r.size; tp=35.4
S=360
boxes=[(0,0),(Wd-S,0),(0,H-S),(Wd-S,H-S)]
out=Image.new('RGB',(2*S+10,2*S+10),'white')
for i,(x,y) in enumerate(boxes):
    c=ImageCms.applyTransform(r.crop((x,y,x+S,y+S)),t)
    d=ImageDraw.Draw(c)
    # trim lines
    tx = tp if x==0 else (Wd-tp)-x
    ty = tp if y==0 else (H-tp)-y
    d.line([(tx,0),(tx,S)],fill=(255,0,0)); d.line([(0,ty),(S,ty)],fill=(255,0,0))
    out.paste(c,((i%2)*(S+10),(i//2)*(S+10)))
out.save('corners.png')
# whole page small with trim box
sm=ImageCms.applyTransform(r.resize((Wd//6,H//6),Image.LANCZOS),t)
d=ImageDraw.Draw(sm); d.rectangle([tp/6,tp/6,(Wd-tp)/6,(H-tp)/6],outline=(255,0,0))
sm.save('page_small.png'); print(sm.size)
