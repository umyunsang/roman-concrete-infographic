"""Saved-v11 world geometry audit, read-only. No operators/mutations/renders."""
import itertools
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

STAGES=['C2_hot_mixing','NB_worker_carrier','NB_vault_construction','NB_worker_builder','NB_worker_pair','NB_vault_complete']
GROUND=['T_land','R_core_road','B_pons1','B_pons2']
ROADS=['R_core_road','B_pons1','B_pons2']

def audit(bpy,H):
    def group(name):
        o=bpy.data.objects[name]
        return ([o] if o.type=='MESH' else [])+[c for c in o.children_recursive if c.type=='MESH' and not c.hide_render]
    def geometry(names):
        verts=[];faces=[];ranges=[];offset=0
        for name in names:
            o=bpy.data.objects[name];a=H['world_coords'](o);verts.extend(a.tolist())
            faces.extend(tuple(offset+i for i in p.vertices) for p in o.data.polygons)
            ranges.append((name,offset,offset+len(a)));offset+=len(a)
        arr=np.asarray(verts,dtype=np.float64)
        return arr,faces,ranges
    def tree(names):
        arr,faces,ranges=geometry(names)
        return {'tree':BVHTree.FromPolygons([Vector(p) for p in arr],faces,all_triangles=False,epsilon=0.0),'points':arr,'ranges':ranges,'bbox':[arr.min(axis=0).tolist(),arr.max(axis=0).tolist()]}
    ground=tree(GROUND);roads=tree(ROADS);individual={n:tree([n]) for n in GROUND}
    groups={n:tree([o.name for o in group(n)]) for n in STAGES+['COL_ruined']}
    contacts=[]
    for name in STAGES:
        a=groups[name]['points'];low=float(a[:,2].min());height=float(a[:,2].max()-low)
        near=a[a[:,2]<low+height*.02+.001];sample=near[::max(1,len(near)//500)]
        checks=[]
        for p in sample:
            # Vertical ground height is independent of body-bbox proxy.
            hit=ground['tree'].ray_cast(Vector((float(p[0]),float(p[1]),100)),Vector((0,0,-1)),200)
            rd=roads['tree'].find_nearest(Vector(p))
            surface=None
            if hit[0] is not None:
                h=float(hit[0].z)
                on=[]
                for gn,gd in individual.items():
                    r=gd['tree'].ray_cast(Vector((float(p[0]),float(p[1]),100)),Vector((0,0,-1)),200)
                    if r[0] is not None and abs(float(r[0].z)-h)<1e-4:on.append(gn)
                surface={'worldZ':h,'verticalGap':float(p[2]-h),'objects':on}
            road=None
            if rd[0] is not None:
                uv=H['project_pts']([p,np.array(rd[0])])
                road={'world_distance':float(rd[3]),'projected_distance_px':float(np.linalg.norm(uv[0]-uv[1])),'nearest_world':list(rd[0]),'vertex_pixel':uv[0].tolist(),'nearest_pixel':uv[1].tolist()}
            checks.append({'world':p.tolist(),'surface':surface,'road':road})
        valid=[x for x in checks if x['surface']]
        rd=[x for x in checks if x['road']]
        closest=min(rd,key=lambda x:x['road']['world_distance']) if rd else None
        contact=min(valid,key=lambda x:abs(x['surface']['verticalGap'])) if valid else None
        gaps=[x['surface']['verticalGap'] for x in valid]
        contacts.append({'object':name,'group_meshes':[o.name for o in group(name)],'world_height':height,'world_lowZ':low,'low_band_vertex_count':len(near),'sample_count':len(sample),'ground_hits':len(valid),'min_gap':min(gaps) if gaps else None,'median_gap':float(np.median(gaps)) if gaps else None,'max_gap':max(gaps) if gaps else None,'closest_ground_vertex':contact,'closest_road_vertex':closest,'ground_penetration_beyond_0_002':any(g<-.002 for g in gaps)})
    collisions=[]
    def coarse(a,b):return np.all(a['points'].max(axis=0)>=b['points'].min(axis=0)) and np.all(b['points'].max(axis=0)>=a['points'].min(axis=0))
    pairs=[(s,'COL_ruined') for s in STAGES]+list(itertools.combinations(STAGES,2))
    for a,b in pairs:
        ga,gb=groups[a],groups[b]
        candidate=bool(coarse(ga,gb));overlap=ga['tree'].overlap(gb['tree']) if candidate else []
        collisions.append({'a':a,'b':b,'worldAABB_overlaps':candidate,'surface_triangle_overlap_pair_count':len(overlap),'surface_triangle_overlap_examples':[list(p) for p in overlap[:8]]})
    crack=bpy.data.objects['NB_detail4_crack'];fill=bpy.data.objects['NB_detail4_crystal']
    ca=H['world_coords'](crack);fa=H['world_coords'](fill)
    inverse=np.linalg.inv(np.asarray(bpy.context.scene.camera.matrix_world));cz=(ca@inverse[:3,:3].T+inverse[:3,3])[:,2];fz=(fa@inverse[:3,:3].T+inverse[:3,3])[:,2]
    same=H['mesh_fingerprint'](crack.data)==H['mesh_fingerprint'](fill.data)
    delta=fz-cz if cz.shape==fz.shape else np.asarray([])
    uvc=H['project_pts'](ca);uvf=H['project_pts'](fa)
    roles=[m.get('semantic_role') for m in fill.data.materials]
    micro={'geometry_sha256_equal':same,'camera_depth_delta_min':float(delta.min()) if len(delta) else None,'camera_depth_delta_max':float(delta.max()) if len(delta) else None,'projected_vertex_max_delta_px':float(np.linalg.norm(uvf-uvc,axis=1).max()) if uvc.shape==uvf.shape else None,'fill_roles':roles,'pass':same and len(delta)>0 and bool(np.all(delta>0)) and roles==['base_lime_calcium_crystal']}
    return {'contacts':contacts,'collisions':collisions,'micro_fill':micro,'method':'World-space exact mesh vertices and BVH polygon surfaces. Low2percent vertex band matches production planting policy; vertical ground rays and closest-road3D distance independently measured. Triangle-surface overlap is a collision indicator, not a closed-solid interior proof; finite surface/no intersection does not prove invisible volume interiors. No scene mutation.'}
