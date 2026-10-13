import numpy as np, json
from PIL import Image
from skimage import color
RL='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/assets/'
def prof(aid,y,x0,x1,label,avg=3):
    im=np.asarray(Image.open(RL+aid+'/isolated.png').convert('RGB')).astype(float)/255
    L=color.rgb2lab(im)[...,0]
    p=L[y-avg:y+avg+1,x0:x1].mean(axis=0)
    d=np.diff(p)
    # detect steps: |d|>=? compare with smooth trend: second difference
    print(label,'y',y,'L* profile:',' '.join('%.0f'%v for v in p))
    dd=np.abs(np.diff(p,2))
    print('   max |1st diff| %.1f, max |2nd diff| %.1f'%(np.abs(d).max(),dd.max()))
prof('support_core5_lab',200,120,218,'C05 healed cyl')
prof('support_core5_lab',150,350,445,'C05 leak cyl')
prof('basic_sources',200,345,425,'B06 core sample')
prof('basic_sources',140,345,425,'B06 core sample hi')
