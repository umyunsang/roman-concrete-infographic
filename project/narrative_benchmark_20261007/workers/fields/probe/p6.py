import bpy, bmesh, numpy as np, collections
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; cam=sc.camera; O=bpy.data.objects
def pt(p):
    v=world_to_camera_view(sc,cam,Vector(p)); return (round(v.x*1191),round((1-v.y)*1684))
o=O['F_centuriatio']; me=o.data
bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
seen=set(); isl=[]
for f in bm.faces:
    if f.index in seen: continue
    st=[f]; seen.add(f.index); fs=[]
    while st:
        a=st.pop(); fs.append(a)
        for e in a.edges:
            for g in e.link_faces:
                if g.index not in seen: seen.add(g.index); st.append(g)
    isl.append(fs)
plates=[];stakes=[];bales=[]
for fs in isl:
    es=set(e for f in fs for e in f.edges); bnd=sum(1 for e in es if len(e.link_faces)==1)
    P=np.array([v.co[:] for f in fs for v in f.verts])
    if len(fs)==12 and bnd==6: stakes.append(P.mean(0)); continue
    if len(fs)==18 and bnd==12: bales.append(P.mean(0)); continue
    vs=list({v.index:v for f in fs for v in f.verts}.values()); P=np.array([v.co[:] for v in vs])
    A=np.c_[P[:,0],P[:,1],np.ones(len(P))]; cf,*_=np.linalg.lstsq(A,P[:,2],rcond=None); r=P[:,2]-A@cf
    # cross-ridge axis: axis with more distinct coordinate rows
    nx=len(np.unique(np.round(P[:,0],2))); ny=len(np.unique(np.round(P[:,1],2)))
    ax=0 if nx>ny else 1
    keys=np.round(P[:,ax],2); rows=sorted(set(keys)); rr=np.array([r[keys==k].mean() for k in rows])
    inner=rr[1:-1]
    alt=np.abs(inner[1:-1]-(inner[:-2]+inner[2:])/2).mean() if len(inner)>=3 else 0
    plates.append(dict(n=len(fs),c=P.mean(0),mn=P.min(0),mx=P.max(0),ax=ax,nrows=len(rows),alt=alt,rim=rr[0]-inner.mean() if len(inner) else 0,pt=pt(P.mean(0)),spacing=np.diff(rows).mean()))
stakes=np.array(stakes); bales=np.array(bales)
print('plates',len(plates),'stakes',len(stakes),'bales',len(bales))
alts=np.array([p['alt'] for p in plates]); print('alt hist',np.histogram(alts,bins=[0,0.01,0.02,0.03,0.04,0.05,0.06,0.08,0.1,0.2])) 
sp=np.array([p['spacing'] for p in plates]); print('row spacing hist',np.histogram(sp,bins=[0,0.25,0.3,0.32,0.4,0.6,0.7,1,2]))
for p in plates:
    inside=lambda Q: ((Q[:,0]>=p['mn'][0]-0.05)&(Q[:,0]<=p['mx'][0]+0.05)&(Q[:,1]>=p['mn'][1]-0.05)&(Q[:,1]<=p['mx'][1]+0.05)).sum() if len(Q) else 0
    p['ns']=inside(stakes); p['nb']=inside(bales)
cat=collections.Counter()
for p in plates:
    k=('ridged' if p['alt']>0.03 else 'flat', 'stakes' if p['ns'] else '', 'bales' if p['nb'] else '')
    cat[k]+=1
print(cat)
print('stakes on plates',sum(p['ns'] for p in plates),'bales on plates',sum(p['nb'] for p in plates))
for p in plates:
    if p['alt']<=0.03: print('flat',p['n'],p['pt'],'rows',p['nrows'],'spacing',round(p['spacing'],2),'alt',round(p['alt'],3),'rim',round(p['rim'],3),'stakes',p['ns'],'bales',p['nb'])
# gaps between plates
C=np.array([p['c'][:2] for p in plates]); 
from itertools import combinations
def gap(a,b):
    dx=max(a['mn'][0]-b['mx'][0], b['mn'][0]-a['mx'][0],0); dy=max(a['mn'][1]-b['mx'][1], b['mn'][1]-a['mx'][1],0); return np.hypot(dx,dy)
G=[min(gap(a,b) for j,b in enumerate(plates) if j!=i) for i,a in enumerate(plates)]
print('nearest gap hist',np.histogram(G,bins=[0,0.1,0.3,0.5,1,2,4,8,100]))
# stakes not on plates
def on_any(q):
    return any(p['mn'][0]-0.05<=q[0]<=p['mx'][0]+0.05 and p['mn'][1]-0.05<=q[1]<=p['mx'][1]+0.05 for p in plates)
print('stakes off-plate',sum(not on_any(q) for q in stakes),'bales off-plate',sum(not on_any(q) for q in bales))
