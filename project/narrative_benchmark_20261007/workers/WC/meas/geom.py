"""visible-mask distances from the inventory ID passes (1px = 0.5pt approx at 48%)."""
import json, sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
root=sys.argv[1].rstrip('/')+'/'
inv=json.load(open(root+'inventory.json')); NAMES=[o['name'] for o in inv['objects']]
def ids(kind):
    im=np.array(Image.open(root+'idpass/id_id_%s.png'%kind)).astype(int)
    k=((im[...,0]-2)//4)+64*((im[...,1]-2)//4)+4096*((im[...,2]-2)//4); k[im[...,3]==0]=0; return k
m,o=ids('map'),ids('overlay'); vis=np.where(o>0,o,m)
s=m.shape[1]/1191.0
def mask(names, src=vis):
    return np.isin(src,[NAMES.index(n)+1 for n in names if n in NAMES])
def box_dist(M, box):
    x0,x1,y0,y1=box; ys,xs=np.nonzero(M); X=xs/s; Y=ys/s
    dx=np.maximum(0,np.maximum(x0-X,X-x1)); dy=np.maximum(0,np.maximum(y0-Y,Y-y1)); d=np.hypot(dx,dy); i=d.argmin()
    return d[i],(X[i],Y[i])
def bbox(M):
    ys,xs=np.nonzero(M); return xs.min()/s,(xs.max()+1)/s,ys.min()/s,(ys.max()+1)/s
c4=[n for n in NAMES if n.startswith('NB_core4_sequence_') or n.startswith('R8_') and n!='R8_pantheon']
M4=mask(c4); print('C4 visible bbox pt', np.round(bbox(M4),1))
print('C4 d_own to ink box 639-802x1031.5-1128.5: %.1f at %s'%box_dist(M4,(639,802,1031.5,1128.5)))
col=mask(['R3_colosseum_podium','COL_ruined']); print('colosseum to ink box: %.1f'%box_dist(col,(639,802,1031.5,1128.5))[0])
dr=mask(['NB_core4_sequence_GRAY04']); print('drops bbox', np.round(bbox(dr),1))
cr=mask(['R8_crack_step1','R8_water_step1']); ys,xs=np.nonzero(cr); top=ys.min(); print('crack/water entrance top y %.1f x %.1f'%(top/s, xs[ys==top].mean()/s))
M1=mask(['NB_modern_building','R1_frame_rust','R3_frame_crack_col','R3_frame_crack_col2'])
print('C1 bbox', np.round(bbox(M1),1), 'area pt2 %.0f'%(M1.sum()/s/s))
print('C1 d_own to ink box 528.5-678.5x385.5-482.5: %.1f at %s'%box_dist(M1,(528.5,678.5,385.5,482.5)))
pan=mask(['R8_pantheon']); 
if pan.any(): print('pantheon to C1 ink: %.1f'%box_dist(pan,(528.5,678.5,385.5,482.5))[0])
mt=mask([n for n in NAMES if n.startswith('L01_')])
dt=ndi.distance_transform_edt(~mt)/s; print('C1 min gap to Apennines (ID pass, pt): %.2f'%dt[M1].min())
for nm in ['MS1_core1_to_2','F_centuriatio','R_core_road','R8_pantheon']:
    mm=mask([n for n in NAMES if n.startswith(nm)])
    if mm.any(): d=ndi.distance_transform_edt(~mm)/s; print('C1 min gap to %s: %.2f'%(nm,d[M1].min()))
# overlap with other objects: count C1 occluded? (pixels where C1 should be but other object visible) skipped
M5=mask(['R1_specimen_healed','R1_specimen_leaking','R1_lab_bench']); print('C5 bbox', np.round(bbox(M5),1))
