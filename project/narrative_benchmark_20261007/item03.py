import json, numpy as np
from skimage.color import deltaE_ciede2000
m=json.load(open('metrics.json'))
T1={'core1_modern_building':1,'core2_hot_mixing':2,'detail_core3_lime_specimen':3,'detail_core4_three_cubes':4,'support_core5_lab':5}
txt={1:[528,702,382,485.5],2:[57.5,217.5,744,847.5],3:[408.5,598.5,1028,1115.5],4:[638.5,816.5,1028,1131.5],5:[982.5,1162.5,813,916.5]}
# recompute text unions from spec
spec=json.load(open('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/text_spec_r11.json'))
ids={1:['790:102','790:146','790:147','790:148'],2:['790:105','790:152','790:153','790:154'],3:['790:110','790:158','790:159','790:160'],4:['790:111','790:164','790:165','790:166'],5:['790:106','790:170','790:171','790:172']}
tb={t[0]:t[1] for t in spec['texts']}
for k,l in ids.items():
    bx=[tb[i] for i in l]
    txt[k]=[min(b[0] for b in bx),max(b[0]+b[2] for b in bx),min(b[1] for b in bx),max(b[1]+b[3] for b in bx)]
print('text unions',txt)
def gap(a,b):
    dx=max(0,max(a[0],b[0])-min(a[1],b[1])); dy=max(0,max(a[2],b[2])-min(a[3],b[3])); return float(np.hypot(dx,dy))
T5a=['landmark_pantheon','landmark_lime_kiln','landmark_aqueduct','landmark_vesuvius','landmark_pompeii_town','landmark_apennines','road_appia','road_ostiensis']
T5b=[k for k in m if k.startswith(('bridge_','fields_','road_core','tree_t','trees_'))]
cmp=['landmark_colosseum']+T5a+T5b
for c,k in T1.items():
    fig=m[c]['bbox']
    print('\n==',c, 'K=%.2f'%m[c]['K'])
    fails=[]
    for o in cmp:
        g=min(gap(m[o]['bbox'],fig),gap(m[o]['bbox'],txt[k]))
        if g<=198.5:
            de=float(deltaE_ciede2000(np.array(m[c]['rep_lab']),np.array(m[o]['rep_lab'])))
            dk=m[c]['K']-m[o]['K']
            ok = de>=10 or dk>=10
            print('  %-24s gap=%6.1f dE00=%5.1f dK=%6.2f %s'%(o,g,de,dk,'ok' if ok else 'FAIL'))
            if not ok: fails.append(o)
    print(' fails',fails)
# FOA for batch assets
print()
for a in ['detail_d1_seawater','detail_d2_making','detail_d3_tower','basic_recipe','basic_sources']:
    out=[]
    for c,k in T1.items():
        g=min(gap(m[a]['bbox'],m[c]['bbox']),gap(m[a]['bbox'],txt[k]))
        out.append((k,round(g,1)))
    print(a,out)
