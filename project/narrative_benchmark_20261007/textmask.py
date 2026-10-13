import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
P=np.array(Image.open(R+'r11/poster_2x.png').convert('RGB')).astype(int)
M=np.array(Image.open(R+'r11/map_only_2x.png').convert('RGB')).astype(int)
print(P.shape, M.shape)
h=min(P.shape[0],M.shape[0]); w=min(P.shape[1],M.shape[1])
P=P[:h,:w]; M=M[:h,:w]
diff=np.abs(P-M).max(-1)
T=json.load(open(R+'text_spec_r11.json'))['texts']
box=np.zeros((h,w),bool); lab=np.zeros((h,w),np.int32)
for i,t in enumerate(T):
    x,y,bw,bh=t[1]; m=2
    x0=int((x-m)*2); x1=int((x+bw+m)*2); y0=int((y-m)*2); y1=int((y+bh+m)*2)
    box[max(0,y0):y1,max(0,x0):x1]=True; lab[max(0,y0):y1,max(0,x0):x1]=i+1
ink=(diff>40)&box
print('ink px', ink.sum(), 'diff>40 outside boxes', ((diff>40)&~box).sum())
np.save('ink2.npy',ink); np.save('inklab2.npy',np.where(ink,lab,0))
