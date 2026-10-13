import json, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/oc_b5_r11')
from clr import *
B = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/assets/'
meta = json.load(open('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/oc_b5_r11/meta.json'))
S=2.9992
ACC=h2r('#983821'); TOK=h2r('#B44327')
tl=s2l(TOK)
rows=[]
for k in range(1,6):
    aid=f'shape_core{k}_marker'; m=meta[aid]; cx0,cx1,cy0,cy1=m['crop_pt']
    ctx=np.array(Image.open(B+aid+'/context.png').convert('RGB')).astype(float)
    a=np.array(Image.open(B+aid+'/isolated_rgba.png'))[...,3]
    def bm(b,pad=1.0):
        x0,x1,y0,y1=b; z=np.zeros(a.shape,bool)
        z[max(int((y0-pad-cy0)*S),0):int((y1+pad-cy0)*S)+1, max(int((x0-pad-cx0)*S),0):int((x1+pad-cx0)*S)+1]=True; return z
    um=(a>127)&bm(m['objs'][f'S_core{k}_underline']['bbox'])
    bmk=(a>127)&bm(m['objs'][f'S_core{k}_badge']['bbox'])
    Lu=lab(ctx[um])[:,0]
    d30=ctx[um][Lu<=np.percentile(Lu,30)].mean(0)
    core=ctx[um&(a>=254)]; cmed=np.median(core,0)
    b1=ndi.binary_erosion(bmk,iterations=1); bmed=np.median(ctx[b1],0)
    # ring
    d_out=ndi.distance_transform_edt(~um); ring=(d_out>=2*S)&(d_out<=8*S)&~bm(m['objs'][f'S_core{k}_badge']['bbox'],pad=8)
    bg=np.median(ctx[ring],0)
    r=dict(aid=aid, ul_dark30=hx(d30), ul_dark30_dE_acc=round(float(de00(lab(d30),lab(ACC))),2), ul_core_med=hx(cmed),
           ul_core_dE_acc=round(float(de00(lab(cmed),lab(ACC))),2), ul_core_L=round(float(lab(cmed)[0]),1),
           badge_med=hx(bmed), badge_dE_acc=round(float(de00(lab(bmed),lab(ACC))),2), badge_L=round(float(lab(bmed)[0]),1),
           ul_vs_badge_dE=round(float(de00(lab(d30),lab(bmed))),2),
           wcag_ul=round(wcag(d30,bg),2), D05=round(szafD(d30,bg,0.5),2), D05_p=round(szafD(cvd(d30,'protan'),cvd(bg,'protan'),0.5),2),
           D05_d=round(szafD(cvd(d30,'deutan'),cvd(bg,'deutan'),0.5),2), D05_t=round(szafD(cvd(d30,'tritan'),cvd(bg,'tritan'),0.5),2),
           D025_ul_vs_acc=round(szafD(d30,ACC,0.25),2))
    # k factors (linear) relative to token
    r['k_ul']=[round(float(x),3) for x in s2l(cmed)/tl]; r['k_badge']=[round(float(x),3) for x in s2l(bmed)/tl]
    rows.append(r); print(json.dumps(r))
ku=np.mean([np.mean(r['k_ul']) for r in rows]); kb=np.mean([np.mean(r['k_badge']) for r in rows])
print('mean k_ul',round(ku,3),'mean k_badge',round(kb,3))
# fix: underline-only material so that underline renders = #983821 : diffuse_lin = acc_lin / k_ul (per channel mean k)
kul_ch=np.mean([r['k_ul'] for r in rows],0); kb_ch=np.mean([r['k_badge'] for r in rows],0)
new_lin=s2l(ACC)/kul_ch
print('k_ul per ch',kul_ch.round(3),'k_badge per ch',kb_ch.round(3))
print('underline-only diffuse to render #983821:', hx(l2s(new_lin)), 'lin', new_lin.round(4), 'scale vs token', (new_lin/tl).round(3))
pred=l2s(new_lin*kul_ch); print('pred render', hx(pred), 'dE vs acc', round(float(de00(lab(pred),lab(ACC))),2))
# alt: match badge median
new2=s2l(np.mean([h2r(r['badge_med']) for r in rows],0))/kul_ch
print('underline diffuse to match badge median:', hx(l2s(new2)))
