import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
ids=json.load(open('ids.json')); names=ids['names']
final=np.load('final_obj.npy'); mapo=np.load('map_obj.npy'); ovl=np.load('ovl_obj.npy')
H,W=final.shape; S=W/1191.0
def cat_of(n):
    if n=='T_land': return 'ground'
    if n in ('L02_tiber','L10_sea','W_water_marks'): return 'water'
    if n.startswith('R_') or n.startswith('R1_road') or n=='R4_bridge_west_bed': return 'road'
    if n.startswith('B_pons'): return 'bridge'
    if n=='F_centuriatio': return 'fields'
    if n.startswith('T_pine') or n=='T_cypress': return 'tree'
    if n.startswith('S_'): return 'shape2d'
    return 'obj'
cats=['none']+[cat_of(n) for n in names]
cat_arr=np.array(cats)
OBJ_ASSET={}
inv=json.load(open(R+'obj_r11/inventory.json'))
for a in inv['assets']:
    for nm in a.get('objects',[]): OBJ_ASSET.setdefault(nm,a['id'])
def objmask(namelist, src=None):
    src=final if src is None else src
    codes=[names.index(n)+1 for n in namelist]
    return np.isin(src,codes)
def catmask(c, src=None):
    src=final if src is None else src
    codes=[i+1 for i,n in enumerate(names) if cat_of(n)==c]
    return np.isin(src,codes)
Mz=np.load('M_all.npz')
def M(aid): return Mz[aid]
ASSET_OBJS={a['id']:a.get('objects',[]) for a in inv['assets']}
def V(aid): return objmask(ASSET_OBJS[aid])
def mindist(a,b):
    if not a.any() or not b.any(): return None
    dt=ndi.distance_transform_edt(~b)
    return float(dt[a].min())/S
def signed_gap(a,b):
    ov=a&b
    if ov.any():
        dt=ndi.distance_transform_edt(ov)
        return -float(dt.max())*2/S
    return mindist(a,b)
def bbox(m):
    ys,xs=np.where(m)
    return [xs.min()/S,(xs.max()+1)/S,ys.min()/S,(ys.max()+1)/S] if len(xs) else None
