import json, numpy as np, sys
from PIL import Image
from scipy import ndimage as ndi
from skimage import morphology
A='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx=json.load(open(A+'assets_index.json'))
for a in idx['assets']:
    if a['id'] not in sys.argv[1:]: continue
    iso=np.asarray(Image.open(a['files']['isolated_rgba'])).astype(float)
    ctx=np.asarray(Image.open(a['files']['context']).convert('RGB')).astype(float)
    al=iso[...,3]>=128
    diff=np.abs(iso[...,:3]-ctx).mean(-1)
    vis=al&(diff<=12)
    vis=morphology.opening(vis,morphology.disk(1)); vis=morphology.closing(vis,morphology.disk(2))
    lbl,n=ndi.label(vis); 
    if n==0: continue
    sz=ndi.sum(vis,lbl,range(1,n+1))
    keep=np.isin(lbl, 1+np.nonzero(sz>=sz.max()*0.02)[0])
    print(a['id'],'alpha px',al.sum(),'visible px',vis.sum(),'kept',keep.sum(),'frac',round(keep.sum()/al.sum(),3), 'area visible inventory pt2',a['area_visible_final_pt2'],'-> kept pt2',round(keep.sum()/9,1))
    Image.fromarray((keep*255).astype(np.uint8)).save('vis_%s.png'%a['id'])
