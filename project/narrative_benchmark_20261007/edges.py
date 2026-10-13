import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/'
src=np.asarray(Image.open(B+'v8_12_map_print_bleed_5033x7087.png').convert('RGB')).astype(np.float32)
H,W=src.shape[:2]
L=src.mean(2)
def prof(name, arr):
    print(name, ' '.join('%.0f'%v for v in arr))
prof('top rows 0-49 mean lum', [L[r,:].mean() for r in range(0,50)])
prof('bottom rows H-50..H-1', [L[r,:].mean() for r in range(H-50,H)])
prof('left cols 0-49', [L[:,c].mean() for c in range(0,50)])
prof('right cols W-50..W-1', [L[:,c].mean() for c in range(W-50,W)])
# local: per 100px segment, max abs diff between row r and row 40 (inside trim), to detect band
for name, get in [('top', lambda r: src[r]), ('bottom', lambda r: src[H-1-r]), ('left', lambda r: src[:,r]), ('right', lambda r: src[:,W-1-r])]:
    ref=get(40)
    worst=[]
    for r in range(0,36):
        d=np.abs(get(r)-ref).sum(1)
        n=len(d)//100*100
        seg=d[:n].reshape(-1,100).mean(1)
        worst.append(seg.max())
    print(name,'edge rows 0..35 max 100px-seg diff vs row 40:', ' '.join('%.0f'%v for v in worst))
