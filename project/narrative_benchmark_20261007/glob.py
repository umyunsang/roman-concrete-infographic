import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
ink=np.load('ink.npy'); g=np.load('grad.npy').astype(np.float32)
M=np.asarray(Image.open(R+'r10/map_only_2x.png').convert('RGB')).astype(np.int16)
ys,xs=np.nonzero(ink)
print('LY-23 ink extremes pt: left %.1f right-margin %.1f top %.1f bottom-margin %.1f'%(xs.min()/2,1191-(xs.max()+1)/2,ys.min()/2,1684-(ys.max()+1)/2))
# board extents: rows 60..200 pt, find object mask columns
paper=np.array([238,226,204])
dist=np.sqrt(((M-paper)**2).sum(2))
obj=(g>12)|(dist>28)
for ypt in (40,80,140,180,215,225):
    row=obj[int(ypt*2), 600:1720]
    xs_=np.nonzero(row)[0]
    print(' board row y=%d: x %.1f..%.1f center %.2f'%(ypt,(xs_.min()+600)/2,(xs_.max()+600+1)/2,((xs_.min()+600)/2+(xs_.max()+600+1)/2)/2))
# board bottom: scan column at x=596
for xpt in (380,450,596,750,815):
    col=obj[300:560,int(xpt*2)]
    nz=np.nonzero(col)[0]
    print(' col x=%d board/obj bottom-ish rows (pt):'%xpt, [(r+300)/2 for r in nz[-3:]])
