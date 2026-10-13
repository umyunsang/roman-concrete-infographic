import sys
from PIL import Image
pref = sys.argv[1]; n = int(sys.argv[2])
for i in range(n):
    m = Image.open(f'{pref}_{i}_map.png').convert('RGBA'); o = Image.open(f'{pref}_{i}_ovl.png').convert('RGBA')
    Image.alpha_composite(m, o).convert('RGB').save(f'{pref}_{i}.png')
