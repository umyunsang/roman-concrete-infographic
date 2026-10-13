import bpy, json, numpy as np
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
E=json.load(open('edges2.json'))
def top_of(x,y,rn):
    o=Vector((x,y,40))
    for _ in range(40):
        h,loc,nor,fi,ob,m=sc.ray_cast(dg,o,Vector((0,0,-1)))
        if not h: return None
        if ob.name==rn: return loc.z
        o=loc+Vector((0,0,-1e-4))
    return None
for rn in ['R_via_ostiensis','R_via_appia','R_core_road']:
    res=[]
    for r in E[rn]:
        if r['vis_pt'] is None or r['near']<0.3 or r['outside']!='T_land': continue
        # inward direction: from edge point toward... approximate using near-dir opposite
        q=np.array([r['qx'],r['qy']]); inward=-np.array([1,-1])/np.sqrt(2)
        zs=[top_of(*(q+inward*d),rn) for d in (0.12,0.18,0.24)]
        zs=[z for z in zs if z is not None]
        if not zs: continue
        pav=min(zs); curb=r['top']
        res.append((r['u'],r['v'],(curb-pav)*10,(pav-r['ofz'])*10,r['vis_pt']))
    a=np.array([x[2:] for x in res])
    print('CURB',rn,'n',len(res),'curb-above-paver p50 %.2f p90 %.2f'%(np.median(a[:,0]),np.percentile(a[:,0],90)),'paver-top above outside terrain p50 %.2f p90 %.2f max %.2f'%(np.median(a[:,1]),np.percentile(a[:,1],90),a[:,1].max()))
    big=[(round(x[0]),round(x[1]),round(x[3],2),round(x[2],2)) for x in res if x[3]>0.70+0.5]
    print('   paver-top>1.2pt:',len(big),sorted(big,key=lambda t:t[1])[:20])
