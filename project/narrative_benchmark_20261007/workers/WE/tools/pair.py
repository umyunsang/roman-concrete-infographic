import sys, os
from PIL import Image, ImageDraw
rd, cd, ta, tb = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
names = sys.argv[5:]
for n in names:
    a = Image.open(f'{rd}/{ta}_{n}_x4.png').convert('RGB'); b = Image.open(f'{rd}/{tb}_{n}_x4.png').convert('RGB')
    maxw = 1400
    if a.width > maxw:
        s = maxw / a.width; a = a.resize((maxw, int(a.height * s))); b = b.resize((maxw, int(b.height * s)))
    if a.width >= a.height:
        S = Image.new('RGB', (a.width, a.height * 2 + 6), 'white'); S.paste(a, (0, 0)); S.paste(b, (0, a.height + 6))
    else:
        S = Image.new('RGB', (a.width * 2 + 6, a.height), 'white'); S.paste(a, (0, 0)); S.paste(b, (a.width + 6, 0))
    d = ImageDraw.Draw(S); d.text((4, 4), f'{ta} (before)', fill=(255, 0, 0)); d.text((4 if a.width >= a.height else a.width + 10, (a.height + 10) if a.width >= a.height else 4), f'{tb} (after)', fill=(255, 0, 0))
    S.save(f'{cd}/ba_{n}.png')
print('ok')
