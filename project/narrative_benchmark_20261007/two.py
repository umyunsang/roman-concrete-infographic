import sys; sys.path.insert(0,"/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/ov3")
from lib import *
m2=np.asarray(Image.open('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/r11/map_only_2x.png').convert('RGB'))
c=np.load(W+'comp3x.npy')
# downsample comp3x to 2x size and compare
c2=np.asarray(Image.fromarray(c).resize((m2.shape[1],m2.shape[0]),Image.LANCZOS))
d=np.abs(c2.astype(int)-m2.astype(int))
print(m2.shape, 'mean abs diff', d.mean(), np.percentile(d,99))
# compare in a region far from text: road appia area
ys=slice(int(950*2),int(985*2)); xs=slice(int(980*2),int(1030*2))
print('appia region diff', d[ys,xs].mean())
L2=Lstar(m2[ys,xs]); L3=Lstar(c2[ys,xs]); print(np.percentile(L2,[5,50,95]), np.percentile(L3,[5,50,95]))
