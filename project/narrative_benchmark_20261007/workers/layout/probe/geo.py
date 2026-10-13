import bpy, numpy as np, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; cam=sc.camera; O=bpy.data.objects
W_PT,H_PT=1191,1684
print('CAM', cam.data.type, cam.data.lens, cam.data.ortho_scale, tuple(round(x,3) for x in cam.matrix_world.translation), tuple(round(math.degrees(a),3) for a in cam.matrix_world.to_euler()))
def to_pt(p):
    v=world_to_camera_view(sc,cam,p); return np.array((v.x*W_PT,(1-v.y)*H_PT))
frame=[cam.matrix_world@v for v in cam.data.view_frame(scene=sc)]
origin=cam.matrix_world.translation
dg=bpy.context.evaluated_depsgraph_get()
def bvh_of(objs):
    verts,polys=[],[]
    for o in objs:
        ev=o.evaluated_get(dg); me=ev.to_mesh(); mw=o.matrix_world; b=len(verts)
        verts+=[mw@v.co for v in me.vertices]; polys+=[[b+i for i in p.vertices] for p in me.polygons]; ev.to_mesh_clear()
    return BVHTree.FromPolygons(verts,polys)
TER=bvh_of([O['T_land']])
def tz(x,y):
    h=TER.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))[0]; return h.z if h else float('nan')
col=O['COL_ruined']; mw=col.matrix_world
W=np.array([(mw@v.co)[:] for v in col.data.vertices])
print('COL loc',tuple(col.location),'rot',tuple(col.rotation_euler),'scale',tuple(col.scale))
print('COL world min',W.min(0).round(3),'max',W.max(0).round(3))
cx,cy=(W[:,0].min()+W[:,0].max())/2,(W[:,1].min()+W[:,1].max())/2
print('center',cx,cy,'tz',tz(cx,cy))
r=cam.matrix_world.col[0].xyz.normalized()
p=Vector((cx,cy,tz(cx,cy))); print('world_per_pt',1/np.linalg.norm(to_pt(p+r)-to_pt(p)))
# terrain grid in the footprint (old)
xs=np.linspace(W[:,0].min()-3,W[:,0].max()+3,15); ys=np.linspace(W[:,1].min()-3,W[:,1].max()+3,15)
G=np.array([[tz(x,y) for x in xs] for y in ys])
np.set_printoptions(linewidth=200,precision=2,suppress=True)
print('xs',xs.round(1)); print('ys',ys.round(1)); print(G)
# COL lowest vertices relative to terrain
rel=np.array([W[i,2]-tz(W[i,0],W[i,1]) for i in range(0,len(W),7)])
print('COL rel z percentiles',np.percentile(rel,[0,1,5,10,25,50]).round(3))
pod=O['R3_colosseum_podium']; pm=pod.matrix_world; PV=np.array([(pm@v.co)[:] for v in pod.data.vertices])
N=len(PV)//3
for j in range(3):
    R=np.array([PV[3*k+j,2]-tz(PV[3*k+j,0],PV[3*k+j,1]) for k in range(N)])
    print('POD idx',j,'rel z min/med/max',R.min().round(3),np.median(R).round(3),R.max().round(3))
print('POD polys',len(pod.data.polygons),'verts',len(PV), 'mats',[m.name for m in pod.data.materials])
print('first poly verts',[list(p.vertices) for p in pod.data.polygons[:4]])
ar=O['R4_arena_skin']; am=ar.matrix_world; AV=np.array([(am@v.co)[:] for v in ar.data.vertices])
R=np.array([AV[i,2]-tz(AV[i,0],AV[i,1]) for i in range(len(AV))])
print('ARENA rel z',np.percentile(R,[0,5,50,95,100]).round(3),'world z',AV[:,2].min().round(3),AV[:,2].max().round(3))
for n in ['R_core_road','R_via_appia','R_via_ostiensis','MS1_core1_to_2','MS2_core2_to_34','MS3_core34_to_5','NB_modern_building','R8_pantheon','R1_road_landing1','B_pons1','T_cypress','L05_aqua_claudia','F_centuriatio']:
    o=O[n]; print('OBJ',n,'users',o.data.users,'loc',tuple(round(x,3) for x in o.location),'mods',[m.type for m in o.modifiers], 'parent', o.parent.name if o.parent else None, 'children',[c.name for c in o.children][:5])
for n in ['COL_ruined','R3_colosseum_podium','R4_arena_skin']:
    o=O[n]; print('GRP',n,'users',o.data.users,'mods',[m.type for m in o.modifiers],'parent',o.parent.name if o.parent else None,'children',[c.name for c in o.children][:5], 'constraints', [c.type for c in o.constraints], 'anim', o.animation_data)
