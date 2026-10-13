import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx={a['id']:a for a in json.load(open(R+'assets_index.json'))['assets']}
def full_mask(aid):
    a=idx[aid]; x0,x1,y0,y1=a['crop_pt']
    al=np.array(Image.open(a['files']['isolated_rgba']))[...,3]>=128
    M=np.zeros((1684*3,1191*3),bool)
    u0=int(round(x0*3)); v0=int(round(y0*3))
    h,w=al.shape
    M[v0:v0+h,u0:u0+w]=al[:min(h,5052-v0),:min(w,3573-u0)]
    return M
G=full_mask('ground_land'); S=full_mask('water_sea'); T=full_mask('water_tiber')
np.save('G3.npy',G); np.save('S3.npy',S); np.save('T3.npy',T)
for rid in ['road_ostiensis','road_appia','road_core_se','road_core_se_2']:
    M=full_mask(rid); np.save(rid+'_3.npy',M)
    off=M&~G
    lab,n=ndi.label(off); sz=ndi.sum(off,lab,range(1,n+1))/9 if n else []
    print(rid,'M=%.0f'%(M.sum()/9),'off-terrain=%.1f pt2 (%.2f%%)'%(off.sum()/9,100*off.sum()/M.sum()))
    if off.sum():
        yy,xx=np.nonzero(off); print('  off bbox x %.1f-%.1f y %.1f-%.1f'%(xx.min()/3,xx.max()/3,yy.min()/3,yy.max()/3), 'onSea=%.1f'%((M&S&~G).sum()/9))
