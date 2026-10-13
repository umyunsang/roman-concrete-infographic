import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx={a['id']:a for a in json.load(open(R+'assets_index.json'))['assets']}
def full_mask(aid):
    a=idx[aid]; x0,x1,y0,y1=a['crop_pt']
    al=np.array(Image.open(a['files']['isolated_rgba']))[...,3]>=128
    u0=int(round(x0*3)); v0=int(round(y0*3)); h,w=al.shape
    return al, u0, v0
mine='road_core_se road_core_se_2 road_appia road_ostiensis tree_t_cypress tree_t_pine_004 tree_t_pine_022 trees_s trees_se water_sea water_tiber'.split()
skip={'ground_land'}
res={}
for A in mine:
    alA,uA,vA=full_mask(A); hA,wA=alA.shape
    pad=60  # 20pt*3
    X0=uA-pad; Y0=vA-pad; W=wA+2*pad; H=hA+2*pad
    MA=np.zeros((H,W),bool); MA[pad:pad+hA,pad:pad+wA]=alA
    bA=MA&~ndi.binary_erosion(MA)
    dA=ndi.distance_transform_edt(~MA)
    out=[]
    for B,a in idx.items():
        if B==A or B in skip: continue
        alB,uB,vB=full_mask(B); hB,wB=alB.shape
        # place B in A window
        MB=np.zeros((H,W),bool)
        sx0=max(uB,X0); sx1=min(uB+wB,X0+W); sy0=max(vB,Y0); sy1=min(vB+hB,Y0+H)
        if sx0>=sx1 or sy0>=sy1: continue
        MB[sy0-Y0:sy1-Y0, sx0-X0:sx1-X0]=alB[sy0-vB:sy1-vB, sx0-uB:sx1-uB]
        if not MB.any(): continue
        ov=MA&MB
        if ov.any():
            # overlap thickness: max EDT inside overlap *2
            s=-2*ndi.distance_transform_edt(ov).max()/3
        else:
            s=dA[MB].min()/3
        if s>20: continue
        bB=MB&~ndi.binary_erosion(MB)
        dB=ndi.distance_transform_edt(~bB)
        par=(bA&(dB<=3)).sum()/3
        out.append((B,round(float(s),2),round(float(par),1), round(ov.sum()/9,1)))
    out.sort(key=lambda t:t[1])
    res[A]=out
    print(A, out)
json.dump(res,open('pairs.json','w'))
