import sys; sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/op0')
from common import *
m, o, f = load_ids()
# free paper check for proposed heat-mark box x134.5-163.5, y959-974 (+4pt margin)
x0,x1,y0,y1 = [int(v*S) for v in (130.5,167.5,955,978)]
sub = f[y0:y1,x0:x1]
u, c = np.unique(CAT[sub], return_counts=True)
print('proposed heat box contents', dict(zip(u, (c/S**2).round(1))))
ink, red = text_ink()
print('ink in box', ink[y0:y1,x0:x1].sum())
d2V = asset_V(f,'detail_d2_making'); core2M = asset_M('core2_hot_mixing')
B = np.zeros_like(d2V); B[int(959*S):int(974*S), int(134.5*S):int(163.5*S)] = True
print('box→core2 M', gap(B, core2M)-0.5, 'box→dice', gap(B, id_mask(f, lambda n: n=='D2_cube'))-0.5, 'box→ms2', gap(B, asset_V(f,'milestone_2_to_34'))-0.5)
