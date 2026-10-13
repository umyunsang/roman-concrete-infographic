import sys, json; sys.path.insert(0,'/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/ocb4')
from clib import *
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
Image.MAX_IMAGE_PIXELS=None
RL='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
inv=json.load(open(RL+'obj_r11/inventory.json')); names=[o['name'] for o in inv['objects']]
TOK={}
for o in inv['objects']:
    for s_ in o['materials']: TOK[s_['material']]=s_['diffuse_hex']
def dec(p):
    a=np.array(Image.open(p)).astype(int); k=np.rint((a[...,:3]-2)/4).astype(int); c=k[...,0]+64*k[...,1]+4096*k[...,2]; c[a[...,3]<128]=0; return c
M=dec(RL+'obj_r11/idpass/id_id_map.png'); O=dec(RL+'obj_r11/idpass/id_id_overlay.png'); F=np.where(O>0,O,M)
IMG=np.array(Image.open(RL+'r11/map_only_2x.png').convert('RGB')).astype(float)
h=min(F.shape[0],IMG.shape[0]); w=min(F.shape[1],IMG.shape[1]); F=F[:h,:w]; IMG=IMG[:h,:w]
mid=np.array(Image.open('matid_full.png').resize((w,h),Image.Resampling.NEAREST)).astype(int)
ids=json.load(open('matid_map.json'))['ids']
LBL=np.full((h,w),-1)
for i,(n,c) in enumerate(ids.items()):
    LBL[(mid[...,3]>127)&(np.abs(mid[...,:3]-np.array(c)).max(-1)<=2)]=i
TL=names.index('T_land')+1
assets={a['id']:a for a in json.load(open(RL+'obj_r11/assets_index.json'))['assets']}
s=w/1191
for aid in sys.argv[1:]:
    x0,x1,y0,y1=assets[aid]['bbox_visible_final_pt']
    X0,X1,Y0,Y1=int(x0*s),int(x1*s)+1,int(y0*s),int(y1*s)+1
    lb=LBL[Y0:Y1,X0:X1]; fc=F[Y0:Y1,X0:X1]; img=IMG[Y0:Y1,X0:X1]; LAB=lab(img)
    tot=[]
    for i,(n,c) in enumerate(ids.items()):
        pm=lb==i
        if pm.sum()<16: continue
        core=ndi.binary_erosion(pm,iterations=2)   # 1pt band at 2x
        sel=core&(fc==TL)
        if sel.sum()==0: continue
        rl=lab(ramp(TOK[n]))
        d=np.full(pm.shape,np.nan)
        d[sel]=np.min(np.stack([de00(LAB[sel],rl[k]) for k in range(len(rl))],-1),-1)
        far=sel&(d>8)
        lab_,nb=ndi.label(far); sz=ndi.sum(far,lab_,range(1,nb+1)) if nb else np.array([])
        big=[(int(sz[k]),round((np.where(lab_==k+1)[1].mean()+X0)/s,1),round((np.where(lab_==k+1)[0].mean()+Y0)/s,1)) for k in range(nb) if sz[k]>=4]
        print(f'{aid} {n.split(".")[-1]:22s} T_land-in-part px {sel.sum():5d}  dE00 to ramp p50 {np.nanmedian(d[sel]):.1f} max {np.nanmax(d[sel]):.1f}  >8 px {far.sum()}  blobs>=1pt2 {big[:6]}')
        tot+=big
    print(aid,'TOTAL foreign blobs >=1pt2:',len(tot))
