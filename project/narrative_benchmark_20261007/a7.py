import numpy as np, sys
from PIL import Image, ImageCms, ImageDraw
Image.MAX_IMAGE_PIXELS=None
RV='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
W='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/'
poster=Image.open(RV+'r9/poster_2x.png').convert('RGB')
pso = ImageCms.getOpenProfile(W+'PSOcoated_v3.icc'); srgb=ImageCms.createProfile('sRGB')
t = ImageCms.buildTransform(pso, srgb, 'CMYK', 'RGB', renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC, flags=ImageCms.Flags.BLACKPOINTCOMPENSATION)
pr = ImageCms.applyTransform(Image.open('print_cmyk_144.tif'), t).crop((17,17,17+2382,17+3368))
pr.save('print_softproof_trim_2x.png')
regions=[(90,360,220,480),(300,500,420,560),(700,600,800,680)]
rows=[]
for (x0,y0,x1,y1) in regions:
    a=poster.crop((x0*2,y0*2,x1*2,y1*2)); b=pr.crop((x0*2,y0*2,x1*2,y1*2))
    w,h=a.size; c=Image.new('RGB',(w*2+10,h),'white'); c.paste(a,(0,0)); c.paste(b,(w+10,0)); rows.append(c)
H=sum(r.size[1] for r in rows)+10*len(rows); Wm=max(r.size[0] for r in rows)
out=Image.new('RGB',(Wm,H),'white'); y=0
for r in rows: out.paste(r,(0,y)); y+=r.size[1]+10
out.save('cmp_labels.png'); print(out.size)
