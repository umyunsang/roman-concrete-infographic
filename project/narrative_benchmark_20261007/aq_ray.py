import bpy, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; cam=sc.camera
ob=bpy.data.objects['L05_aqua_claudia']
dg=bpy.context.evaluated_depsgraph_get()
bvh=BVHTree.FromObject(ob,dg)  # object space
mw=ob.matrix_world; mi=mw.inverted()
me=ob.evaluated_get(dg).to_mesh()
P=np.array([tuple(mw@v.co) for v in me.vertices])
c=P[:,:2].mean(0); xy=P[:,:2]-c
u,s,vt=np.linalg.svd(xy,full_matrices=False); ax=vt[0]; pp=vt[1]
t=xy@ax; nn=xy@pp
z0,z1=P[:,2].min(),P[:,2].max()
for zf in (0.25,0.45):
    z=z0+zf*(z1-z0)
    hits=[]
    ts=np.arange(t.min(),t.max(),0.01)
    for tv in ts:
        # local centerline offset: median n of verts near tv
        sel=np.abs(t-tv)<1.0
        nc=np.median(nn[sel]) if sel.any() else 0
        o=Vector((*(c+ax*tv+pp*(nc-20)),z)); d=Vector((pp[0],pp[1],0))
        lo=mi@o; ld=(mi.to_3x3()@d).normalized()
        loc,nor,idx,dist=bvh.ray_cast(lo,ld,40)
        hits.append(loc is not None)
    hits=np.array(hits)
    runs=[];i=0
    while i<len(hits):
        j=i
        while j<len(hits) and hits[j]==hits[i]: j+=1
        runs.append((bool(hits[i]),(j-i)*0.01)); i=j
    piers=[l for h,l in runs if h]; gaps=[l for h,l in runs if not h]
    print('z frac',zf,'n piers',len(piers),'pier width med',np.median(piers),'gap med',np.median([g for g in gaps if g<5]) if gaps else None,'gaps',sorted([round(g,2) for g in gaps])[:8], '...', sorted([round(g,2) for g in gaps])[-6:])
# thickness across axis at a pier: cast along pp through a pier center at z=0.45
z=z0+0.45*(z1-z0)
th=[]
for tv in np.linspace(t.min()+1,t.max()-1,200):
    sel=np.abs(t-tv)<1.0
    nc=np.median(nn[sel]) if sel.any() else 0
    o=Vector((*(c+ax*tv+pp*(nc-20)),z)); d=Vector((pp[0],pp[1],0))
    lo=mi@o; ld=(mi.to_3x3()@d).normalized()
    loc,nor,idx,dist=bvh.ray_cast(lo,ld,40)
    if loc is None: continue
    o2=Vector((*(c+ax*tv+pp*(nc+20)),z)); lo2=mi@o2
    loc2,_,_,dist2=bvh.ray_cast(lo2,-ld,40)
    if loc2 is not None: th.append(40-dist-dist2)
print('pier depth across axis median',np.median(th))
vd=cam.matrix_world.to_3x3()@Vector((0,0,-1))
ang=math.degrees(math.acos(abs(vd.x*ax[0]+vd.y*ax[1])/math.hypot(vd.x,vd.y)))
print('angle view vs axis (deg)',ang)
W,H=1191,1684
def topt(v):
    q=world_to_camera_view(sc,cam,v); return np.array([q.x*W,(1-q.y)*H])
cc=Vector((*c,z0))
print('pt per m along axis',np.linalg.norm(topt(cc+Vector((ax[0],ax[1],0)))-topt(cc)),'pt per m across',np.linalg.norm(topt(cc+Vector((pp[0],pp[1],0)))-topt(cc)),'pt per m up',np.linalg.norm(topt(cc+Vector((0,0,1)))-topt(cc)))
print('axis',ax,'pp',pp)
