import numpy as np, json, warnings
warnings.filterwarnings('ignore')
from PIL import Image
from skimage import color, measure
from scipy import ndimage as ndi
Image.MAX_IMAGE_PIXELS=None
idx=json.load(open('../nb_work/review_loop/obj_r11/assets_index.json'))
A={a['id']:a for a in idx['assets']}
full=np.asarray(Image.open('../nb_work/review_loop/obj_r11/full/full_map_pass.png').convert('RGB')).astype(float)/255
FS=3.0
X0,Y0,X1,Y1=40,1355,115,1400
F=full[int(Y0*FS):int(Y1*FS), int(X0*FS):int(X1*FS)]
def isocrop(aid):
    a=A[aid]; cx0,cx1,cy0,cy1=a['crop_pt']
    im=Image.open(a['files']['isolated_rgba'])
    arr=np.asarray(im).astype(float)/255
    return arr[int(round((Y0-cy0)*3)):int(round((Y1-cy0)*3)), int(round((X0-cx0)*3)):int(round((X1-cx0)*3))]
T=isocrop('water_tiber'); S=isocrop('water_sea'); G=isocrop('ground_land')
h=min(F.shape[0],T.shape[0],S.shape[0],G.shape[0]); w=min(F.shape[1],T.shape[1],S.shape[1],G.shape[1])
F=F[:h,:w]; T=T[:h,:w]; S=S[:h,:w]; G=G[:h,:w]
Lf=color.rgb2lab(F)
water_ref=np.where(T[...,3:4]>0.5,T[...,:3],S[...,:3])
Lw=color.rgb2lab(water_ref)
waterpix=(T[...,3]>0.5)|(S[...,3]>0.5)
dL=Lf[...,0]-Lw[...,0]
dE=color.deltaE_ciede2000(Lf,Lw)
# pixels in water area where final is darker than iso water by >=5 and not land-coloured (b* of land >10)
cand=waterpix&(dL<=-5)&(Lf[...,2]<8)
cand=ndi.binary_opening(cand,iterations=0) if False else cand
lbl=measure.label(cand,connectivity=2)
regs=[p for p in measure.regionprops(lbl) if p.area>=3]
tot=sum(p.area for p in regs)/9
print("dark scribble px area %.1f pt2 in %d comps; dL median %.1f, min %.1f; dE median %.1f"%(tot,len(regs),np.median(dL[cand]),dL[cand].min(),np.median(dE[cand])))
ys,xs=np.nonzero(cand); print("extent x %.1f-%.1f y %.1f-%.1f"%(X0+xs.min()/3,X0+xs.max()/3,Y0+ys.min()/3,Y0+ys.max()/3))
# transitions along 3pt (9px) horizontal segments
maxtr=0
for r in range(h):
    row=cand[r]
    for c in range(0,w-9):
        seg=row[c:c+9]; tr=np.count_nonzero(np.diff(seg.astype(int)))
        maxtr=max(maxtr,tr)
print("max transitions in any 3pt horizontal segment:",maxtr)
# area of 'mixed' zone: dilate cand by 1.5pt and count windows with >=3 transitions
mix=np.zeros_like(cand)
for r in range(h):
    row=cand[r].astype(int)
    for c in range(0,w-9):
        if np.count_nonzero(np.diff(row[c:c+9]))>=3: mix[r,c:c+9]=True
print("mixed-zone area (>=3 transitions per 3pt) %.1f pt2"%(mix.sum()/9))
Image.fromarray((np.dstack([cand*255,cand*0,cand*0])+F*255*(~cand[...,None])).astype(np.uint8)).resize((w*4,h*4),Image.NEAREST).save('mouth_scribble_mask.png')
