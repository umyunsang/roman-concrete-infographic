import numpy as np, json
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/'
P=np.asarray(Image.open('print_proof144aa.png').convert('L')).astype(np.float64)[17:17+3368,17:17+2382]
D=np.asarray(Image.open('poster_proof144.png').convert('L')).astype(np.float64)
spec=json.load(open(B+'review_loop/text_spec_r10.json'))['texts']
def pc(a,b):
    a=a-a.mean(); b=b-b.mean()
    A=np.fft.fft2(a); Bf=np.fft.fft2(b); R=A*np.conj(Bf); R/=np.abs(R)+1e-9
    r=np.real(np.fft.ifft2(R)); y,x=np.unravel_index(np.argmax(r),r.shape)
    H,W=r.shape
    if y>H/2:y-=H
    if x>W/2:x-=W
    return x,y,r.max()
worst=[]
for t in spec:
    tid,(x,y,w,h),rot,al,segs=t
    x0,y0=int((x-4)*2),int((y-4)*2); x1,y1=int((x+w+4)*2),int((y+h+4)*2)
    a=P[y0:y1,x0:x1]; b=D[y0:y1,x0:x1]
    # dark-ink masks
    ma=a<110; mb=b<110
    inter=(ma&mb).sum(); uni=(ma|mb).sum()
    dx,dy,pk=pc(a,b)
    worst.append((inter/max(uni,1), tid, rot, dx/2, dy/2, ma.sum(), mb.sum()))
worst.sort()
for w_ in worst[:12]: print('IoU %.3f %s rot %s shift(pt) dx %.1f dy %.1f inkpx print %d design %d'%w_)
print('rotated:'); [print('  IoU %.3f %s rot %s shift dx %.1f dy %.1f ink %d/%d'%w_) for w_ in worst if w_[2]!=0]
