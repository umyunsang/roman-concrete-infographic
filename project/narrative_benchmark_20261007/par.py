import json, numpy as np, sys
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx={a['id']:a for a in json.load(open(R+'assets_index.json'))['assets']}
def fm(aid):
    a=idx[aid]; x0,x1,y0,y1=a['crop_pt']
    al=np.array(Image.open(a['files']['isolated_rgba']))[...,3]>=128
    M=np.zeros((5052,3573),bool); u0=int(round(x0*3)); v0=int(round(y0*3)); h,w=al.shape
    M[v0:v0+h,u0:u0+w]=al[:5052-v0,:3573-u0]; return M
for A,B in [('trees_se','fields_se'),('tree_t_pine_022','fields_se'),('trees_s','fields_s'),('tree_t_cypress','fields_e')]:
    MA=fm(A); MB=fm(B)
    ys,xs=np.nonzero(MA|MB); sl=(slice(ys.min()-5,ys.max()+5),slice(xs.min()-5,xs.max()+5))
    MA=MA[sl]; MB=MB[sl]
    bA=MA&~ndi.binary_erosion(MA); bB=MB&~ndi.binary_erosion(MB)
    dB=ndi.distance_transform_edt(~bB)
    P=bA&(dB<=3)
    lab,n=ndi.label(P,structure=np.ones((3,3)))
    if n==0: print(A,B,'none'); continue
    # length of each run ~ max extent (diagonal of bbox) in pt
    runs=[]
    for k,s in enumerate(ndi.find_objects(lab)):
        h=(s[0].stop-s[0].start)/3; w=(s[1].stop-s[1].start)/3
        runs.append(round(float(np.hypot(h,w)),1))
    runs.sort(reverse=True)
    print(A,B,'total %.1f pt'%(P.sum()/3),'runs',len(runs),'longest',runs[:6])
