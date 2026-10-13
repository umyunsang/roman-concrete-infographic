"""Local readable construction corrections to actual Meshy-generated workers.
The three source GLBs are preserved. Called only by root's v11 controller.
"""
def add_worker_geometry(bpy,bmesh,H,w,child_mesh,mat,new,operations):
 from math import sin,cos,pi
 masks=w['build_correction_masks'](bpy)
 carrier=bpy.data.objects['NB_worker_carrier'];builder=bpy.data.objects['NB_worker_builder'];pair=bpy.data.objects['NB_worker_pair']
 # Copy an actual Meshy human head, keep its material indices, then place it
 # at the surviving carrier neck; do not pretend the bucket was a head.
 ids=masks[builder.name]['head_for_copy']['faces'];vset=sorted(set(i for p in ids for i in builder.data.polygons[p].vertices));remap={i:k for k,i in enumerate(vset)}
 import numpy as np
 coords=np.array([builder.data.vertices[i].co[:] for i in vset]);low,high=coords.min(0),coords.max(0)
 coords=(coords-np.array([(low[0]+high[0])/2,(low[1]+high[1])/2,low[2]]))*.87+np.array([.020,-.060,1.425])
 head=child_mesh('NB_carrier_human_head',coords.tolist(),[tuple(remap[i]for i in builder.data.polygons[p].vertices)for p in ids],'skin',carrier)
 head.data.materials.clear()
 for m in builder.data.materials:head.data.materials.append(m)
 for p,source in zip(head.data.polygons,ids):p.material_index=builder.data.polygons[source].material_index
 for p in head.data.polygons:p.use_smooth=True
 remove=set(masks[carrier.name]['head_bucket']['faces']+masks[carrier.name]['unwanted_hand_bars']['faces'])
 bm=bmesh.new();bm.from_mesh(carrier.data);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.faces[i]for i in remove],context='FACES')
 # Remove only loose source vertices, preserving actual body/hand geometry.
 loose=[v for v in bm.verts if not v.link_faces]
 if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
 bm.to_mesh(carrier.data);bm.free();carrier.data.update()
 operations.append({'name':carrier.name,'action':'remove failed bucket-head/hand bars; copy real Meshy builder head; add filled bucket connected to actual hands','removed_faces':len(remove),'head_source_faces':len(ids),'source_glb_unchanged':True})
 def beam(name,c,s,role,parent):
  verts=[(c[0]+dx*s[0]/2,c[1]+dy*s[1]/2,c[2]+dz*s[2]/2)for dx,dy,dz in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
  return child_mesh(name,verts,[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],role,parent)
 def cylinder(name,center,radius,height,role,parent):
  verts=[];n=24
  for z in [center[2]-height/2,center[2]+height/2]:
   verts.extend((center[0]+radius*cos(2*pi*i/n),center[1]+radius*sin(2*pi*i/n),z)for i in range(n))
  faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)]
  return child_mesh(name,verts,faces,role,parent)
 def tube(name,path,radius,role,parent):
  from mathutils import Vector
  verts=[];n=8
  for i,c in enumerate(path):
   tangent=Vector(path[min(i+1,len(path)-1)])-Vector(path[max(i-1,0)]);tangent.normalize();u=tangent.cross(Vector((0,0,1)))
   if u.length<.001:u=tangent.cross(Vector((0,1,0)))
   u.normalize();v=tangent.cross(u)
   verts.extend(tuple(Vector(c)+radius*(u*cos(2*pi*k/n)+v*sin(2*pi*k/n)))for k in range(n))
  faces=[tuple(reversed(range(n))),tuple(range((len(path)-1)*n,len(path)*n))]
  for i in range(len(path)-1):
   for k in range(n):faces.append((i*n+k,i*n+(k+1)%n,(i+1)*n+(k+1)%n,(i+1)*n+k))
  return child_mesh(name,verts,faces,role,parent)
 # Wooden open bucket and visible pale mortar. Two side handles terminate
 # inside the preserved palms rather than floating above them.
 n=24;verts=[]
 for r,z in [(.145,.82),(.175,1.055),(.143,1.055),(.127,.86)]:verts.extend((.017+r*cos(2*pi*i/n),-.43+r*sin(2*pi*i/n),z)for i in range(n))
 faces=[]
 for j in range(3):
  for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
 faces.append(tuple(range(3*n,4*n)));child_mesh('NB_carrier_bucket',verts,faces,'toolwood',carrier)
 cylinder('NB_carrier_mortar',(.017,-.43,1.024),.141,.028,'worker_mortar',carrier)
 for k,x in enumerate([-.158,.192]):
  hand=w['CORRECTION_GUIDES']['carrier_hand_centers'][k]
  tube('NB_carrier_handle'+str(k),[(x,-.43,1.055),(x,-.40,1.115),tuple(hand),(x,-.28,1.09),(x,-.27,1.03)],.018,'toolmetal',carrier)
 # Actual empty pair trough receives a separate small visible fill, retaining
 # its modeled wooden rim and natural hand connection.
 beam('NB_pair_mortar',(-.030,-.105,.997),(.230,.140,.030),'worker_mortar',pair)
 # A low stepped masonry/mortar wall and timber side form beside the actual
 # kneeling Meshy builder. No claim this is an exact archaeological replica.
 beam('NB_build_wall_mortar',(-.055,-.58,.27),(1.12,.29,.51),'worker_mortar',builder)
 for row,z in enumerate([.135,.35,.57]):
  for k,x in enumerate([-.475,-.20,.075,.35]):
   if row==2 and k>1:continue
   beam('NB_build_stone_%d_%d'%(row,k),(x+(.025 if row%2 else 0),-.58,z),(.247,.265,.185),'roman_stone',builder)
 for k,x in enumerate([-.64,.54]):beam('NB_build_formpost'+str(k),(x,-.80,.26),(.055,.065,.52),'toolwood',builder)
 for k,z in enumerate([.095,.245]):beam('NB_build_formboard'+str(k),(-.05,-.80,z),(1.28,.042,.11),'toolwood',builder)
 beam('NB_build_formbrace',(-.64,-.96,.145),(.045,.32,.045),'toolwood',builder)
 operations.append({'name':builder.name,'action':'add visible low stepped masonry wall, mortar seams and wooden side form next to real kneeling worker'})
 operations.append({'name':pair.name,'action':'add visible mortar fill to actual carried wooden trough'})
 return {'carrier_removed_faces':len(remove),'copied_meshy_head_faces':len(ids)}
