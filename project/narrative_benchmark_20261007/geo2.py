import bpy, runpy, json, sys, numpy as np, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
inv=runpy.run_path('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/inventory/inventory.py', run_name='inv_mod')
to_pt_np=inv['to_pt_np']; eval_mesh_arrays=inv['eval_mesh_arrays']
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
VS=10.0
def hits_down(x,y,z0=40.0,maxn=40):
    out=[]; o=Vector((x,y,z0))
    for _ in range(maxn):
        h,loc,nor,fi,ob,m=sc.ray_cast(dg,o,Vector((0,0,-1)))
        if not h: break
        out.append((ob.name,loc.z,nor.z)); o=loc+Vector((0,0,-1e-4))
    return out
def bvh_of(name):
    ob=bpy.data.objects[name]; ev=ob.evaluated_get(dg); me=ev.to_mesh(); mw=ob.matrix_world
    V=[mw@v.co for v in me.vertices]; F=[list(p.vertices) for p in me.polygons]; ev.to_mesh_clear()
    return BVHTree.FromPolygons(V,F), np.array([tuple(v) for v in V])
def hull2d(pts):
    pts=sorted(set(map(tuple,np.round(pts,6))))
    if len(pts)<3: return np.array(pts)
    def cross(o,a,b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lo=[];up=[]
    for p in pts:
        while len(lo)>=2 and cross(lo[-2],lo[-1],p)<=0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up)>=2 and cross(up[-2],up[-1],p)<=0: up.pop()
        up.append(p)
    return np.array(lo[:-1]+up[:-1])
def inpoly(pt,poly):
    if len(poly)<3: return False
    s=None
    for i in range(len(poly)):
        a=poly[i]; b=poly[(i+1)%len(poly)]
        c=(b[0]-a[0])*(pt[1]-a[1])-(b[1]-a[1])*(pt[0]-a[0])
        if s is None: s=c>=0
        elif (c>=0)!=s: return False
    return True
mode=sys.argv[sys.argv.index('--')+1]; outp=sys.argv[sys.argv.index('--')+2]
OUT={}
if mode=='trees':
    trees="T_cypress,T_pine.004,T_pine.022,T_pine.001,T_pine.002,T_pine.003,T_pine.011,T_pine.013,T_pine.017,T_pine.018,T_pine.019,T_pine,T_pine.007,T_pine.008,T_pine.009,T_pine.010,T_pine.014,T_pine.015,T_pine.016,T_pine.020,T_pine.021".split(',')
    fb,_=bvh_of('F_centuriatio'); lb,_=bvh_of('T_land'); rb,_=bvh_of('R_core_road')
    for tn in trees:
        ob=bpy.data.objects[tn]
        P,mi,edges,nf,tris=eval_mesh_arrays(ob,dg)
        mats=[s.material.name if s.material else '' for s in ob.material_slots]
        me=ob.evaluated_get(dg).to_mesh(); tv=set()
        for poly in me.polygons:
            if 'trunk' in mats[poly.material_index]: tv.update(poly.vertices)
        ob.evaluated_get(dg).to_mesh_clear()
        tv=np.array(sorted(tv))
        r={}
        zmin=P[:,2].min()
        if len(tv):
            T=P[tv]; zt0=T[:,2].min(); zt1=T[:,2].max()
            bot=T[T[:,2]<=zt0+0.02].mean(0); top=T[T[:,2]>=zt1-0.02].mean(0)
            ax=top-bot; r['trunk_tilt_ring_deg']=math.degrees(math.acos(ax[2]/np.linalg.norm(ax)))
            sp=to_pt_np([bot,top]); d=sp[1]-sp[0]; r['trunk_screen_angle_deg']=math.degrees(math.atan2(d[0],-d[1])); r['trunk_screen_len_pt']=float(np.linalg.norm(d))
            base_xy=bot[:2]
        else:
            base_xy=P[P[:,2]<=zmin+0.05][:,:2].mean(0)
            r['trunk']='none'
        # contact hull & COM
        dz=0.05
        S=P[P[:,2]<=zmin+dz]
        if len(S)<8: S=P[np.argsort(P[:,2])[:8]]
        cont=[]
        for p in S:
            hs=[h for h in hits_down(p[0],p[1],p[2]+1e-4) if h[0]!=tn]
            g=(p[2]-hs[0][1])*VS if hs else None
            # buried if terrain above p
            hu=sc.ray_cast(dg,Vector((p[0],p[1],p[2]+1e-4)),Vector((0,0,1)))
            buried = hu[0] and hu[4].name!=tn
            if (g is not None and g<=0.41) or buried: cont.append(p[:2])
        com=P.mean(0)
        hull=hull2d(np.array(cont)) if len(cont)>=3 else np.array(cont)
        r['n_contact']=len(cont); r['com_in_hull']=bool(inpoly(com[:2],hull)) if len(hull)>=3 else False
        if len(hull)>=3:
            # distance of COM to hull (world) -> pt approx via projection
            r['com_offset_world']=float(np.linalg.norm(com[:2]-np.mean(hull,0)))
        # stack at base
        hs=hits_down(base_xy[0],base_xy[1])
        r['stack_at_base']=[(n,round(z,3)) for n,z,nz in hs[:6]]
        r['zmin']=float(zmin)
        # field under any trunk-base point? check ring of base points
        onfield=[]
        if len(tv):
            T=P[tv]; ring=T[T[:,2]<=T[:,2].min()+0.02]
            for p in ring:
                hs2=[h for h in hits_down(p[0],p[1]) if h[0]!=tn]
                onfield.append(hs2[0][0] if hs2 else None)
        r['first_hit_above_trunk_ring']=onfield
        # BVH overlap tree vs field/road
        tb,_=bvh_of(tn)
        r['overlap_field']=len(tb.overlap(fb)); r['overlap_road']=len(tb.overlap(rb))
        OUT[tn]=r; print('TREE',tn,json.dumps(r))
elif mode=='roads':
    roads={'R_via_ostiensis':None,'R_roadgeo_ostiensis_junction_fill':None,'R_via_appia':None,'R_core_road':[[840.9,964.9,864.4,982.4],[588.2,816.8,963.9,1026.4]],'R1_road5_bed':None,'R1_road_landing5':None}
    roadset=set(n for n in bpy.data.objects.keys() if n.startswith('R_') or n.startswith('R1_road') or n=='R4_bridge_west_bed')
    for rn,regs in roads.items():
        ob=bpy.data.objects[rn]; ev=ob.evaluated_get(dg); me=ev.to_mesh(); mw=ob.matrix_world
        C=[];A=[]
        for p in me.polygons:
            n=(mw.to_3x3()@p.normal)
            if n.z>0.7: C.append(tuple(mw@p.center)); A.append(p.area)
        ev.to_mesh_clear()
        C=np.array(C); A=np.array(A)
        uv=to_pt_np(C)
        if regs:
            keep=np.zeros(len(C),bool)
            for ri,b in enumerate(regs):
                keep|=(uv[:,0]>=b[0])&(uv[:,0]<=b[1])&(uv[:,1]>=b[2])&(uv[:,1]<=b[3])
        else: keep=np.ones(len(C),bool)
        rows=[]
        step=max(1,int(keep.sum()//1500))
        for i in np.where(keep)[0][::step]:
            x,y,z=C[i]
            hs=hits_down(x,y)
            # first hit
            first=hs[0][0] if hs else None
            # road layers then support
            zr_bot=None; sup=None; zs=None; covered=None
            seen_road=False
            for n,zz,nz in hs:
                if n in roadset: seen_road=True; zr_bot=zz; continue
                if n.startswith('W_water'): continue
                if not seen_road:
                    covered=(n,zz); continue
                sup=n; zs=zz; break
            rows.append(dict(i=int(i),u=float(uv[i,0]),v=float(uv[i,1]),area=float(A[i]),top=float(z),first=first,covered=covered,bot=zr_bot,sup=sup,zs=zs))
        OUT[rn]=rows
        sups={}
        for r in rows: sups[r['sup']]=sups.get(r['sup'],0)+r['area']
        tot=sum(sups.values())
        gaps=[(r['bot']-r['zs'])*VS for r in rows if r['bot'] is not None and r['zs'] is not None]
        cov=[r for r in rows if r['covered'] and not r['covered'][0].startswith('MS') ]
        print('ROAD',rn,'n',len(rows),'support area frac',{k:round(v/tot,4) for k,v in sups.items()}, 'gap pt min/max', (round(min(gaps),2),round(max(gaps),2)) if gaps else None, 'covered_by', {c['covered'][0] for c in rows if c['covered']})
elif mode=='overlap':
    pairs=[('R_via_ostiensis',x) for x in ['L09_portus_lighthouse','L09_portus_mole','L12_harbor_pilae','B_pons2','T_land','L10_sea','L02_tiber','R_core_road','F_centuriatio','T_pine.011']]+\
          [('R_via_appia',x) for x in ['MS3_core34_to_5','R3_colosseum_podium','R_core_road','F_centuriatio','T_land']]+\
          [('R_core_road',x) for x in ['MS3_core34_to_5','R3_colosseum_podium','COL_ruined','F_centuriatio','T_cypress']]+\
          [('R1_road5_bed',x) for x in ['MS3_core34_to_5','F_centuriatio','T_land']]+[('R1_road_landing5',x) for x in ['F_centuriatio','T_land']]
    cache={}
    for a,b in pairs:
        if a not in cache: cache[a]=bvh_of(a)
        if b not in cache: cache[b]=bvh_of(b)
        ov=cache[a][0].overlap(cache[b][0])
        r={'pairs':len(ov)}
        if ov:
            # locate overlap: centroid of first polygon pairs in screen
            ob=bpy.data.objects[a]; ev=ob.evaluated_get(dg); me=ev.to_mesh(); mw=ob.matrix_world
            cs=np.array([tuple(mw@me.polygons[i].center) for i,j in ov[:4000]]); ev.to_mesh_clear()
            uv=to_pt_np(cs)
            r['screen_bbox']=[float(uv[:,0].min()),float(uv[:,0].max()),float(uv[:,1].min()),float(uv[:,1].max())]
            # penetration depth: vertices of a inside b (find_nearest normal sign)
            Va=cache[a][1]; bv=cache[b][0]
            box=r['screen_bbox']; uva=to_pt_np(Va)
            selv=np.where((uva[:,0]>=box[0]-2)&(uva[:,0]<=box[1]+2)&(uva[:,1]>=box[2]-2)&(uva[:,1]<=box[3]+2))[0]
            dmax=0.0
            for k in selv[:20000]:
                p=Vector(Va[k]); loc,nor,idx,dist=bv.find_nearest(p)
                if loc is not None and (p-loc).dot(nor)<0: dmax=max(dmax,dist)
            r['depth_world']=dmax; r['depth_pt_vert']=dmax*VS
        OUT[a+'|'+b]=r; print('OV',a,b,json.dumps(r))
json.dump(OUT,open(outp,'w'))
