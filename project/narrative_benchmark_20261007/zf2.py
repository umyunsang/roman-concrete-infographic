import numpy as np
from PIL import Image
from skimage import color
RL='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/assets/'
def interior(aid,box,dark_thr,bump,dark=True,label=''):
    im=np.asarray(Image.open(RL+aid+'/isolated.png').convert('RGB')).astype(float)/255
    L=color.rgb2lab(im)[...,0]; x0,y0,x1,y1=box
    cnt=0; rows=[]
    for y in range(y0,y1):
        r=L[y,x0:x1] if dark else 100-L[y,x0:x1]
        thr=dark_thr if dark else 100-dark_thr
        idx=np.where(r<thr)[0]
        if len(idx)<2: continue
        # pixels between first and last dark pixel within a run of <=12px that are > dark+bump
        a,b=idx[0],idx[-1]
        if b-a>14: continue
        seg=r[a:b+1]; c=int((seg>thr+bump).sum())
        if c: cnt+=c; rows.append((y,c))
    print(label,'interior bright px',cnt,'= %.2f pt2'%(cnt/9),'rows',rows)
interior('support_core5_lab',(372,95,412,135),20,12,True,'C05 leak upper')
interior('support_core5_lab',(380,140,412,185),20,12,True,'C05 leak lower')
