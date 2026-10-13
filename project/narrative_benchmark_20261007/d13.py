import json, numpy as np
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
T={t[0]:t for t in json.load(open(R+'text_spec_r11.json'))['texts']}
TL=json.load(open(R+'text_spec_r11.json'))['texts']
oid=json.load(open('oid.json')); a2o=json.load(open('a2o.json'))
final=np.load('final.npy'); il=np.load('inklab2.npy')
h=min(final.shape[0],il.shape[0]); w=min(final.shape[1],il.shape[1]); final=final[:h,:w]; il=il[:h,:w]
wm_sea=np.load('wm_sea.npy')[:h,:w]; wm_riv=np.load('wm_riv.npy')[:h,:w]
named=[a for a in a2o if a.startswith(('landmark_','support_','detail_','core','basic_'))]+['road_appia','water_sea','water_tiber']
def V(aid):
    m=np.isin(final,[oid[o] for o in a2o[aid] if o!='W_water_marks'])
    if aid=='water_sea': m|=wm_sea
    if aid=='water_tiber': m|=wm_riv
    return m
def lab(tid): return il==([t[0] for t in TL].index(tid)+1)
def dmin(m1,m2):
    return ndi.distance_transform_edt(~m2)[m1].min()/2
for aid,tid in [('road_appia','790:107'),('water_tiber','797:80'),('water_sea','790:124')]:
    L=lab(tid); VA=V(aid)
    d_own=dmin(L,VA); inside=(L&VA).sum()
    dos=sorted([(round(dmin(L,V(b)),1),b) for b in named if b!=aid])[:3]
    # d_rev: A to other labels
    others=[]
    for t in TL:
        if t[0]==tid: continue
        Lt=lab(t[0])
        if not Lt.any(): continue
        others.append((round(dmin(Lt,VA),1),t[0],''.join(s[0] for s in t[4])[:14]))
    others.sort()
    print('13',aid,tid,'d_own %.1f inside_px %d'%(d_own,inside),'d_other',dos,'d_rev',others[:3])
