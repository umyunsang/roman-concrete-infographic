"""compose map+overlay passes (48%) into map_only_2x like scripts/compose_r11_map_v8_14.py; crop helper."""
import sys
from PIL import Image
def compose(prefix, out):
    maps=Image.open(prefix+'_map_pass.png').convert('RGBA'); ov=Image.open(prefix+'_overlay_pass.png').convert('RGBA')
    o=Image.alpha_composite(maps,ov).convert('RGB')
    pad=Image.new('RGB',(2382,3368)); pad.paste(o,(0,0))
    pad.paste(o.crop((2380,0,2381,3367)),(2381,0)); pad.paste(pad.crop((0,3366,2382,3367)),(0,3367))
    pad.save(out); return out
def crop(src, x0,x1,y0,y1, out, scale=3):
    im=Image.open(src)
    c=im.crop((int(x0*2),int(y0*2),int(x1*2),int(y1*2)))
    c=c.resize((int((x1-x0)*scale),int((y1-y0)*scale)),Image.Resampling.LANCZOS)
    c.save(out)
if __name__=='__main__':
    if sys.argv[1]=='compose': compose(sys.argv[2], sys.argv[3])
    else:
        a=sys.argv; crop(a[2],*map(float,a[3:7]),a[7],float(a[8]) if len(a)>8 else 3)
