import numpy as np, json
from PIL import Image
from scipy import ndimage as ndi
from skimage import color, measure, morphology
from collections import Counter
Image.MAX_IMAGE_PIXELS=None
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/'
im=np.asarray(Image.open(B+'nb_work/review_loop/r11/map_only_2x.png').convert('RGB')).astype(float)/255
code2=np.load(B+'objform_b1/code2.npy')
m=code2==132830
ys,xs=np.nonzero(m); y0,y1,x0,x1=ys.min()-25,ys.max()+26,xs.min()-25,xs.max()+26
mm=m[y0:y1,x0:x1]; cc=code2[y0:y1,x0:x1]; lab=color.rgb2lab(im[y0:y1,x0:x1])
S=2.0
f=morphology.remove_small_objects(ndi.binary_fill_holes(mm),20)
di=ndi.distance_transform_edt(f); do=ndi.distance_transform_edt(~f)
inner=f&(di>=1*S)&(di<=3*S); outer=(~f)&(do>=1*S)&(do<=3*S)
H,W=f.shape; r=int(4*S)
res=[]
holes_f=ndi.binary_fill_holes(f)
for c in measure.find_contours(f.astype(float),0.5):
  if len(c)<10: continue
  seg=np.sqrt((np.diff(c,axis=0)**2).sum(1)); L=np.r_[0,np.cumsum(seg)]
  for t in np.arange(0,L[-1],S):
    j=min(np.searchsorted(L,t),len(c)-1); py,px=c[j]
    a0,a1,b0,b1=max(0,int(py)-r),min(H,int(py)+r+1),max(0,int(px)-r),min(W,int(px)+r+1)
    yy,xx=np.mgrid[a0:a1,b0:b1]; dd=(yy-py)**2+(xx-px)**2<=r*r
    mi=inner[a0:a1,b0:b1]&dd; mo=outer[a0:a1,b0:b1]&dd
    if mi.sum()<3 or mo.sum()<3: continue
    li=np.median(lab[a0:a1,b0:b1][mi],axis=0); lo=np.median(lab[a0:a1,b0:b1][mo],axis=0)
    dL=li[0]-lo[0]; dE=float(color.deltaE_ciede2000(li[None],lo[None])[0])
    oc=cc[a0:a1,b0:b1][mo]; oc=oc[oc>=0]; ocode=int(np.bincount(oc).argmax()) if len(oc) else -1
    isinner = bool(holes_f[int(py),int(px)]) and False
    res.append(((px+x0)/2,(py+y0)/2,dL,dE,ocode))
R=np.array([(a,b,c,d) for a,b,c,d,e in res]); codes=[e for *_,e in res]
ok=(np.abs(R[:,2])>=10)|(R[:,3]>=10)
print('n',len(R),'ok frac',round(ok.mean(),3))
cnt=Counter(); cntf=Counter()
for o,c in zip(ok,codes):
  cnt[c]+=1
  if not o: cntf[c]+=1
for k,v in cnt.most_common(8): print('outer code',k,'n',v,'fail',cntf[k],'fail frac',round(cntf[k]/v,2))
# fail positions by screen x bins
fx=R[~ok,0]; print('fail x hist', np.histogram(fx,bins=[830,870,910,950,990,1030,1070,1110,1172])[0])
print('all x hist ', np.histogram(R[:,0],bins=[830,870,910,950,990,1030,1070,1110,1172])[0])
