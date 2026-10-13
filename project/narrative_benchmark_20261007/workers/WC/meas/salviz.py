import sys, json, numpy as np
sys.path.insert(0,'/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/WC/meas')
from sal import *
from PIL import Image
img=load(sys.argv[1]); A={a['id']:a for a in json.load(open(sys.argv[2]))['assets']}
a=A['detail_core3_lime_specimen']; x0,x1,y0,y1=a['bbox_visible_final_pt']; X0,Y0=x0-60,y0-60
rgb=img[int(round(Y0*2)):int(round((y1+60)*2)),int(round(X0*2)):int(round((x1+60)*2))]
lab=rgb2lab(rgb)
chans=[conspic(lab[...,i]/100) for i in range(3)]
S=sum(chans)/3
H,Wd=rgb.shape[:2]
def up8(m): 
    m=m/max(m.max(),1e-9); im=Image.fromarray((m*255).astype(np.uint8)).resize((Wd,H),Image.NEAREST); return np.asarray(im)
row=[(rgb*255).astype(np.uint8)]
for m in chans+[S]:
    g=up8(m); row.append(np.stack([g,g,g],-1))
out=np.concatenate(row,1)
Image.fromarray(out).resize((out.shape[1]//2,out.shape[0]//2)).save(sys.argv[3])
for nm,m in zip(['L','a','b','S'],chans+[S]):
    pk=peaks(m,k=4); print(nm,[(round(X0+(px+0.5)*rgb.shape[1]/m.shape[1]/2,1),round(Y0+(py+0.5)*rgb.shape[0]/m.shape[0]/2,1),round(float(v),3)) for py,px,v in pk])
