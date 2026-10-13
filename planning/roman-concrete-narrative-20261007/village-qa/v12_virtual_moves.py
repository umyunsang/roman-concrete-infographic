"""Mathematical candidate translations/scaling only; never modifies bpy objects."""
import bpy,runpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/Users/um-yunsang/Documents/로마콘크리트_3D/narrative_benchmark_20261007');O=Path('/Users/um-yunsang/.planning/roman-concrete-narrative-20261007/village-qa');H=runpy.run_path(str(R/'scripts/integrate_assets.py'),run_name='helpers')
M=np.load(O.parent/'construction-detail/village-plan.masks.npz')
def group(n):
 o=bpy.data.objects[n];return([o]if o.type=='MESH'else[])+[c for c in o.children_recursive if c.type=='MESH']
def data(names):
 points=[];faces=[]
 for o in names:
  p=H['world_coords'](o);k=len(points);points.extend(p.tolist());faces.extend(tuple(k+i for i in f.vertices)for f in o.data.polygons)
 return np.array(points),faces
p,f=data([bpy.data.objects[n]for n in ['T_land','R_core_road','B_pons1','B_pons2']]);ground=BVHTree.FromPolygons([Vector(q)for q in p],f)
cp,cf=data(group('COL_ruined'));col=BVHTree.FromPolygons([Vector(q)for q in cp],cf)
def hull(a):
 q=sorted(set(map(tuple,a.tolist())))
 if len(q)<3:return q
 def cross(a,b,c):return(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 l=[];u=[]
 for p in q:
  while len(l)>1 and cross(l[-2],l[-1],p)<=0:l.pop()
  l.append(p)
 for p in reversed(q):
  while len(u)>1 and cross(u[-2],u[-1],p)<=0:u.pop()
  u.append(p)
 return l[:-1]+u[:-1]
def pixelstats(poly):
 a=np.asarray(poly);x0=max(0,int(a[:,0].min()));x1=min(1190,int(np.ceil(a[:,0].max())));y0=max(0,int(a[:,1].min()));y1=min(1683,int(np.ceil(a[:,1].max())));yy,xx=np.mgrid[y0:y1+1,x0:x1+1];x=xx+.5;y=yy+.5;m=np.zeros(x.shape,bool);previous=a[-1]
 for point in a:
  if point[1]!=previous[1]:m^=((point[1]>y)!=(previous[1]>y))&(x<(previous[0]-point[0])*(y-point[1])/(previous[1]-point[1])+point[0])
  previous=point
 return {k:int((m&M[k][y0:y1+1,x0:x1+1]).sum())for k in ['road','water']}
def virtual(name,target,height=None,label=None):
 ob=bpy.data.objects[name];p,faces=data(group(name));origin=np.array(ob.matrix_world.translation);ratio=1 if height is None else height/np.ptp(p[:,2]);p=(p-origin)*ratio+origin
 for _ in range(4):
  lo=p[:,2].min();q=p[p[:,2]<lo+.045];uv=H['project_pts']([q.mean(0)])[0];delta=np.asarray(target)-uv;ou=H['project_pts']([origin])[0];xyz=H['pts_to_world']([ou+delta],origin[2])[0]-origin;p[:,:2]+=xyz[:2];origin[:2]+=xyz[:2]
  lo=p[:,2].min();q=p[p[:,2]<lo+np.ptp(p[:,2])*.02+.001];hits=[]
  for x,y,z in q[::max(1,len(q)//100)]:
   h=ground.ray_cast(Vector((float(x),float(y),100)),Vector((0,0,-1)),200)
   if h[0] is not None:hits.append(h[0].z)
  dz=max(hits)-lo+.025 if hits else 0;p[:,2]+=dz;origin[2]+=dz
 lo=p[:,2].min();q=p[p[:,2]<lo+max(.045,np.ptp(p[:,2])*.02)];uv=H['project_pts'](q);poly=hull(uv);stats=pixelstats(poly);coarse=np.all(p.max(0)>=cp.min(0))and np.all(cp.max(0)>=p.min(0));overlap=BVHTree.FromPolygons([Vector(v)for v in p],faces).overlap(col)if coarse else[]
 return {'name':label or name,'source':name,'target_anchor':target,'actual_floor_mean':H['project_pts']([p[p[:,2]<lo+.045].mean(0)])[0].tolist(),'height_world':float(np.ptp(p[:,2])),'floor_hull':poly,**stats,'COLsurface_overlap_pairs':len(overlap)}
items=[('V_house_01',[510,623],None,None),('V_house_courtyard_01',[510,623],None,None),('NB_village_citizens',[658,613],None,None),('V_citizens_02',[637,1220],None,None),('NB_worker_builder',[476,1222],None,None),('V_mortar_wall_1',[849,1273],None,None),('NB_village_house',[360,751],3.9,'proposed_W_house'),('V_house_courtyard_00',[360,751],None,'proposed_W_house_courtyard')]
rows=[virtual(*x)for x in items]
D={'source_sha':H['sha256_file'](bpy.data.filepath),'mathematical_only_no_bpy_transforms_applied':True,'candidates':rows,'method':'Copies of current world point arrays scaled around real object origin and mathematically translated/ground-planted with source controller policy. Independent actual floor-hull raster and world COLBVH intersection; no object mutation/save/render.'}
(O/'v12-virtual-moves-validation.json').write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n')
for r in rows:print('VIRTUAL',json.dumps({k:v for k,v in r.items()if k!='floor_hull'},ensure_ascii=False))
