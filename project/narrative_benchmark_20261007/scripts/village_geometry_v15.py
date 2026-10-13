"""Actual village architecture and workspaces; no display bases or abstract cubes."""
import math,random

def build_village(bpy,H,bmesh,np,Vector,BVHTree,layout,mat,child_mesh,copy_world,new,operations,fit,plant,box,move_screen,face_screen,allow):
 records=[];rng=random.Random(1512)
 def objects(ob):return ([ob]if ob.type=='MESH'else[])+[c for c in ob.children_recursive if c.type=='MESH']
 def pts(ob):return np.concatenate([H['world_coords'](x)for x in objects(ob)])
 def floor_uv(ob):
  p=pts(ob);lo=p[:,2].min();q=p[p[:,2]<lo+.045];return H['project_pts']([q.mean(0)])[0]
 def place(ob,anchor,height=None,yaw=None,ground=True):
  if yaw is not None:ob.rotation_euler.z=math.radians(yaw)
  bpy.context.view_layer.update()
  if height is not None:
   p=pts(ob);ob.scale*=height/(p[:,2].max()-p[:,2].min());bpy.context.view_layer.update()
  for _ in range(4):
   uv=floor_uv(ob);move_screen(ob,anchor[0]-uv[0],anchor[1]-uv[1])
   if ground:plant(ob)
  p=pts(ob);entry={'name':ob.name,'anchor':anchor,'actual_floor_proxy':floor_uv(ob).tolist(),'world_height':float(p[:,2].max()-p[:,2].min()),'bbox':box(ob),'yaw':math.degrees(ob.rotation_euler.z)};records.append(entry)
  if ob.name.startswith(('C2_','D2_','L04_')):
   allow(ob.name,'matrix_basis','matrix_world')
   for c in ob.children_recursive:allow(c.name,'matrix_world')
  return entry
 def group(name):
  o=bpy.data.objects.new(name,None);H['get_new_collection']('46_NARRATIVE_ASSETS').objects.link(o);new.append(name);return o
 def clone(src,name):
  a=copy_world(src.name,name,'46_NARRATIVE_ASSETS');mapping={src:a}
  for key in src.keys():
   if key.startswith('narrative_'):a[key]=src[key]
  a['narrative_cloned_from']=src.name
  for c in src.children_recursive:
   parent=mapping.get(c.parent,a);n=copy_world(c.name,name+'__'+c.name,'46_NARRATIVE_ASSETS',parent);mapping[c]=n
  return a
 def beam(name,c,s,role,parent=None):
  v=[tuple(c[k]+d[k]*s[k]/2 for k in range(3))for d in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
  return child_mesh(name,v,[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],role,parent)
 def beam_between(name,a,b,w,role,parent=None):
  a,b=Vector(a),Vector(b);d=b-a;c=(a+b)/2;ob=beam(name,(0,0,0),(w,w,d.length),role,parent);ob.rotation_euler=d.to_track_quat('Z','Y').to_euler();ob.location=c;return ob
 def patch(name,anchor,rx,ry):
  center=H['pts_to_world']([anchor],0)[0];verts=[(center[0],center[1],.028)]
  for i in range(14):
   t=2*math.pi*i/14;r=rng.uniform(.90,1.08);verts.append((center[0]+rx*r*math.cos(t),center[1]+ry*r*math.sin(t),.028))
  faces=[(0,i+1,(i+1)%14+1)for i in range(14)];ob=child_mesh(name,verts,faces,'village_paving',None)
  # The terrain is smooth at selected reservations; patch lies on soil, not
  # a raised stage. Fit its Z to the local terrain height through plant.
  plant(ob);return ob
 def stone(name,c,r,role,parent=None):
  verts=[]
  for z,rad in [(-.32,.75),(.1,1.),(.55,.54)]:
   for i in range(7):
    t=2*math.pi*i/7;rr=rad*r*rng.uniform(.86,1.13);verts.append((c[0]+rr*math.cos(t),c[1]+rr*math.sin(t),c[2]+z*r))
  faces=[tuple(reversed(range(7))),tuple(range(14,21))]
  for j in range(2):
   for i in range(7):faces.append((j*7+i,j*7+(i+1)%7,(j+1)*7+(i+1)%7,(j+1)*7+i))
  return child_mesh(name,verts,faces,role,parent)
 # Repair the missing citizen head with the actual left citizen head.
 c=bpy.data.objects['NB_village_citizens']
 # Helper's normalized masks are consumed before any topology edits.
 import runpy
 vh=runpy.run_path(str(__import__('pathlib').Path(__file__).resolve().parent/'village_parts_v15.py'),run_name='village_helpers')
 mask=vh['build_correction_masks'](bpy)['NB_village_citizens'];ids=mask['left_head_for_copy']['faces'];vs=sorted(set(k for i in ids for k in c.data.polygons[i].vertices));mapping={k:i for i,k in enumerate(vs)}
 q=np.array([c.data.vertices[k].co[:]for k in vs]);low,hi=q.min(0),q.max(0);target=[*vh['CORRECTION_GUIDES']['right_empty_neck_center'][:2],1.66];q=q-np.array([(low[0]+hi[0])/2,(low[1]+hi[1])/2,low[2]])+np.array(target)
 head=child_mesh('V_citizen_head',q.tolist(),[tuple(mapping[k]for k in c.data.polygons[i].vertices)for i in ids],'skin',c);head.data.materials.clear()
 for m in c.data.materials:head.data.materials.append(m)
 for p,i in zip(head.data.polygons,ids):p.material_index=c.data.polygons[i].material_index;p.use_smooth=True
 # Move the real source amphora to the actual crossed hands. Keep the GLB,
 # garment/limb surfaces and all unselected geometry intact.
 potids=mask['amphora_for_move']['faces'];pvs=sorted(set(k for i in potids for k in c.data.polygons[i].vertices));pmap={k:i for i,k in enumerate(pvs)}
 delta=np.array(vh['CORRECTION_GUIDES']['proposed_amphora_neck_at_hands'])-np.array(vh['CORRECTION_GUIDES']['source_amphora_neck_center'])
 pot=child_mesh('V_citizen_carried_amphora',[(np.array(c.data.vertices[k].co)+delta).tolist()for k in pvs],[tuple(pmap[k]for k in c.data.polygons[i].vertices)for i in potids],'village_terracotta',c)
 for p in pot.data.polygons:p.use_smooth=True
 bm=bmesh.new();bm.from_mesh(c.data);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.faces[i]for i in potids],context='FACES');loose=[v for v in bm.verts if not v.link_faces]
 if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
 bm.to_mesh(c.data);bm.free();c.data.update()
 for k,hand in enumerate(vh['CORRECTION_GUIDES']['right_actual_crossed_hand_hits']):beam_between('V_citizen_jarhandle'+str(k),hand,tuple(np.array(vh['CORRECTION_GUIDES']['proposed_amphora_neck_at_hands'])+np.array([(-.025 if k==0 else .025),0,-.022])),.025,'village_terracotta',c)
 operations.append({'name':c.name,'action':'copy actual source human head to missing neck; move actual amphora beside the crossed hands and connect handles','copied_head_faces':len(ids),'moved_vessel_faces':len(potids),'source_glb_preserved':True})
 # All assets share plausible physical units, rather than filling poster
 # rectangles with oversized figures.
 fit(bpy.data.objects['COL_ruined'],[395,592,791,965])
 houses=[];base=bpy.data.objects['NB_village_house']
 for i,(anchor,yaw,height)in enumerate(layout['houses']):
  ob=base if i==0 else clone(base,'V_house_%02d'%i);place(ob,anchor,height,yaw);houses.append(ob.name);patch('V_house_courtyard_%02d'%i,anchor,3.6,3.0)
 market=bpy.data.objects['NB_village_market'];place(market,layout['market'],4.1,-10);patch('V_market_ground',layout['market'],4.3,3.3)
 place(bpy.data.objects['D2_lime_kiln'],layout['kiln'],3.5,-12)
 place(bpy.data.objects['C2_hot_mixing'],layout['maker'],3.45,0)
 patch('V_making_ground',layout['maker'],4.0,3.4)
 carrier=bpy.data.objects['NB_worker_carrier'];face_screen(carrier,50,-20);place(carrier,layout['carrier'],2.5)
 citizen_copies=[]
 for i,(anchor,yaw)in enumerate(layout['citizens']):
  ob=c if i==0 else clone(c,'V_citizens_%02d'%i);place(ob,anchor,2.45,yaw);citizen_copies.append(ob.name)
 va=bpy.data.objects['NB_vault_construction'];vb=bpy.data.objects['NB_vault_complete'];place(va,layout['vault_construction'],4.8,0);place(vb,layout['vault_complete'],4.4,-12)
 builder=bpy.data.objects['NB_worker_builder'];place(builder,layout['builder'],2.5,0)
 pair=bpy.data.objects['NB_worker_pair'];place(pair,layout['pair'],2.5,221.4250477)
 # Stockpiles are actual loose chunks and low mortar residues in workyards.
 for prefix,anchor,material in [('raw',layout['raw_pile'],'raw_lime'),('rubble',layout['mortar_pile'],'worker_mortar')]:
  g=group('V_'+prefix+'_pile')
  for i in range(8):stone('V_'+prefix+'_chunk%02d'%i,(rng.uniform(-1.2,1.2),rng.uniform(-.7,.7),rng.uniform(.18,.4)),rng.uniform(.26,.52),material,g)
  place(g,anchor)
 patch('V_sw_workyard',layout['vault_construction'],4.6,3.5);patch('V_se_workyard',layout['vault_complete'],4.1,3.3)
 # Actual wall panels within the two workshops replace the specimen cube and
 # disconnected crack triptych. White inclusions remain in cured mortar.
 walls=[]
 for i,anchor in enumerate(layout['walls']):
  g=group('V_mortar_wall_%d'%i);beam('V_wall_core_%d'%i,(0,0,1.05),(3.8,.40,2.1),'worker_mortar',g)
  for z in [.30,.80,1.30,1.80]:
   for x in [-1.42,-.48,.48,1.42]:beam('V_wall_facing_%d_%s_%s'%(i,z,x),(x,-.14,z),(.86,.43,.43),'roman_stone',g)
  if i==0:
   # Small lime-bearing inclusions on an exposed, cured mortar end.
   for k in range(9):stone('V_wall_lime_%02d'%k,(-1.91,-.06,.22+k*.19),.045,'raw_lime',g)
  else:
   path=[(-.15,-.36,1.96),(.05,-.36,1.58),(-.08,-.36,1.15),(.18,-.36,.72),(.03,-.36,.24)]
   for k in range(4):beam_between('V_wall_crack%d'%k,path[k],path[k+1],.025,'worker_dark',g)
   for k in [2,3]:beam_between('V_wall_whitefill%d'%k,tuple(v-.006 if a==1 else v for a,v in enumerate(path[k])),tuple(v-.006 if a==1 else v for a,v in enumerate(path[k+1])),.012,'raw_lime',g)
  place(g,anchor,None,0);walls.append(g.name)
 # Ground the previous lab architecture by removing its display-island rock
 # in a COPY, preserving the original hidden mesh and material palette.
 lab=copy_world('S_lab_island','V_grounded_research_building','46_NARRATIVE_ASSETS');bm=bmesh.new();bm.from_mesh(lab.data)
 # The old lab's base role contains the display rock. The default labstone
 # role belongs to the building walls, which must remain intact.
 cut=[f for f in bm.faces if lab.data.materials[f.material_index].name=='RC.v12.base'];bmesh.ops.delete(bm,geom=cut,context='FACES');loose=[v for v in bm.verts if not v.link_faces]
 if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
 bm.to_mesh(lab.data);bm.free();lab.data.update();place(lab,layout['research'],4.6);patch('V_research_ground',layout['research'],3.,2.5)
 operations.append({'name':lab.name,'action':'retire island rock only in a copied mesh; ground actual building on terrain','removed_rock_faces':len(cut),'original_geometry_preserved':True})
 # Native camera rays locate the actual Colosseum facade. Scaffolds are
 # anchored against that surface with ground supports and working platforms.
 col=bpy.data.objects['COL_ruined'];cp=H['world_coords'](col);bv=BVHTree.FromPolygons([Vector(v)for v in cp],[tuple(p.vertices)for p in col.data.polygons]);cam=bpy.context.scene.camera
 tr,br,bl,tl=[Vector(v)for v in cam.data.view_frame(scene=bpy.context.scene)]
 tland=bpy.data.objects['T_land'];tv=H['world_coords'](tland);groundtree=BVHTree.FromPolygons([Vector(v)for v in tv],[tuple(p.vertices)for p in tland.data.polygons])
 def ground_height(x,y):
  co,_,_,_=groundtree.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),200);return co.z+.025 if co else .025
 scaffold_records=[]
 for i,uv in enumerate(layout['scaffold_wall_pixels']):
  q=bl+(br-bl)*(uv[0]/1191)+(tl-bl)*(1-uv[1]/1684)
  if cam.data.type=='ORTHO':origin=cam.matrix_world@Vector((q.x,q.y,0));direction=cam.matrix_world.to_3x3()@Vector((0,0,-1))
  else:origin=cam.matrix_world.translation;direction=(cam.matrix_world.to_3x3()@q).normalized()
  co,n,index,dist=bv.ray_cast(origin,direction,2000)
  if co is None:raise ValueError('Scaffold facade ray missed '+str(uv))
  n=Vector((n.x,n.y,0));toward=cam.matrix_world.translation-co;toward.z=0
  if n.length<.1:n=toward.normalized()
  else:n.normalize()
  if n.dot(toward)<0:n=-n
  t=Vector((-n.y,n.x,0));center=co+n*.88;level=max(3.,min(9.,co.z-.55));g=group('V_COL_scaffold_%d'%i)
  # Group geometry is in world coordinates so support/attachment are exact.
  for a in [-1.9,1.9]:
   for b in [.25,1.5]:
    xy=co+t*a+n*b;gz=ground_height(xy.x,xy.y);beam('V_COL_post_%d_%s_%s'%(i,a,b),(xy.x,xy.y,(gz+level+1.05)/2),(.12,.12,level+1.05-gz),'toolwood',g)
  for z in [level-2.7,level]:
   if z<1.:continue
   # Flat planks on the work platform, tangent to the real wall.
   for k in range(5):
    xy=co+t*(-1.6+k*.8)+n*.9;ob=beam('V_COL_plank_%d_%s_%d'%(i,z,k),(0,0,0),(.77,1.42,.11),'toolwood',g);ob.rotation_euler.z=math.atan2(t.y,t.x);ob.location=(xy.x,xy.y,z)
   for b in [.25,1.5]:beam_between('V_COL_rail_%d_%s_%s'%(i,z,b),co-t*1.95+n*b+Vector((0,0,z+.85-co.z)),co+t*1.95+n*b+Vector((0,0,z+.85-co.z)),.08,'toolwood',g)
  for side in [-1.9,1.9]:
   a=co+t*side+n*.25;a.z=ground_height(a.x,a.y);b=co+t*side+n*1.5;b.z=level;beam_between('V_COL_brace_%d_%s'%(i,side),a,b,.075,'toolwood',g)
  actor=clone(builder,'V_COL_mason_%d'%i)
  # Copied kneeling source plus its low wall is a believable work surface.
  p=pts(actor);actor.scale*=2.4/(p[:,2].max()-p[:,2].min());actor.rotation_euler.z=math.atan2(-n.y,-n.x)+math.pi/2;bpy.context.view_layer.update()
  low=pts(actor);xymean=low[low[:,2]<low[:,2].min()+.03].mean(0);actor.location+=Vector((center.x-xymean[0],center.y-xymean[1],level+.065-low[:,2].min()));bpy.context.view_layer.update()
  scaffold_records.append({'scaffold':g.name,'worker':actor.name,'facade_pixel':uv,'actual_surface_point':list(co),'normal':list(n),'platform_level':level,'worker_height':float(pts(actor)[:,2].ptp()) if hasattr(pts(actor)[:,2],'ptp')else float(np.ptp(pts(actor)[:,2])),'worker_bbox':box(actor),'scaffold_bbox':box(g),'attachment_face':index})
 # Small loose building materials around the direct work zone; no road line
 # or process chain is built into the village.
 for i,anchor in enumerate(layout['col_rubble']):
  g=group('V_COL_materials%d'%i)
  for k in range(4):stone('V_COL_rubble_%d_%d'%(i,k),(rng.uniform(-1,1),rng.uniform(-.6,.6),.22),.35,'roman_stone',g)
  place(g,anchor)
 operations.append({'action':'integrated village physical placement','records':records,'attached_scaffolds':scaffold_records})
 return {'placements':records,'house_objects':houses,'citizen_groups':citizen_copies,'walls':walls,'scaffolds':scaffold_records,'direction':'village courts and workspaces off the roads; main CORE counterclockwise','retired_display_island':True}
