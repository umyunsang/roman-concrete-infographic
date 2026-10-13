import json, numpy as np
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
S=1.9992
im=np.array(Image.open(R+'idpass/id_id_map.png'))
full=(im[...,0].astype(np.int64)<<16)|(im[...,1].astype(np.int64)<<8)|im[...,2]
fa=im[...,3]>0
parts={'D3_light':0x160602,'D3_middle':0x1a0602,'D3_heavy':0x120602,'D3_foundation':0xe0602,'brick1':0x20602,'brick2':0x60602,'brick3':0xa0602}
masks={k:(full==v)&fa for k,v in parts.items()}
# light = light + bricks
masks['D3_light_all']=masks['D3_light']|masks['brick1']|masks['brick2']|masks['brick3']
def dist(mask, x, y):
    ys,xs=np.nonzero(mask)
    px=(xs+0.5)/S; py=(ys+0.5)/S
    d=np.hypot(px-x,py-y)
    i=d.argmin()
    return round(float(d[i]),2), (round(float(px[i]),1), round(float(py[i]),1))
leads={'가벼운 벽돌 S_lead03':(314.6,1232.0),'중간 돌 S_lead05':(314.6,1258.5),'무거운 돌 S_lead07':(316.6,1287.0),'기초 S_lead09':(319.6,1308.0)}
for n,(x,y) in leads.items():
    print(n, {k:dist(masks[k],x,y) for k in ['D3_light_all','D3_middle','D3_heavy','D3_foundation']})
# also: right-edge x of each part at leader y (row scan)
for n,(x,y) in leads.items():
    r=int(y*S)
    row={k: (np.nonzero(masks[k][r])[0].max()+1)/S if masks[k][r].any() else None for k in ['D3_light_all','D3_middle','D3_heavy','D3_foundation']}
    print(n,'row y',y,{k:(round(v,1) if v else None) for k,v in row.items()})
