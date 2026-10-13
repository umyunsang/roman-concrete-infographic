"""Counterclockwise road construction, corrected Meshy workers and aligned details."""
import hashlib,json,math,runpy
from pathlib import Path
import bpy,bmesh,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'out/roman_concrete_narrative_v9.blend';OUT=ROOT/'out/roman_concrete_narrative_v11.blend'
H=runpy.run_path(str(ROOT/'scripts/integrate_assets.py'),run_name='helpers')
assert Path(bpy.data.filepath).resolve()==SOURCE.resolve()
assert H['sha256_file'](SOURCE)=='8125d6cf8ec2da6cf09125472aa603afd1debcd88910ff8ed0893b174a2288fe'
source_sha=H['sha256_file'](SOURCE);canonical_sha=H['sha256_file'](H['SOURCE'])
def snap():
 flags={o.name:o.hide_viewport for o in bpy.data.objects}
 for o in bpy.data.objects:o.hide_viewport=False
 bpy.context.view_layer.update();x=H['source_fingerprints'](list(bpy.data.objects))
 for n,v in x.items():
  v['hide_viewport']=flags[n]
  if 'camera_data'in v:v['camera_data'].pop('session_uid',None)
 for o in bpy.data.objects:o.hide_viewport=flags[o.name]
 bpy.context.view_layer.update();return x
def index_sha(o):return hashlib.sha256(b''.join(int(p.material_index).to_bytes(2,'little')for p in o.data.polygons)).hexdigest()
before=snap();scene_before=H['scene_fingerprint'](bpy.context.scene)
indices_before={o.name:index_sha(o)for o in bpy.data.objects if o.type=='MESH'}
flags={o.name:o.hide_viewport for o in bpy.data.objects}
for o in bpy.data.objects:o.hide_viewport=False
bpy.context.view_layer.update()
operations=[];hidden=[];allowed={};parts={};palette={};materials={};applied={};new=[]
def allow(n,*fields):allowed[n]=sorted(set(allowed.get(n,[]))|set(fields))
def hide(n):
 o=bpy.data.objects[n];o.hide_render=True;flags[n]=True;hidden.append(n);allow(n,'hide_render','hide_viewport')
for o in list(bpy.data.objects):
 if o.name.startswith(('D1_','D3_','S_sect')) or (o.name.startswith('D2_')and o.name!='D2_lime_kiln') or o.name.startswith('S_lead'):
  hide(o.name)
for filename in ['hearth_object_parts.py','construction_parts.py']:
 m=runpy.run_path(str(ROOT/'scripts'/filename),run_name='part_helpers');palette.update(m['PALETTE'])
 if filename.startswith('hearth'):parts.update(m['build_assignments'](bpy))
jobs=json.loads((ROOT/'meshy_construction_jobs_v14.json').read_text())
for name,key in [('NB_vault_construction','roman_vault_timber_centering'),('NB_vault_complete','roman_completed_vault_cutaway')]:
 o=H['import_glb']({'id':key,'path':str(ROOT/'models/construction_v14'/f'{key}.glb'),'object_name':name,'source_task_id':jobs['tasks'][key]['task_id']});new.append(o.name)
parts.update(m['build_assignments'](bpy))
worker_jobs=json.loads((ROOT/'meshy_construction_workers_v14.json').read_text())
for name,key in [('NB_worker_carrier','roman_mortar_carrier'),('NB_worker_builder','roman_wall_builder'),('NB_worker_pair','roman_mortar_pair')]:
 o=H['import_glb']({'id':key,'path':str(ROOT/'models/workers_v14'/f'{key}.glb'),'object_name':name,'source_task_id':worker_jobs['tasks'][key]['task_id']});new.append(o.name)
w=runpy.run_path(str(ROOT/'scripts/worker_parts_v14.py'),run_name='part_helpers');parts.update(w['build_assignments'](bpy));palette.update(w['PALETTE'])
palette.update({'construction_timber':'#8D6C49','construction_rubble':'#B5AD97'})
def lin(hex):
 s=[int(hex[i:i+2],16)/255 for i in (1,3,5)];return [x/12.92 if x<=.04045 else((x+.055)/1.055)**2.4 for x in s]
def mat(role):
 if role not in materials:
  c=(*lin(palette[role]),1.);t=bpy.data.materials.new('RC.v14.'+role);t.diffuse_color=c;t.roughness=.85;t.use_nodes=True
  bsdf=t.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=c;bsdf.inputs['Roughness'].default_value=.85
  t['semantic_role']=role;t['sRGB_hex']=palette[role];materials[role]=t
 return materials[role]
for name,s in parts.items():
 o=bpy.data.objects[name]
 if o.data.users>1:o.data=o.data.copy()
 roles=[s['default']]+[r for r in s['faces']if r!=s['default']];slots={r:i for i,r in enumerate(roles)};o.data.materials.clear()
 for r in roles:o.data.materials.append(mat(r))
 for p in o.data.polygons:p.material_index=0
 used=set()
 for r,ids in s['faces'].items():
  assert len(ids)==len(set(ids))
  for i in ids:
   assert i not in used and 0<=i<len(o.data.polygons);used.add(i);o.data.polygons[i].material_index=slots[r]
 applied[name]={'notes':s.get('notes',''),'material_roles':roles,'initial_face_counts':{r:sum(p.material_index==slots[r]for p in o.data.polygons)for r in roles}}
 if name in before:allow(name,'materials')

# Meshy A has a complete roof. Open its front crown and add explicit timber
# centering to make the in-progress stage visible; preserve the downloaded GLB.
o=bpy.data.objects['NB_vault_construction'];mesh=o.data;bm=bmesh.new();bm.from_mesh(mesh)
cut=[f for f in bm.faces if f.calc_center_median().z>.85 and f.calc_center_median().y<-.12 and abs(f.calc_center_median().x)<.73]
removed=len(cut);bmesh.ops.delete(bm,geom=cut,context='FACES');bm.to_mesh(mesh);bm.free();mesh.update()
operations.append({'name':o.name,'action':'open front crown of Meshy-derived vault; expose added timber centering','removed_polygons':removed,'downloaded_glb_preserved':True})
def child_mesh(name,verts,faces,role,parent=o):
 data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update();ob=bpy.data.objects.new(name,data);H['get_new_collection']('46_NARRATIVE_ASSETS').objects.link(ob)
 ob.parent=parent;ob.data.materials.append(mat(role));new.append(name);return ob
def rib(name,y):
 verts=[];r=.62;t=.045;spring=.55;depth=.075;segments=24
 for i in range(segments+1):
  a=math.pi*i/segments
  for rad,yy in [(r-t,y-depth/2),(r+t,y-depth/2),(r+t,y+depth/2),(r-t,y+depth/2)]:verts.append((rad*math.cos(a),yy,spring+rad*math.sin(a)))
 faces=[(0,3,2,1),(segments*4,segments*4+1,segments*4+2,segments*4+3)]
 for i in range(segments):
  for k in range(4):faces.append((4*i+k,4*i+(k+1)%4,4*(i+1)+(k+1)%4,4*(i+1)+k))
 return child_mesh(name,verts,faces,'construction_timber')
def beam(name,x,y,z,sx,sy,sz):
 verts=[(x+dx*sx/2,y+dy*sy/2,z+dz*sz/2)for dx,dy,dz in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
 return child_mesh(name,verts,[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],'construction_timber')
for i,y in enumerate([-.45,-.08]):
 rib(f'NB_vault_timber_rib{i}',y)
 for k,x in enumerate([-.62,.62]):beam(f'NB_vault_timber_post{i}_{k}',x,y,.325,.065,.075,.45)
 beam(f'NB_vault_timber_sill{i}',0,y,.09,1.38,.11,.09)

wg=runpy.run_path(str(ROOT/'scripts/worker_geometry_v14.py'),run_name='geometry_helpers')
worker_corrections=wg['add_worker_geometry'](bpy,bmesh,H,w,child_mesh,mat,new,operations)

def copy_world(source,name,collection,parent=None):
 src=bpy.data.objects[source];world=src.matrix_world.copy();ob=bpy.data.objects.new(name,src.data.copy());H['get_new_collection'](collection).objects.link(ob);ob.parent=parent;ob.matrix_world=world;ob.hide_render=False;new.append(name);return ob
clast=copy_world('D2_lime00','NB_detail_calcium_clast','46_NARRATIVE_ASSETS');clast.parent=None
micro=bpy.data.objects.new('NB_detail4_micro',None);H['get_new_collection']('81_NOSHADOW').objects.link(micro);new.append(micro.name)
for src,n in [('D4_cube2','NB_detail4_matrix'),('D4_crack2','NB_detail4_crack'),('D4_crack2','NB_detail4_crystal')]:
 ob=copy_world(src,n,'81_NOSHADOW',micro)
 if not ob.data.materials:
  role={'NB_detail4_matrix':'base_lime_specimen_matrix','NB_detail4_crack':'base_type_heading','NB_detail4_crystal':'base_lime_calcium_crystal'}[n]
  ob.data.materials.append(bpy.data.materials.get('RC.v12.'+role))
 if n=='NB_detail4_crystal':
  ob.data.materials.clear();ob.data.materials.append(bpy.data.materials['RC.v12.base_lime_calcium_crystal'])
  toward=bpy.context.scene.camera.matrix_world.translation-ob.matrix_world.translation
  ob.matrix_world.translation+=toward.normalized()*.12
def descendants(ob):return([ob]if ob.type=='MESH'else[])+[x for x in ob.children_recursive if x.type=='MESH']
def points(ob):return np.concatenate([H['world_coords'](x)for x in descendants(ob)])
def box(ob):
 uv=H['project_pts'](points(ob));return [float(uv[:,0].min()),float(uv[:,1].min()),float(uv[:,0].max()),float(uv[:,1].max())]
def move_screen(ob,du,dv):
 origin=np.array(ob.matrix_world.translation);uv=H['project_pts']([origin])[0];delta=H['pts_to_world']([uv+[du,dv]],origin[2])[0]-origin
 ob.location.x+=float(delta[0]);ob.location.y+=float(delta[1]);bpy.context.view_layer.update()
groundverts=[];groundfaces=[]
for name in ['T_land','R_core_road','B_pons1','B_pons2']:
 ground=bpy.data.objects[name];ev=ground.evaluated_get(bpy.context.evaluated_depsgraph_get());tmp=ev.to_mesh();start=len(groundverts)
 groundverts.extend(ground.matrix_world@v.co for v in tmp.vertices);groundfaces.extend(tuple(start+i for i in p.vertices)for p in tmp.polygons);ev.to_mesh_clear()
bvh=BVHTree.FromPolygons(groundverts,groundfaces)
def plant(ob):
 pts=points(ob);low=pts[:,2].min();near=pts[pts[:,2]<low+(pts[:,2].max()-low)*.02+.001];heights=[]
 for x,y,z in near[::max(1,len(near)//100)]:
  co,_,_,_=bvh.ray_cast(Vector((float(x),float(y),100)),Vector((0,0,-1)),200)
  if co:heights.append(co.z)
 if heights:ob.location.z+=max(heights)-low+.025
 bpy.context.view_layer.update()
def fit(ob,target,ground=True):
 start=box(ob)
 for _ in range(10):
  b=box(ob);ratio=min((target[2]-target[0])/(b[2]-b[0]),(target[3]-target[1])/(b[3]-b[1]));ob.scale*=ratio;bpy.context.view_layer.update();b=box(ob)
  move_screen(ob,(target[0]+target[2]-b[0]-b[2])/2,target[3]-b[3])
  if ground:plant(ob)
 b=box(ob);assert b[0]>=target[0]-.6 and b[1]>=target[1]-.6 and b[2]<=target[2]+.6 and b[3]<=target[3]+.6,(ob.name,b,target)
 operations.append({'name':ob.name,'action':'uniform fit and plant'if ground else'uniform fit conceptual inset','before_bbox':start,'target_bbox':target,'after_bbox':b})
 if ob.name in before:
  allow(ob.name,'matrix_world','matrix_basis')
  for x in ob.children_recursive:
   if x.name in before:allow(x.name,'matrix_world')
def face_screen(ob,du,dv):
 delta=H['pts_to_world']([[600+du,1000+dv]],0)[0]-H['pts_to_world']([[600,1000]],0)[0]
 ob.rotation_euler.z=math.atan2(float(delta[1]),float(delta[0]))+math.pi/2;bpy.context.view_layer.update()
face_screen(bpy.data.objects['NB_worker_carrier'],60,22)
bpy.data.objects['NB_worker_builder'].rotation_euler.z=0
face_screen(bpy.data.objects['NB_worker_pair'],-80,-80)
# Existing hero keeps its geometry, proportions and central importance.
fit(bpy.data.objects['COL_ruined'],[395,592,791,965])
for name,target in [
 ('D2_lime_kiln',[90,578,196,710]),
 ('C2_hot_mixing',[135,779,315,940]),
 ('NB_worker_carrier',[301,913,360,1005]),
 ('NB_vault_construction',[351,920,463,1008]),
 ('NB_worker_builder',[465,920,548,1008]),
 ('NB_worker_pair',[557,902,673,1008]),
 ('NB_vault_complete',[804,887,917,970]),
 ('NB_detail_calcium_clast',[300,1170,400,1260]),
 ('L04_palatine',[65,1125,130,1189])]:fit(bpy.data.objects[name],target)
fit(micro,[682,1365,765,1414],False)
def overlay_shift(ob,du,dv):
 cam=bpy.context.scene.camera;inverse=np.linalg.inv(np.array(cam.matrix_world));view=points(ob)@inverse[:3,:3].T+inverse[:3,3];tr,br,bl,tl=[np.array(x)for x in cam.data.view_frame(scene=bpy.context.scene)]
 ratio=float(view[:,2].mean()/tr[2])if cam.data.type!='ORTHO' else 1.
 delta=np.array([du/1191*(tr[0]-bl[0])*ratio,-dv/1684*(tr[1]-bl[1])*ratio,0]);ob.location+=Vector(np.array(cam.matrix_world)[:3,:3]@delta);allow(ob.name,'matrix_world','matrix_basis');bpy.context.view_layer.update()
for n in ['S_core2_badge','S_core2_underline']:overlay_shift(bpy.data.objects[n],-39.5,-22)
for ob in bpy.data.objects:
 if ob.name in flags:ob.hide_viewport=flags[ob.name]
bpy.context.view_layer.update();after=snap()
changes={n:[k for k in before[n]if before[n][k]!=after[n][k]]for n in before if before[n]!=after[n]}
assert all(n in allowed and set(keys)<=set(allowed[n])for n,keys in changes.items()),changes
indices_after={o.name:index_sha(o)for o in bpy.data.objects if o.type=='MESH'}
assert all(indices_before[n]==indices_after[n]for n in indices_before if n!='D2_lime_kiln')
assert scene_before==H['scene_fingerprint'](bpy.context.scene)
assert H['sha256_file'](SOURCE)==source_sha and H['sha256_file'](H['SOURCE'])==canonical_sha
for n in parts:
 ob=bpy.data.objects[n];roles=[m['semantic_role']for m in ob.data.materials]
 applied[n].update(material_roles=roles,face_counts={r:sum(roles[p.material_index]==r for p in ob.data.polygons)for r in roles},polygon_count=len(ob.data.polygons),assignment_sha256=index_sha(ob))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
report={'input':str(SOURCE),'output':str(OUT),'source_sha256':source_sha,'canonical_sha256':canonical_sha,'before':before,'after':after,
 'allowed_existing_changes':allowed,'actual_existing_changes':changes,'new_objects':new,'hidden_objects':hidden,'operations':operations,'worker_corrections':worker_corrections,
 'indices_before':indices_before,'indices_after':indices_after,'applied':applied,'materials':{r:{'name':t.name,'hex':palette[r],'linear_color':list(t.diffuse_color)}for r,t in materials.items()},
 'total_objects':len(bpy.data.objects),'total_materials':sum(m.users>0 or m.use_fake_user for m in bpy.data.materials),'in_memory_materials':len(bpy.data.materials),'retired_unused_materials':[m.name for m in bpy.data.materials if m.users==0 and not m.use_fake_user],'new_meshy_jobs':5,'credits_used':100,'worker_meshy_jobs':3,'worker_credits':60,'construction_direction':'counterclockwise along R_core_road and B_pons2, final delivery inward toward central Colosseum',
 'render_passes':H['render_two_pass'](ROOT/'renders/narrative_v11_construction_details.png')}
(ROOT/'out/construction-detail-v11.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(ROOT/'copy/construction_material_palette_v14.json').write_text(json.dumps({'part_colors':palette,'materials':report['materials']},ensure_ascii=False,indent=2)+'\n')
print('CONSTRUCTION_V11_COMPLETE',json.dumps({k:report[k]for k in ['output','total_objects','total_materials','credits_used']},ensure_ascii=False))
