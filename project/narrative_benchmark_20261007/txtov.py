import json, numpy as np
from PIL import Image
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
idx=json.load(open(B+'obj_r11/assets_index.json'))
ts=json.load(open(B+'text_spec_r11.json'))['texts']
mine=['road_core_se','road_core_se_2','road_appia','road_ostiensis','water_sea','water_tiber','ground_land','tree_t_cypress','tree_t_pine_004','tree_t_pine_022','trees_s','trees_se']
for a in idx['assets']:
    if a['id'] not in mine: continue
    rgba=np.asarray(Image.open(a['files']['isolated_rgba']).convert('RGBA'))
    M=rgba[...,3]>=128
    x0,x1,y0,y1=a['crop_pt']; S=a['scale']
    for t in ts:
        tid,(tx,ty,tw,th),rot=t[0],t[1],t[2]
        if rot!=0: continue
        px0=int(round((tx-x0)*S)); px1=int(round((tx+tw-x0)*S)); py0=int(round((ty-y0)*S)); py1=int(round((ty+th-y0)*S))
        px0=max(px0,0); py0=max(py0,0); px1=min(px1,M.shape[1]); py1=min(py1,M.shape[0])
        if px1<=px0 or py1<=py0: continue
        ov=M[py0:py1,px0:px1].sum()/S**2
        if ov>0 and a['id'] not in ('ground_land',):
            print(a['id'], tid, ''.join(s[0] for s in t[4])[:30].replace('\n','/'), 'box-overlap pt2 %.1f'%ov)
