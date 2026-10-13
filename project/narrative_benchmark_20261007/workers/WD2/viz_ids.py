import sys, json, numpy as np
from PIL import Image, ImageDraw
d = np.load(sys.argv[1]); out = sys.argv[2]; x0,x1,y0,y1 = map(float, sys.argv[3:7]); z = float(sys.argv[7]) if len(sys.argv)>7 else 2
ids = d['ids']; names = list(d['names']); step=float(d['step']); roi=d['roi']
sub = ids[int((y0-roi[2])/step):int((y1-roi[2])/step), int((x0-roi[0])/step):int((x1-roi[0])/step)]
rng = np.random.default_rng(3); pal = rng.integers(40, 230, (len(names)+1, 3)).astype(np.uint8)
special = {'T_land': (236,226,203), 'L10_sea': (130,185,188), 'W_water_marks': (255,255,255)}
for n,c in special.items():
    if n in names: pal[names.index(n)] = c
pal[-1] = (0,0,0)
img = pal[sub]
im = Image.fromarray(img).resize((int(sub.shape[1]*z), int(sub.shape[0]*z)), Image.NEAREST)
dr = ImageDraw.Draw(im)
spec = json.load(open(sys.argv[8])) if len(sys.argv)>8 else None
if spec:
    for t in spec['texts']:
        bx,by,bw,bh = t[1]
        if bx < x1 and bx+bw > x0 and by < y1 and by+bh > y0:
            dr.rectangle([ (bx-x0)*z, (by-y0)*z, (bx+bw-x0)*z, (by+bh-y0)*z ], outline=(255,0,0))
# legend: print object names present with pixel counts
u, c = np.unique(sub, return_counts=True)
for k, cnt in sorted(zip(u, c), key=lambda t: -t[1])[:40]:
    print(names[k] if k>=0 else 'NONE', cnt, tuple(pal[k]))
im.save(out)
