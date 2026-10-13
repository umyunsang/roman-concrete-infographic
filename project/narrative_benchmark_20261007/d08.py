import json, numpy as np
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx={a['id']:a for a in json.load(open(R+'assets_index.json'))['assets']}
oid=json.load(open('oid.json')); a2o=json.load(open('a2o.json'))
final=np.load('final.npy')
def fm(aid):
    a=idx[aid]; x0,x1,y0,y1=a['crop_pt']
    al=np.array(Image.open(a['files']['isolated_rgba']))[...,3]>=128
    M=np.zeros((5052,3573),bool); u0=int(round(x0*3)); v0=int(round(y0*3)); h,w=al.shape
    M[v0:v0+h,u0:u0+w]=al[:5052-v0,:3573-u0]; return M
# final id upsampled to 3px/pt grid via index mapping
Y,X=np.mgrid[0:5052,0:3573]
F3=final[np.clip(((Y+0.5)/3*2).astype(int),0,final.shape[0]-1),np.clip(((X+0.5)/3*2).astype(int),0,final.shape[1]-1)]
info=[a for a in a2o if a.startswith(('landmark_','support_','detail_','core','basic_','milestone_','bridge_'))]+['water_tiber','water_sea','road_appia','road_core_nw','road_core_sw','road_core_w']
for A in ['road_core_se','road_core_se_2','road_appia','road_ostiensis','tree_t_cypress','tree_t_pine_004','tree_t_pine_022','trees_s','trees_se']:
    ids=[oid[o] for o in a2o[A]]
    VA=np.isin(F3,ids)
    if A in ('road_core_se','road_core_se_2'):
        b=idx[A]['bbox_visible_final_pt']; m=np.zeros_like(VA); m[int(b[2]*3):int(b[3]*3)+1,int(b[0]*3):int(b[1]*3)+1]=True; VA&=m
    ys,xs=np.nonzero(VA); box=(xs.min()-60,xs.max()+60,ys.min()-60,ys.max()+60)
    res=[]
    for B in info:
        if B==A: continue
        bb=idx[B]['crop_pt']
        if bb[0]*3>box[1] or bb[1]*3<box[0] or bb[2]*3>box[3] or bb[3]*3<box[2]: continue
        MB=fm(B)
        o=(MB&VA).sum()/max(1,MB.sum())
        if (MB&VA).sum()>0: res.append((B,round(100*o,3),round((MB&VA).sum()/9,1)))
    print('08',A,res)
