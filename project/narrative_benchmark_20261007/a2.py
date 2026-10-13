import numpy as np
from PIL import Image, ImageCms
Image.MAX_IMAGE_PIXELS=None
W='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/'
tac=np.load('tac.npy'); vmask=np.load('vmask.npy')
hi = tac>300
print('>300 in vector mask', (hi & vmask[:,:]).sum() if vmask.shape==hi.shape else 'shape', vmask.shape, hi.shape)
# cluster sizes of >300 using simple labeling via scipy-free approach: dilate and count
from collections import deque
ys,xs=np.where(tac>302)
pts=set(zip(ys.tolist(),xs.tolist()))
clusters=[]
while pts:
    p=pts.pop(); q=deque([p]); c=[p]
    while q:
        y,x=q.popleft()
        for dy in (-1,0,1):
            for dx in (-1,0,1):
                n=(y+dy,x+dx)
                if n in pts: pts.remove(n); q.append(n); c.append(n)
    clusters.append(c)
clusters.sort(key=len, reverse=True)
print('clusters >302:', len(clusters), 'largest sizes', [len(c) for c in clusters[:8]])
for c in clusters[:5]:
    a=np.array(c); print('  at y %d-%d x %d-%d (pt x %.0f y %.0f)'%(a[:,0].min(),a[:,0].max(),a[:,1].min(),a[:,1].max(), a[:,1].mean()*72/300-8.5, a[:,0].mean()*72/300-8.5))
# big diffs localization
bg = Image.open(W+'v8_11_map_print_bleed_5033x7087.png').convert('RGB')
srgb = ImageCms.createProfile('sRGB'); pso = ImageCms.getOpenProfile(W+'PSOcoated_v3.icc')
t = ImageCms.buildTransform(srgb, pso, 'RGB', 'CMYK', renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC, flags=0)
B = np.asarray(ImageCms.applyTransform(bg, t)).astype(np.int16)
R = np.asarray(Image.open('print_cmyk_300.tif')).astype(np.int16)[:7087]
d = np.abs(R-B).max(axis=2)
d[vmask[:7087]]=0
# dilate vmask by 3 to exclude AA edges
vm=vmask[:7087].copy()
for _ in range(3):
    vm = vm | np.roll(vm,1,0) | np.roll(vm,-1,0) | np.roll(vm,1,1) | np.roll(vm,-1,1)
d2=d.copy(); d2[vm]=0
print('max diff excluding vector+3px', d2.max(), 'n>60', (d2>60).sum(), 'n>30', (d2>30).sum())
ys,xs=np.where(d2>60)
if len(ys):
    print(' rows hist', np.histogram(ys, bins=[0,12,40,100,3500,3600,7000,7047,7075,7087])[0])
    print(' cols hist', np.histogram(xs, bins=[0,20,40,100,2500,2540,4990,5017,5033])[0])
# edges: mean diff in top 12 rows and right 16 cols
print('top 12 rows mean maxdiff', d[:12].mean(), 'rows 12-40', d[12:40].mean(), 'right16', d[:,-16:].mean(), 'cols -40:-16', d[:,-40:-16].mean())
print('bottom 12', d[-12:].mean(), 'left 12', d[:,:12].mean())
