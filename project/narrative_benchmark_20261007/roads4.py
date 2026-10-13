import sys; sys.path.insert(0,"/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/ov3")
from lib2 import *
import json
res={}
for aid in ['road_core_se','road_core_se_2','road_appia','road_ostiensis','road_core_nw','road_core_sw','road_core_w']:
    M=mask2(aid); sl=crop2(M); Ms=M[sl]; L=L2[sl]; c=m2[sl]
    hp=mhp(L,Ms)
    Mi=ndi.binary_erosion(Ms,iterations=1)
    v=hp[Mi]; A=np.percentile(v,90)-np.percentile(v,10)
    lab=Lab(c); paver=Ms&(lab[...,2]<=6); curb=Ms&(lab[...,2]>8)
    joint=paver&(hp<=-3); top=paver&(hp>-1.5)&(hp<3)
    topc=top&(ndi.distance_transform_edt(~joint)>1)
    dLdet=np.median(L[joint])-np.median(L[topc])
    pav_only=Mi&~ndi.binary_dilation(curb,iterations=2)
    vp=hp[pav_only]; Ap=np.percentile(vp,90)-np.percentile(vp,10)
    res[aid]=dict(A2x=float(A),A2x_pavement_only=float(Ap),joint_dL=float(dLdet),sig_top=float(np.std(hp[topc])),top_L=float(np.median(L[topc])), joint_L=float(np.median(L[joint])))
    print(aid,{k:round(v,2) for k,v in res[aid].items()})
json.dump(res,open('roads4.json','w'),indent=1)
