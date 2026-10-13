import sys, numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
W=sys.argv[1]; tag=sys.argv[2]
m=Image.open(f'{W}/renders/{tag}_print_bleed_map_pass.png').convert('RGBA'); o=Image.open(f'{W}/renders/{tag}_print_bleed_overlay_pass.png').convert('RGBA')
a=np.array(Image.alpha_composite(m,o).convert('RGB')).astype(float)
def prof(lines, label):
    print(label); prev=None
    for i,v in lines:
        d = '' if prev is None else f'  d={np.abs(v-prev).max():5.1f}'
        print(f'  {i:5d} {v.round(1)}{d}'); prev=v
prof([(i, a[i].mean(0)) for i in range(0,30)], 'top rows (mean RGB)')
prof([(j, a[:, j].mean(0)) for j in range(a.shape[1]-30, a.shape[1])], 'right cols')
prof([(j, a[:, j].mean(0)) for j in range(0,8)], 'left cols')
prof([(i, a[i].mean(0)) for i in range(a.shape[0]-8, a.shape[0])], 'bottom rows')
