import json, numpy as np
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
idx={a['id']:a for a in json.load(open(R+'obj_r11/assets_index.json'))['assets']}
T=json.load(open(R+'text_spec_r11.json'))['texts']
oid=json.load(open('oid.json')); a2o=json.load(open('a2o.json'))
final=np.load('final.npy'); ink=np.load('ink2.npy'); il=np.load('inklab2.npy')
h=min(final.shape[0],ink.shape[0]); w=min(final.shape[1],ink.shape[1])
final=final[:h,:w]; ink=ink[:h,:w]; il=il[:h,:w]
PX=2.0
# 2D marks: shape_* assets objects
marks=np.zeros_like(ink)
for aid,objs in a2o.items():
    if aid.startswith('shape_'):
        marks|=np.isin(final,[oid[o] for o in objs])
din=ndi.distance_transform_edt(~ink, return_indices=True)
dist_ink, (iy,ix)=din[0], din[1]
dmk=ndi.distance_transform_edt(~marks)
def V(aid):
    ids=[oid[o] for o in a2o[aid]]
    m=np.isin(final,ids)
    if aid in ('road_core_se','road_core_se_2'):
        b=idx[aid]['bbox_visible_final_pt']; r=np.zeros_like(m); r[int(b[2]*2):int(b[3]*2)+1,int(b[0]*2):int(b[1]*2)+1]=True; m&=r
        # for se region also include bed/landing; exclude se_2 overlap
    return m
sea=final==oid['L10_sea']; riv=final==oid['L02_tiber']; wm=final==oid['W_water_marks']
dsea=ndi.distance_transform_edt(~sea); driv=ndi.distance_transform_edt(~riv)
wm_sea=wm&(dsea<driv); wm_riv=wm&(driv<=dsea)
land_like=~(sea|riv|wm)
shore_sea=sea&ndi.binary_dilation(land_like&~wm)  # sea pixels adjacent to non-water
shore_riv=riv&ndi.binary_dilation(land_like&~wm)
out={}
for aid in ['road_core_se','road_core_se_2','road_appia','road_ostiensis','tree_t_cypress','tree_t_pine_004','tree_t_pine_022','trees_s','trees_se']:
    m=V(aid)
    d=dist_ink[m]; k=np.argmin(d); ys,xs=np.nonzero(m)
    ti=il[iy[ys[k],xs[k]],ix[ys[k],xs[k]]]-1
    dm=dmk[m].min()
    ov=(m&ink).sum()
    print('12',aid,'min text dist %.2f pt to %s %r rot %s'%(d[k]/PX, T[ti][0], ''.join(s[0] for s in T[ti][4])[:20], T[ti][2]),'overlap px',int(ov),'| min 2D-mark dist %.2f'%(dm/PX))
for nm,wmk,sh,own in [('water_sea',wm_sea,shore_sea,'790:124'),('water_tiber',wm_riv,shore_riv,None)]:
    for part,mm in [('waves',wmk),('shore',sh)]:
        # per text, min distance
        best=[]
        for i,t in enumerate(T):
            if t[0]==own: continue
            ti=(il==i+1)
            if not ti.any(): continue
            dd=ndi.distance_transform_edt(~mm) if False else None
        dmm=ndi.distance_transform_edt(~mm)
        rows=[]
        for i,t in enumerate(T):
            if t[0]==own: continue
            ti=(il==i+1)
            if not ti.any(): continue
            v=dmm[ti].min()/PX
            if v<12: rows.append((round(v,2),t[0],''.join(s[0] for s in t[4])[:16],t[2], int((ti&mm).sum())))
        rows.sort()
        print('12',nm,part,rows[:8])
    dmk2=ndi.distance_transform_edt(~marks)
    print('12',nm,'marks vs waves min %.2f'%(dmk2[wmk].min()/PX if wmk.any() else -1))
np.save('wm_sea.npy',wm_sea); np.save('wm_riv.npy',wm_riv)
