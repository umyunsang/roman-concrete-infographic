import sys; sys.path.insert(0,'.')
import numpy as np
from lstar import load, Lstar
P='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/figma_import/map_v8_13_without_text_2x.png'
L=Lstar(load(P))
axis=sys.argv[1]; c=float(sys.argv[2]); a0=float(sys.argv[3]); a1=float(sys.argv[4]); step=float(sys.argv[5]) if len(sys.argv)>5 else 2
out=[]
for t in np.arange(a0,a1,step):
    if axis=='y': v=L[int(c*2), int(t*2)]
    else: v=L[int(t*2), int(c*2)]
    out.append(f'{t:.0f}:{v:.0f}')
print(' '.join(out))
