import sys, numpy as np
sys.path.insert(0,'.')
from common import *
from PIL import Image, ImageCms
from scipy import ndimage as ndi
icc='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/PSOcoated_v3.icc'
srgb=ImageCms.createProfile('sRGB'); cmyk=ImageCms.getOpenProfile(icc)
t1=ImageCms.buildTransform(srgb,cmyk,'RGB','CMYK',renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC,flags=ImageCms.Flags.BLACKPOINTCOMPENSATION)
t2=ImageCms.buildTransform(cmyk,srgb,'CMYK','RGB',renderingIntent=ImageCms.Intent.ABSOLUTE_COLORIMETRIC)
im=Image.open('hg_full_ctx.png').convert('RGB')
pim=ImageCms.applyTransform(ImageCms.applyTransform(im,t1),t2)
s=2.9991603694374476; X0,Y0=300,0
al=np.load('hg_full_ovl_alpha.npy'); M=al>=128
for nm,I in [('screen',im),('print',pim)]:
    L=rgb2L(np.array(I).astype(float))
    def box(a,b,c,d):
        return float(np.median(L[int((c-Y0)*s):int((d-Y0)*s),int((a-X0)*s):int((b-X0)*s)]))
    top_bev=box(560,640,112.3,112.9); cor_front=box(560,640,114.5,116.5)
    lbev=box(372,389,0,0) if False else None
    pil_lbev=box(378.7,379.4,180,220); pil_front=box(383,388,180,220); pil_rbev=box(392.0,392.8,180,220)
    body=box(400,790,40,100)
    # cornice host ring: body 1-3pt above/below
    host=np.median(np.r_[L[int(109*s):int(111*s),int((560-X0)*s):int((640-X0)*s)].ravel(),L[int(119.5*s):int(121.5*s),int((560-X0)*s):int((640-X0)*s)].ravel()])
    cor=box(560,640,112.5,117.8)
    # arch opening vs rim (central arch): opening interior 2-8pt inside hole, rim 1-3pt in gate
    holes=ndi.binary_fill_holes(M)&~M
    dh=ndi.distance_transform_edt(holes)/s; dm=ndi.distance_transform_edt(~holes)/s
    op=float(np.median(L[holes&(dh>=1)&(dh<=3)])); rim=float(np.median(L[M&(dm>=1)&(dm<=3)]))
    paper=float(np.median(L[(~M)&~holes][::50]))
    print(nm,f'top_bevel={top_bev:.1f} cornice_front={cor_front:.1f} step={top_bev-cor_front:.1f} | pil_lbev={pil_lbev:.1f} pil_front={pil_front:.1f} pil_rbev={pil_rbev:.1f} steps={pil_lbev-pil_front:.1f},{pil_rbev-pil_front:.1f} | body={body:.1f} pil-body={pil_front-body:.1f} | cornice={cor:.1f} host={host:.1f} d={cor-host:.1f} | opening={op:.1f} rim={rim:.1f} d={op-rim:.1f} | paper~{paper:.1f}')
