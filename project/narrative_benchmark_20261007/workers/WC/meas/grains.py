"""grain measure exactly as critic objform_b0/grains.py, parametrised by assets root."""
import json, sys, numpy as np
from PIL import Image
from skimage import measure, color
RL=sys.argv[1].rstrip('/')+'/'
A={a['id']:a for a in json.load(open(RL+'assets_index.json'))['assets']}
INV={o['name']:o for o in json.load(open(RL+'inventory.json'))['objects']}
S=3
def run(aid, names):
    a=A[aid]; im=np.asarray(Image.open(a['files']['isolated_rgba']).convert('RGBA')).astype(float)/255
    lab=color.rgb2lab(im[...,:3]); x0,y0=a['crop_pt'][0],a['crop_pt'][2]
    rows=[]
    for n in names:
        if n not in INV: continue
        b=INV[n]['bbox_visible_final_pt']
        if b is None: rows.append(dict(n=n,eqd_pt=0,circ=0)); continue
        X0,X1,Y0,Y1=[int(round((v-o)*S)) for v,o in zip(b,(x0,x0,y0,y0))]
        X0-=2;Y0-=2;X1+=3;Y1+=3
        sub=lab[Y0:Y1,X0:X1]; L=sub[...,0]
        m=(L>78)&(np.hypot(sub[...,1],sub[...,2])<20)
        lb=measure.label(m); ps=sorted(measure.regionprops(lb),key=lambda p:-p.area)
        if not ps: rows.append(dict(n=n,eqd_pt=0,circ=0)); continue
        p=ps[0]
        circ=4*np.pi*p.area/(p.perimeter_crofton**2) if p.perimeter_crofton>0 else 0
        cy,cx=p.centroid
        rows.append(dict(n=n,eqd_pt=round(p.equivalent_diameter_area/S,2),circ=round(circ,3),ecc=round(p.eccentricity,2),
                         c=(round(x0+(X0+cx)/S,1),round(y0+(Y0+cy)/S,1))))
    return rows
def summ(tag,rows):
    print(tag)
    for r in rows: print('  ',r)
    d=np.array([r['eqd_pt'] for r in rows]); c=np.array([r['circ'] for r in rows])
    if len(d): print('   eqd mean %.2f sd %.2f CV %.3f | circ median %.3f'%(d.mean(),d.std(ddof=0),d.std(ddof=0)/max(d.mean(),1e-9),np.median(c)))
groups=json.loads(sys.argv[2]) if len(sys.argv)>2 else None
if groups is None:
    summ('C03 all',run('detail_core3_lime_specimen',[f'NB_lime_clast_specimen_LIME{i:02d}' for i in range(12)]))
    summ('C05',run('support_core5_lab',[f'R1_healed_clast{i}' for i in range(3)]))
else:
    for tag,(aid,names) in groups.items(): summ(tag,run(aid,names))
