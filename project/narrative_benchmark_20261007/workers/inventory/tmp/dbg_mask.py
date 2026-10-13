import json, sys
import numpy as np
from PIL import Image
inv = json.load(open(sys.argv[1])); m = np.array(Image.open(sys.argv[2]).convert('RGBA')).astype(np.int64)
names = [o['name'] for o in inv['objects']]
k = np.rint((m[..., :3] - 2) / 4).astype(np.int64); code = k[..., 0] + 64 * k[..., 1] + 4096 * k[..., 2]; code[m[..., 3] < 128] = 0
out = np.full(code.shape + (3,), 235, np.uint8)
cols = {'F_centuriatio': (60, 140, 60), 'R_core_road': (200, 60, 40), 'R1_road_landing1': (200, 60, 200), 'R1_road_landing5': (200, 60, 200), 'R1_road5_bed': (40, 60, 200)}
for nm, c in cols.items():
    out[code == names.index(nm) + 1] = c
im = Image.fromarray(out)
from PIL import ImageDraw
d = ImageDraw.Draw(im)
for x in range(0, 2382, 200): d.line([(x, 0), (x, 3368)], fill=(150, 150, 150))
for y in range(0, 3368, 200): d.line([(0, y), (2382, y)], fill=(150, 150, 150))
im.resize((im.width // 3, im.height // 3)).save(sys.argv[3])
