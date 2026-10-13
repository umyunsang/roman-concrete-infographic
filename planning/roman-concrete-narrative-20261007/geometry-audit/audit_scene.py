"""Read-only scene geometry audit; writes evidence JSON only, never bpy data."""
import hashlib
import importlib.util
import json
import math
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path('/Users/um-yunsang/.planning/roman-concrete-narrative-20261007/geometry-audit')
HELPER = Path('/Users/um-yunsang/Documents/로마콘크리트_3D/narrative_benchmark_20261007/scripts/integrate_assets.py')
spec = importlib.util.spec_from_file_location('integrate_assets_audit', HELPER)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
scene = bpy.context.scene

def visible(ob):
    return not ob.hide_render and any(not c.hide_render for c in ob.users_collection)

def category(ob):
    collections = {c.name for c in ob.users_collection}
    if ob.name.startswith('NB_'): return 'narrative'
    if '60_TREES' in collections: return 'trees'
    if '30_TERRAIN' in collections: return 'terrain_water'
    if '35_FIELDS_ROADS' in collections: return 'fields_roads'
    if '40_REGION' in collections: return 'support_region'
    if '45_CORE_SCENES' in collections: return 'core'
    if '20_LANDMARK' in collections: return 'hero'
    if '50_DETAIL_MODEL' in collections: return 'detail'
    if collections & {'80_SHAPES','81_NOSHADOW','85_HEADER'}: return 'overlay_mesh'
    return 'other'

cache = {}
inventory = []
for ob in sorted(scene.objects, key=lambda o:o.name):
    info = dict(name=ob.name, type=ob.type, category=category(ob),
                render_visible=visible(ob), hide_viewport=ob.hide_viewport,
                collections=[c.name for c in ob.users_collection],
                parent=ob.parent.name if ob.parent else None,
                children=[c.name for c in ob.children],
                location=list(ob.location), world_origin=list(ob.matrix_world.translation),
                scale=list(ob.scale), rotation_z_degrees=math.degrees(ob.rotation_euler.z))
    if ob.type == 'MESH' and visible(ob):
        ev = ob.evaluated_get(dg)
        mesh = ev.to_mesh()
        try:
            local = np.empty(len(mesh.vertices)*3,dtype=np.float64)
            mesh.vertices.foreach_get('co',local)
            local=local.reshape(-1,3)
            mat=np.array(ob.matrix_world)
            pts=local@mat[:3,:3].T+mat[:3,3]
            polys=[list(p.vertices) for p in mesh.polygons]
            uv=helper.project_pts(pts)
            info.update(world_min=pts.min(0).tolist(), world_max=pts.max(0).tolist(),
                        world_z_min=float(pts[:,2].min()),world_z_max=float(pts[:,2].max()),
                        projected_bbox=[float(uv[:,0].min()),float(uv[:,1].min()),float(uv[:,0].max()),float(uv[:,1].max())],
                        vertex_count=len(mesh.vertices),face_count=len(mesh.polygons))
            cache[ob.name]={'pts':pts,'polys':polys,'info':info}
        finally: ev.to_mesh_clear()
    inventory.append(info)

def bvh(name):
    item=cache[name]
    if 'bvh' not in item:
        item['bvh']=BVHTree.FromPolygons([Vector(v) for v in item['pts']],item['polys'])
    return item['bvh']

def bbox_overlap(a,b,pad=0):
    low=np.maximum(np.array(a[:2]),np.array(b[:2]))
    high=np.minimum(np.array(a[2:]),np.array(b[2:]))
    wh=np.maximum(0,high-low)
    return {'area':float(np.prod(wh)), 'bbox':[*low.tolist(),*high.tolist()]} if np.all(wh>0) else None

def physical_overlap(a,b):
    aa,bb=cache[a]['info'],cache[b]['info']
    low=np.maximum(aa['world_min'],bb['world_min'])
    high=np.minimum(aa['world_max'],bb['world_max'])
    if np.any(high<low): return None
    overlaps=bvh(a).overlap(bvh(b))
    return dict(a=a,b=b,world_aabb_intersection=[low.tolist(),high.tolist()],
                crossing_polygon_pair_count=len(overlaps),
                crossing_polygon_pairs_first20=overlaps[:20],
                screen=bbox_overlap(aa['projected_bbox'],bb['projected_bbox']))

support_names=[n for n in ['T_land','L10_sea','L02_tiber','F_centuriatio','R_core_road','R_via_appia','R_via_ostiensis'] if n in cache]
def support_ray(x,y):
    hits=[]
    for name in support_names:
        co,normal,index,distance=bvh(name).ray_cast(Vector((x,y,10000)),Vector((0,0,-1)),20000)
        if co is not None: hits.append({'name':name,'z':float(co.z),'face':index})
    return sorted(hits,key=lambda x:-x['z'])

contacts=[]
target_names=[n for n,x in cache.items() if x['info']['category'] in {'narrative','core','trees','support_region','hero'} and not n.startswith('NB_lime_clast_specimen_LIME') and not n.startswith('NB_core4_sequence_GRAY')]
for name in target_names:
    item=cache[name]; pts=item['pts']; zmin=pts[:,2].min(); zmax=pts[:,2].max()
    low=pts[pts[:,2]<=zmin+max(.02,(zmax-zmin)*.005)]
    step=max(1,len(low)//150)
    sample=low[::step][:151]
    origin=item['info']['world_origin']
    origin_hits=support_ray(origin[0],origin[1])
    bottom_samples=[]
    for p in sample:
        hits=support_ray(p[0],p[1])
        land=next((h for h in hits if h['name']=='T_land'),None)
        sea=next((h for h in hits if h['name']=='L10_sea'),None)
        if land or sea:
            bottom_samples.append({'point':p.tolist(),'land_gap':float(p[2]-land['z']) if land else None,
                                   'sea_gap':float(p[2]-sea['z']) if sea else None,
                                   'top_support':hits[0]})
    land_gaps=[p['land_gap'] for p in bottom_samples if p['land_gap'] is not None]
    sea_gaps=[p['sea_gap'] for p in bottom_samples if p['sea_gap'] is not None]
    contacts.append({'name':name,'origin_support_hits':origin_hits,
                     'bottom_sample_count':len(sample),'bottom_support_count':len(bottom_samples),
                     'land_gap_min_max': [min(land_gaps),max(land_gaps)] if land_gaps else None,
                     'sea_gap_min_max': [min(sea_gaps),max(sea_gaps)] if sea_gaps else None,
                     'bottom_samples':bottom_samples[:20]})

intersections=[]
modern='NB_modern_building'
for name,item in cache.items():
    if name != modern and item['info']['category'] in {'trees','fields_roads','terrain_water','support_region'}:
        physical=physical_overlap(modern,name)
        if physical: intersections.append(physical)

screen_neighbors={}
for main in ['NB_modern_building','NB_lime_clast_specimen','NB_marine_breakwater','COL_ruined','C2_hot_mixing','C5_researchers','L11_privernum_wall','S_lab_island','L08_pompeii_site']:
    if main not in cache: continue
    neighbors=[]
    for name,item in cache.items():
        if main==name or item['info']['category'] in {'overlay_mesh','terrain_water','other'}:continue
        if item['info']['parent']==main:continue
        overlap=bbox_overlap(cache[main]['info']['projected_bbox'],item['info']['projected_bbox'])
        if overlap: neighbors.append({'name':name,**overlap})
    screen_neighbors[main]=sorted(neighbors,key=lambda x:-x['area'])

# Connected pieces of merged field object identify precisely which geometry crowding is local.
field_components=[]
if 'F_centuriatio' in cache:
    item=cache['F_centuriatio'];pts=item['pts'];polys=item['polys']
    parent=list(range(len(pts)))
    def find(v):
        while parent[v]!=v:
            parent[v]=parent[parent[v]];v=parent[v]
        return v
    def union(a,b):
        aa,bb=find(a),find(b)
        if aa!=bb:parent[bb]=aa
    for poly in polys:
        for v in poly[1:]:union(poly[0],v)
    groups={}
    for i in range(len(pts)):groups.setdefault(find(i),[]).append(i)
    for idx,indices in enumerate(groups.values()):
        p=pts[indices];uv=helper.project_pts(p)
        bb=[float(uv[:,0].min()),float(uv[:,1].min()),float(uv[:,0].max()),float(uv[:,1].max())]
        if bbox_overlap(bb,cache[modern]['info']['projected_bbox']):
            field_components.append({'component_id':idx,'vertex_indices':indices,'world_min':p.min(0).tolist(),
                                     'world_max':p.max(0).tolist(),'projected_bbox':bb})

report={'source_file':bpy.data.filepath,'source_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
        'poster_frame':[1191,1684],'camera':scene.camera.name,'camera_type':scene.camera.data.type,
        'inventory':inventory,'main_contacts':contacts,'modern_physical_candidates':intersections,
        'screen_neighbors':screen_neighbors,'modern_field_components':field_components}
(ROOT/'scene_inventory.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('AUDIT_COMPLETE',len(inventory),'objects;',len(cache),'visible meshes;',len(intersections),'physical candidates')
for n in ['NB_modern_building','NB_lime_clast_specimen','NB_marine_breakwater','T_land','L10_sea']:
    print('BOUNDS',n,json.dumps(cache[n]['info'],ensure_ascii=False))
for x in intersections:
    print('INTERSECTION',x['b'],x['crossing_polygon_pair_count'],x['screen'])
for x in contacts:
    if x['name'] in ['NB_modern_building','NB_lime_clast_specimen','NB_marine_breakwater']:
        print('CONTACT',x['name'],x['land_gap_min_max'],x['sea_gap_min_max'],x['origin_support_hits'])
