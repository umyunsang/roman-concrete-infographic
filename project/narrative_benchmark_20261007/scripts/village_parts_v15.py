"""Pure part selections for three actual generated living-village source meshes.

Use H.import_glb normalized local coordinates and ORIGINAL topology. Apply
material assignments before root's citizen head/vessel correction and before
house duplication. No geometry, material, scene, or file mutation here.

Headless right citizen is a documented source failure. It is never colored
as though a human head exists. Root grafts the real left head locally.
"""
import numpy as np

PALETTE={
    'village_plaster':'#DCCFB8',
    'village_roof':'#B77B60',
    'village_stone':'#B5A68B',
    'village_wood':'#8D6C49',
    'village_terracotta':'#AC7055',
    'village_basket':'#A3885E',
    'village_canopy':'#D9CFB1',
    'village_linen':'#DED1AF',
    'village_cloth':'#A66F57',
    'village_skin':'#C99C78',
    'village_sandals':'#735A42',
}
EXPECTED={'NB_village_house':20188,'NB_village_market':20448,'NB_village_citizens':20661}
CORRECTION_GUIDES={
 'head_source_center':[-.303572,-.245771,1.737341],
 'right_empty_neck_center':[.231305,.268044,1.638757],
 'right_graft_low_z_range':[1.65,1.67],
 'right_actual_crossed_hand_hits':[[.128667,-.035823,1.277058],[.215977,-.014914,1.243411]],
 'source_amphora_body_center':[.506,.365,.930],
 'source_amphora_neck_center':[.470,.360,1.093],
 'proposed_amphora_neck_at_hands':[.180,-.095,1.250],
 'source_left_head_note':'A real bald human head. Keep copied material village_skin; no invented hair cap.',
 'amphora_move_note':'Cylinder region exposes the full actual vessel shoulder/back; its contact edge includes thin fused garment triangles. Root inspects that boundary before copying/removing. Connect actual crossed hands to the moved vessel neck/handles.',
}

def _geometry(ob):
 me=ob.data;v=np.empty(len(me.vertices)*3);c=np.empty(len(me.polygons)*3);n=np.empty(len(me.polygons)*3);a=np.empty(len(me.polygons))
 me.vertices.foreach_get('co',v);me.polygons.foreach_get('center',c);me.polygons.foreach_get('normal',n);me.polygons.foreach_get('area',a)
 v=v.reshape(-1,3)
 zmin=np.fromiter((v[list(p.vertices),2].min()for p in me.polygons),dtype=float)
 zmax=np.fromiter((v[list(p.vertices),2].max()for p in me.polygons),dtype=float)
 return v,c.reshape(-1,3),n.reshape(-1,3),a,zmin,zmax
def _ellipsoid(c,p,r):return np.sum(((c-np.asarray(p))/np.asarray(r))**2,axis=1)<1
def _segment(c,a,b,r):
 a=np.asarray(a);d=np.asarray(b)-a;t=np.clip((c-a)@d/(d@d),0,1)
 return np.linalg.norm(c-a-t[:,None]*d,axis=1)<r
def _ids(mask):return np.flatnonzero(mask).astype(int).tolist()
def _amphora(c):
 # The actual shoulder is broader than an ellipsoid. A narrow XY cylinder
 # spanning the inspected vessel keeps the back shoulder/neck intact.
 x,y,z=c.T
 radial=((x-.492)/.116)**2+((y-.363)/.134)**2<1
 return radial&(x>.391)&(y>.255)&(z>.748)&(z<1.184)
def _left_head(c):
 x,y,z=c.T;return (x<-.170)&(y<-.100)&(z>1.625)

def _house(v,c,n,a,zmin,zmax):
 x,y,z=c.T;role=np.full(len(c),'village_plaster',dtype=object)
 # Actual high tile roof, preserving vertically oriented masonry gable ends.
 roof=(z>.900)&~((np.abs(n[:,0])>.90)&(a>.008))
 role[roof]='village_roof'
 # Existing low stone/step/bed fragments only; not an invented diorama floor.
 role[(zmax<.180)&(y<-.560)&~roof]='village_stone'
 # Real recessed rectangular door panel, excluding forward plaster jambs.
 door=(x>-.275)&(x<-.012)&(y>-.465)&(y<-.380)&(z>.080)&(z<.740)
 role[door]='village_wood'
 vessel=_ellipsoid(c,(.046,-.646,.249),(.128,.158,.228))&(y<-.545)&(a<.009)
 role[vessel]='village_terracotta'
 return role

def _market(v,c,n,a,zmin,zmax):
 x,y,z=c.T;role=np.full(len(c),'village_wood',dtype=object)
 # Four real corner posts and their crossbar ends stay wood; the intervening
 # high fabric surface and scalloped valance receive quiet cream cloth.
 posts=np.zeros(len(c),dtype=bool)
 for px in [-.838,.838]:
  for py in [-.585,.615]:posts|=(np.abs(x-px)<.077)&(np.abs(y-py)<.093)
 canopy=(z>.825)&~posts
 role[canopy]='village_canopy'
 # Recognizable pottery at the left counter and on the ground.
 pottery=np.zeros(len(c),dtype=bool)
 for center,r in [((-.565,.068,.471),(.109,.140,.165)),((-.411,.027,.372),(.058,.064,.060)),((-.337,.046,.374),(.058,.067,.061)),((-.340,-.067,.171),(.104,.126,.175)),((.460,.053,.439),(.070,.088,.095))]:
  pottery|=_ellipsoid(c,center,r)
 role[pottery&~canopy&(a<.003)]='village_terracotta'
 # Two actual woven baskets, with the underlying timber stand kept wood.
 baskets=_ellipsoid(c,(-.181,-.150,.172),(.092,.107,.156))|_ellipsoid(c,(.450,.065,.354),(.163,.199,.091))
 role[baskets&~canopy&(a<.004)]='village_basket'
 # Visible merchant body occupies a bounded local volume under the canopy.
 person=(x>.022)&(x<.295)&(y>-.173)&(y<.190)&(z>.130)&(z<.780)
 role[person]='village_linen'
 head=(x>.067)&(x<.228)&(y>-.225)&(y<.075)&(z>.645)&(z<.790)
 arms=np.zeros(len(c),dtype=bool)
 for a,b,r in [((.060,.010,.571),(.054,-.067,.468),.038),((.054,-.067,.468),(.118,-.130,.421),.035),((.257,.010,.570),(.259,-.056,.422),.038)]:arms|=_segment(c,a,b,r)
 # Exposed lower shins/feet; preserve the actual garment hem above them.
 legs=(x>.064)&(x<.260)&(y>-.135)&(y<.160)&(z<.160)
 role[(head|arms|legs)&~canopy]='village_skin'
 sandals=legs&(z<.043);role[sandals]='village_sandals'
 return role

def _citizens(v,c,n,area,zmin,zmax):
 x,y,z=c.T;role=np.where(x<0,'village_cloth','village_linen').astype(object)
 basket=_ellipsoid(c,(-.435,-.370,1.085),(.160,.145,.165))&(z<1.245)&(area<.003)
 role[basket]='village_basket'
 # Existing amphora is at the right hip; no claim it is correctly held yet.
 vessel=_amphora(c);role[vessel]='village_terracotta'
 # Complete left face/scalp/neck, but NO right head exists in the source.
 head=(x<-.170)&(y<-.100)&(zmin>1.570)
 role[head]='village_skin'
 # Actual arms/hands are front of their garment volumes. Keep backs of both
 # tunics outside these narrow local limb segments.
 arms=np.zeros(len(c),dtype=bool)
 for a,b,r in [
  ((-.165,-.180,1.490),(-.153,-.304,1.335),.079),
  ((-.153,-.304,1.335),(-.341,-.348,1.254),.067),
  ((-.449,-.164,1.463),(-.462,-.223,1.328),.062),
  ((-.462,-.223,1.328),(-.367,-.350,1.248),.060),
  ((.067,.171,1.490),(.042,.072,1.312),.081),
  ((.042,.072,1.312),(.216,-.015,1.243),.071),
  ((.395,.218,1.460),(.429,.095,1.276),.078),
  ((.429,.095,1.276),(.129,-.036,1.277),.065),
 ]:arms|=_segment(c,a,b,r)
 role[arms&~vessel&~basket&(area<.012)]='village_skin'
 # Both long garment hems end above the individually bounded lower legs.
 leftleg=(x<-.075)&(y>-.260)&(y<.245)&(z<.505)
 rightleg=(x>.055)&(x<.405)&(y>-.050)&(y<.375)&(z<.530)
 role[(leftleg|rightleg)&(zmax<.560)]='village_skin'
 shoes=(leftleg|rightleg)&(z<.090)
 role[shoes]='village_sandals'
 return role

def build_assignments(bpy):
 result={}
 for name,build,default in [('NB_village_house',_house,'village_plaster'),('NB_village_market',_market,'village_wood'),('NB_village_citizens',_citizens,'village_linen')]:
  ob=bpy.data.objects.get(name)
  if ob is None or ob.type!='MESH':continue
  if len(ob.data.polygons)!=EXPECTED[name]:raise ValueError('Use original normalized village topology before correction: '+name)
  v,c,n,a,zmin,zmax=_geometry(ob);roles=build(v,c,n,a,zmin,zmax);faces={r:_ids(roles==r)for r in sorted(set(roles))if r!=default}
  all_ids=[i for ids in faces.values()for i in ids]
  assert len(all_ids)==len(set(all_ids))
  result[name]={'default':default,'faces':faces,'notes':{
   'local_bbox':[v.min(0).tolist(),v.max(0).tolist()],
   'source_face_count':EXPECTED[name],
   'face_counts':{r:int(np.count_nonzero(roles==r))for r in sorted(set(roles))},
   'actual_display_or_floor_base':False,
   'right_citizen_head_exists':False if name.endswith('citizens')else None,
   'apply_before_root_surgery_and_duplicates':True,
   'graphic_material_roles_not_verified_reconstruction':True,
  }}
 return result

def build_correction_masks(bpy):
 """Pure actual source head and vessel selections for root-owned corrections."""
 ob=bpy.data.objects.get('NB_village_citizens')
 if ob is None or ob.type!='MESH':return {}
 if len(ob.data.polygons)!=EXPECTED[ob.name]:raise ValueError('Correction masks require original citizen source topology')
 v,c,n,a,zmin,zmax=_geometry(ob);x,y,z=c.T
 masks={'left_head_for_copy':_left_head(c),'right_empty_neck_rim':(x>.12)&(x<.36)&(y>.12)&(y<.40)&(z>1.61),'amphora_for_move':_amphora(c)}
 result={}
 for label,mask in masks.items():
  ids=_ids(mask);vi=np.unique([j for i in ids for j in ob.data.polygons[i].vertices]);vv=v[vi]
  result[label]={'faces':ids,'face_count':len(ids),'bbox':[vv.min(0).tolist(),vv.max(0).tolist()],'vertex_mean':vv.mean(0).tolist()}
 return {ob.name:result}
