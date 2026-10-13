import json, numpy as np
from PIL import Image
from skimage import color
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx=json.load(open(B+'assets_index.json')); A={a['id']:a for a in idx['assets']}
inv={o['name']:o for o in json.load(open(B+'inventory.json'))['objects']}
def stats(aid, objname, shrink=0.35, box=None):
    a=A[aid]; x0,x1,y0,y1=a['crop_pt']
    rgba=np.asarray(Image.open(a['files']['isolated_rgba'])).astype(float)/255
    bx = box or inv[objname]['bbox_visible_final_pt']
    X0,X1,Y0,Y1=bx
    c0=int(round((X0-x0+shrink)*3)); c1=int(round((X1-x0-shrink)*3)); r0=int(round((Y0-y0+shrink)*3)); r1=int(round((Y1-y0-shrink)*3))
    sub=rgba[r0:r1, c0:c1]
    m=sub[...,3]>0.98
    if m.sum()==0: return None
    rgb=sub[...,:3][m]
    lab=color.rgb2lab(rgb.reshape(-1,1,3)).reshape(-1,3)
    return dict(n=int(m.sum()), L=round(float(np.median(lab[:,0])),2), Lmin=round(float(lab[:,0].min()),2), Lmax=round(float(lab[:,0].max()),2), Lstd=round(float(lab[:,0].std()),2), hex='#%02X%02X%02X'%tuple(int(v*255) for v in np.median(rgb,axis=0)))
for aid,objs in [('shape_core1_marker',['S_core1_badge','S_core1_underline']),('shape_core2_marker',['S_core2_badge','S_core2_underline']),('shape_core3_marker',['S_core3_badge','S_core3_underline']),('shape_core4_marker',['S_core4_badge','S_core4_underline']),('shape_core5_marker',['S_core5_badge','S_core5_underline']),
 ('shape_d2_leader',['S_lead02','S_lead_dot2']),('shape_pin_harbor',['S_pin_harbor','S_pin_harbor_dot']),('shape_pin_pompeii',['S_pin_pompeii','S_pin_pompeii_dot']),
 ('shape_d3_section',['S_lead03','S_lead04','S_lead05','S_lead06','S_lead07','S_lead08','S_lead09','S_lead10','S_sect0','S_sect1','S_sect2','S_sect3','S_sect_ground'])]:
    for o in objs:
        print(aid,o,'n·cdir?', stats(aid,o, shrink=0.0 if ('lead' in o or 'ground' in o or 'underline' in o or 'pin' in o) else 0.8))
