import numpy as np
from PIL import Image, ImageDraw, ImageCms
Image.MAX_IMAGE_PIXELS=None
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/'
# soft-proofed 300dpi print render
cm=Image.open('cmyk300.tif')
pso=ImageCms.getOpenProfile(B+'PSOcoated_v3.icc'); srgb=ImageCms.createProfile('sRGB')
t=ImageCms.buildTransform(pso,srgb,'CMYK','RGB',renderingIntent=1)
P=ImageCms.applyTransform(cm,t); P.save('print_proof300.png')
W,H=P.size; tr=35.42
def strip(box, name, scale=1):
    im=P.crop(box)
    d=ImageDraw.Draw(im)
    x0,y0,x1,y1=box
    # trim lines
    for xx in (tr, W-tr):
        if x0<=xx<=x1: d.line([(xx-x0,0),(xx-x0,y1-y0)], fill=(255,0,255))
    for yy in (tr, H-tr):
        if y0<=yy<=y1: d.line([(0,yy-y0),(x1-x0,yy-y0)], fill=(255,0,255))
    if scale!=1: im=im.resize((int(im.width*scale), int(im.height*scale)), Image.NEAREST)
    im.save(name)
strip((0,0,700,700),'e_tl.png')
strip((W-700,0,W,700),'e_tr.png')
strip((0,H-700,700,H),'e_bl.png')
strip((W-700,H-700,W,H),'e_br.png')
# whole-edge thin strips (120px wide) rotated into a mosaic downscaled 0.5
L=P.crop((0,0,120,H)); R=P.crop((W-120,0,W,H))
T=P.crop((0,0,W,120)); Bt=P.crop((0,H-120,W,H))
mos=Image.new('RGB',(120*2+20, H),(255,255,255)); mos.paste(L,(0,0)); mos.paste(R,(140,0))
d=ImageDraw.Draw(mos); d.line([(tr,0),(tr,H)],fill=(255,0,255)); d.line([(140+120-tr,0),(140+120-tr,H)],fill=(255,0,255))
mos.resize((mos.width//2, H//2)).save('e_LR.png')
mos2=Image.new('RGB',(W,120*2+20),(255,255,255)); mos2.paste(T,(0,0)); mos2.paste(Bt,(0,140))
d=ImageDraw.Draw(mos2); d.line([(0,tr),(W,tr)],fill=(255,0,255)); d.line([(0,140+120-tr),(W,140+120-tr)],fill=(255,0,255))
mos2.resize((W//2, mos2.height//2)).save('e_TB.png')
