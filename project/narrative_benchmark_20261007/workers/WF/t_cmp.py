import numpy as np, sys
from PIL import Image
W = sys.argv[1]
raw = np.asarray(Image.open(W + '/workers/WF/dl_raw/map_raw.png').convert('RGB')).astype(int)
mo = np.asarray(Image.open(W + '/review_loop/r11/map_only_2x.png').convert('RGB')).astype(int)
print('raw vs r11 map_only: max', np.abs(raw - mo).max(), 'n px diff', int((np.abs(raw - mo).max(2) > 0).sum()))
a = np.asarray(Image.open(W + '/workers/WF/poster_2x_after.png').convert('RGB')).astype(int)
b = np.asarray(Image.open(W + '/review_loop/r11/poster_2x.png').convert('RGB')).astype(int)
d = np.abs(a - b).max(2) > 8
ys, xs = np.nonzero(d)
print('after vs r11 poster: n px >8', int(d.sum()))
# cluster bboxes of differences on a coarse grid
from scipy.ndimage import label, find_objects, binary_dilation
lab, n = label(binary_dilation(d, iterations=6))
for i, sl in enumerate(find_objects(lab)):
    cnt = int(d[sl].sum())
    if cnt > 20: print('diff region pt', [sl[1].start / 2, sl[0].start / 2, sl[1].stop / 2, sl[0].stop / 2], 'px', cnt)
