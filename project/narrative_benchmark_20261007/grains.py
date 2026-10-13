import json, numpy as np
from PIL import Image
from skimage import measure, color
RL='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
A={a['id']:a for a in json.load(open(RL+'assets_index.json'))['assets']}
INV={o['name']:o for o in json.load(open(RL+'inventory.json'))['objects']}
S=3
def run(aid, names, extra=None):
    a=A[aid]; im=np.asarray(Image.open(a['files']['isolated_rgba']).convert('RGBA')).astype(float)/255
    ctx=np.asarray(Image.open(a['files']['context']).convert('RGB')).astype(float)/255
    lab=color.rgb2lab(im[...,:3]); x0,y0=a['crop_pt'][0],a['crop_pt'][2]
    rows=[]
    for n in names:
        b=INV[n]['bbox_visible_final_pt'] if n in INV else n
        X0,X1,Y0,Y1=[int(round((v-o)*S)) for v,o in zip(b,(x0,x0,y0,y0))]
        X0-=2;Y0-=2;X1+=3;Y1+=3
        sub=lab[Y0:Y1,X0:X1]; L=sub[...,0]
        m=(L>78)&(np.hypot(sub[...,1],sub[...,2])<20)
        lb=measure.label(m); ps=sorted(measure.regionprops(lb),key=lambda p:-p.area)
        if not ps: rows.append((n,None)); continue
        p=ps[0]
        circ=4*np.pi*p.area/(p.perimeter_crofton**2) if p.perimeter_crofton>0 else 0
        rows.append(dict(n=n,eqd_pt=round(p.equivalent_diameter_area/S,2),circ=round(circ,3),ecc=round(p.eccentricity,2),solidity=round(p.solidity,3),Lmax=round(L.max(),1)))
    return rows
out={}
out['C03']=run('detail_core3_lime_specimen',[f'NB_lime_clast_specimen_LIME{i:02d}' for i in range(6)])
out['D01']=run('detail_d2_making',[f'D2_lime{i:02d}' for i in range(16)])
out['B04']=run('basic_recipe',[f'H_mold_lime{i}' for i in range(5)])
out['C05']=run('support_core5_lab',[f'R1_healed_clast{i}' for i in range(3)])
for k,v in out.items():
    print(k)
    for r in v: print('  ',r)
    d=np.array([r['eqd_pt'] for r in v]); c=np.array([r['circ'] for r in v])
    print('   eqd mean %.2f sd %.2f CV %.3f | circ median %.3f'%(d.mean(),d.std(ddof=0),d.std(ddof=0)/d.mean(),np.median(c)))
json.dump(out,open('grains.json','w'),indent=1)
