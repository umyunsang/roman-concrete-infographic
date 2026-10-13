import sys; sys.path.insert(0,"/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/ov3")
from lib2 import *
from printsim import psim
import json
out={}
for aid in ['road_core_se','road_core_se_2','road_appia','road_ostiensis']:
    M=mask2(aid); sl=crop2(M); Ms=M[sl]; c=m2[sl]
    res=[]
    for img in (c, psim(c)):
        L=Lstar(img); hp=mhp(L,Ms); Mi=ndi.binary_erosion(Ms,iterations=1)
        lab=Lab(c); paver=Ms&(lab[...,2]<=6)
        joint=paver&(mhp(Lstar(c),Ms)<=-3); top=paver&(np.abs(mhp(Lstar(c),Ms))<1.5)
        topc=top&(ndi.distance_transform_edt(~joint)>1)
        A=np.percentile(hp[Mi],90)-np.percentile(hp[Mi],10)
        jd=np.median(L[joint])-np.median(L[topc])
        # ring g and fg
        d=ndi.distance_transform_edt(~Ms); rg=(d>6*P)&(d<=20*P)&(id2[sl]==NID['T_land'])
        fg=np.median(L[Ms])-np.median(L[rg])
        res.append((A,jd,fg))
    out[aid]=dict(A=[res[0][0],res[1][0]],joint=[res[0][1],res[1][1]],fg=[res[0][2],res[1][2]],
                  keep_A=res[1][0]/res[0][0],keep_joint=res[1][1]/res[0][1],keep_fg=res[1][2]/res[0][2])
    print(aid,json.dumps(out[aid],default=lambda x: round(float(x),3)))
json.dump(out,open('roads6.json','w'),default=float,indent=1)
