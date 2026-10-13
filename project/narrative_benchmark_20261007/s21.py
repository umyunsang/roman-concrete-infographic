import sys; sys.path.insert(0,"/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/oc_b1")
from base import *
from PIL import Image
m11,ov11=r11_obj(); n2i=name2id()
mat,obj,matname,objkey=v813()
mo=np.asarray(Image.open(B+'nb_work/review_loop/r11/map_only_2x.png').convert('RGB')).astype(float)
inv13=json.load(open(B+'objcolor/inventory_v8_13.json'))['materials']
for aid in ['landmark_lime_kiln','support_pompeii_site','support_harbor','landmark_vesuvius','landmark_apennines','support_ruin_observers','landmark_aqueduct','landmark_pompeii_town','support_privernum','support_breakwater_block']:
    a=A[aid]; ids=[n2i[n] for n in a['objects']]; keys=[objkey[n] for n in a['objects']]
    msk=np.isin(m11,ids)&(ov11==0)
    tot=[]
    for k in np.unique(mat[msk & np.isin(obj,keys)]):
        reg=msk&(mat==k)
        er=ndi.binary_erosion(reg,iterations=2)  # 1pt band at 2x
        ys,xs=np.where(er)
        if len(ys)==0: continue
        # sample map_only (2x exact 2.0) at id grid coords
        yy=np.clip(np.round((ys+0.5)*2/S2-0.5).astype(int),0,mo.shape[0]-1); xx=np.clip(np.round((xs+0.5)*2/S2-0.5).astype(int),0,mo.shape[1]-1)
        px=mo[yy,xx]
        u,iv=np.unique(px.astype(np.uint8),axis=0,return_inverse=True); iv=iv.reshape(-1)
        Rl=ramp_lab(inv13[matname[int(k)]]['diffuse']); d=np.min(np.stack([de00(lab(u.astype(float)),r[None,:]) for r in Rl],1),1)[iv]
        big=np.zeros(reg.shape,bool); big[ys[d>8],xs[d>8]]=True
        lb,n=ndi.label(big,structure=np.ones((3,3))); sz=ndi.sum(big,lb,range(1,n+1)) if n else []
        cl=[int(s) for s in sz if s>=4]
        tot.append((matname[int(k)].split('.')[-1], round(float((d>8).mean()*100),3), cl))
    print(aid,tot)
