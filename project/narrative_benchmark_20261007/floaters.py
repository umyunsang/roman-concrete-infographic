import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
Image.MAX_IMAGE_PIXELS=None
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
ida=np.asarray(Image.open(B+'idpass/id_id_map.png'))[...,:3].astype(np.int64)
code=ida[...,0]*65536+ida[...,1]*256+ida[...,2]
idm=json.load(open('idmap.json')); obj2code={v['obj']:int(k) for k,v in idm.items()}
s=1.9992
groups={'landmark_colosseum':['COL_ruined','R3_colosseum_podium','R4_arena_skin'],'COL_only':['COL_ruined'],'landmark_pantheon':['R8_pantheon'],
 'bridge_north':['B_pons1'],'bridge_south':['B_pons2','R4_bridge_west_bed'],'MS1':['MS1_core1_to_2'],'MS2':['MS2_core2_to_34'],'MS3':['MS3_core34_to_5'],'roads':['R_core_road','R1_road_landing1']}
# parapets missing from idmap? check
print([n for n in ['B_pons1_parapet0','B_pons1_parapet1','B_pons2_parapet0','B_pons2_parapet1'] if n in obj2code])
for g,names in groups.items():
    names=names+[n for n in ['B_pons1_parapet0','B_pons1_parapet1'] if g=='bridge_north' and n in obj2code]+[n for n in ['B_pons2_parapet0','B_pons2_parapet1'] if g=='bridge_south' and n in obj2code]
    m=np.isin(code,[obj2code[n] for n in names if n in obj2code])
    lbl,n=ndi.label(m,structure=np.ones((3,3)))
    sz=ndi.sum(m,lbl,range(1,n+1))
    main=1+np.argmax(sz)
    dmain=ndi.distance_transform_edt(lbl!=main)
    out=[]
    for i in range(1,n+1):
        if i==main: continue
        area=sz[i-1]/s/s
        if area<1: continue
        gap=dmain[lbl==i].min()/s
        ys,xs=np.nonzero(lbl==i)
        out.append((round(area,1),round(gap,2),round(xs.min()/s,1),round(xs.max()/s,1),round(ys.min()/s,1),round(ys.max()/s,1)))
    out.sort(reverse=True)
    print(g,'components',n,'main area pt2',round(sz.max()/s/s,1),'others>=1pt2:',len(out))
    for o in out[:15]: print('   area %.1f gap %.2f x %.1f-%.1f y %.1f-%.1f'%o)
