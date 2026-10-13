"""Read-only primary-floor, unit and intentional scaffold physical geometry audit."""
from pathlib import Path
import itertools
from collections import Counter
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

O=Path('/Users/um-yunsang/.planning/roman-concrete-narrative-20261007/village-qa')

def audit(bpy,H,report):
    source_masks=np.load(O.parent/'construction-detail/village-plan.masks.npz')
    road=source_masks['road'];water=source_masks['water'];land=source_masks['land'];W=1191;C=1684
    def objects(name):
        ob=bpy.data.objects[name]
        return ([ob] if ob.type=='MESH' else [])+[c for c in ob.children_recursive if c.type=='MESH' and not c.hide_render]
    def pts(name):return np.concatenate([H['world_coords'](o) for o in objects(name)])
    def geomtree(names):
        verts=[];faces=[]
        for n in names:
            ob=bpy.data.objects[n];p=H['world_coords'](ob);offset=len(verts);verts.extend(p.tolist());faces.extend(tuple(offset+i for i in f.vertices) for f in ob.data.polygons)
        p=np.asarray(verts);return BVHTree.FromPolygons([Vector(v) for v in verts],faces),p
    def hull(p):
        q=sorted(set(map(tuple,p.tolist())))
        if len(q)<3:return q
        def cross(a,b,c):return(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
        lo=[];hi=[]
        for v in q:
            while len(lo)>1 and cross(lo[-2],lo[-1],v)<=0:lo.pop()
            lo.append(v)
        for v in reversed(q):
            while len(hi)>1 and cross(hi[-2],hi[-1],v)<=0:hi.pop()
            hi.append(v)
        return lo[:-1]+hi[:-1]
    def mask(poly):
        out=np.zeros((C,W),dtype=bool)
        if len(poly)<3:return out
        a=np.asarray(poly);x0=max(0,int(np.floor(a[:,0].min())));x1=min(W-1,int(np.ceil(a[:,0].max())));y0=max(0,int(np.floor(a[:,1].min())));y1=min(C-1,int(np.ceil(a[:,1].max())))
        if x1<x0 or y1<y0:return out
        yy,xx=np.mgrid[y0:y1+1,x0:x1+1];xx=xx+.5;yy=yy+.5;inside=np.zeros(xx.shape,dtype=bool)
        prev=a[-1]
        for point in a:
            if point[1]!=prev[1]:
                crossing=((point[1]>yy)!=(prev[1]>yy))&(xx<(prev[0]-point[0])*(yy-point[1])/(prev[1]-point[1])+point[0]);inside^=crossing
            prev=point
        out[y0:y1+1,x0:x1+1]=inside;return out
    terrain,_=geomtree(['T_land']);col,colp=geomtree(['COL_ruined'])
    floor_rows=[];floor_errors=[];unit_errors=[];units=[];collisions=[];trees={};stage_names=[]
    placements=report['village']['placements']
    for r in placements:
        name=r['name'];p=pts(name);stage_names.append(name);height=float(np.ptp(p[:,2]));lo=float(p[:,2].min())
        tolerance=max(.045,height*.02);q=p[p[:,2]<lo+tolerance];uv=H['project_pts'](q);poly=hull(uv);m=mask(poly)
        samples=q[::max(1,len(q)//200)];gaps=[]
        for v in samples:
            hit=terrain.ray_cast(Vector((float(v[0]),float(v[1]),100)),Vector((0,0,-1)),200)
            if hit[0] is not None:gaps.append(float(v[2]-hit[0].z))
        entry={'name':name,'source_anchor':r['anchor'],'actual_low_vertex_mean_pixel':H['project_pts']([q.mean(0)])[0].tolist(),'world_height':height,'world_lowZ':lo,'low_band_vertices':len(q),'low_band_threshold_world':tolerance,'floor_hull':poly,'road_pixels':int((m&road).sum()),'water_pixels':int((m&water).sum()),'outside_terrain_pixels':int((m&~land).sum()),'ground_gap_min':min(gaps) if gaps else None,'ground_gap_median':float(np.median(gaps)) if gaps else None,'ground_gap_max':max(gaps) if gaps else None}
        floor_rows.append(entry)
        if entry['road_pixels'] or entry['water_pixels'] or entry['outside_terrain_pixels']:floor_errors.append(entry)
        expected=r['world_height'];units.append({'name':name,'actual_world_height':height,'reported_world_height':expected})
        if abs(height-expected)>.002:unit_errors.append({'name':name,'error':'report height differs from fresh geometry','actual':height,'reported':expected})
        if name.startswith(('NB_worker','NB_village_citizens','V_citizens')) and not (2.3-.02<=height<=3.0+.02):unit_errors.append({'name':name,'error':'human group height outside2.3–3.0world','actual':height})
        if name.startswith(('NB_village_house','V_house_')) and not (3.8-.02<=height<=6+.02):unit_errors.append({'name':name,'error':'house height outside3.8–6world (newW3.9authorized)','actual':height})
        gt,gp=geomtree([o.name for o in objects(name)]);trees[name]=(gt,gp)
        coarse=bool(np.all(gp.max(0)>=colp.min(0)) and np.all(colp.max(0)>=gp.min(0)))
        ol=gt.overlap(col) if coarse else []
        if ol:collisions.append({'name':name,'COL_surface_overlap_pair_count':len(ol),'examples':ol[:8]})
    # Ground paving patches are true floor polygons, not a figure's bbox proxy.
    patches=[]
    for o in bpy.data.objects:
        if o.type!='MESH' or o.hide_render:continue
        n=o.name
        if n.startswith('V_house_courtyard_') or n in ['V_market_ground','V_making_ground','V_sw_workyard','V_se_workyard','V_research_ground']:
            p=H['world_coords'](o);uv=H['project_pts'](p);m=np.zeros((C,W),dtype=bool)
            for f in o.data.polygons:m|=mask([tuple(v) for v in uv[list(f.vertices)]])
            entry={'name':n,'floor_hull':hull(uv),'road_pixels':int((m&road).sum()),'water_pixels':int((m&water).sum()),'outside_terrain_pixels':int((m&~land).sum())};patches.append(entry)
            if entry['road_pixels'] or entry['water_pixels'] or entry['outside_terrain_pixels']:floor_errors.append(entry)
    scaffold_errors=[];scaffolds=[]
    for r in report['village']['scaffolds']:
        wp=pts(r['worker']);height=float(np.ptp(wp[:,2]));low=float(wp[:,2].min());co=Vector(r['actual_surface_point']);hit=col.find_nearest(co)
        support_names=[c.name for c in bpy.data.objects[r['scaffold']].children_recursive if c.type=='MESH'];support,sp=geomtree(support_names)
        near=wp[wp[:,2]<low+.03];dist=[]
        for v in near[::max(1,len(near)//200)]:
            # Ray may hit the intended platform below the actual worker sole.
            q=support.ray_cast(Vector((float(v[0]),float(v[1]),float(v[2]+.1))),Vector((0,0,-1)),10)
            if q[0] is not None:dist.append(float(v[2]-q[0].z))
        row={'scaffold':r['scaffold'],'worker':r['worker'],'human_world_height':height,'facade_record_distance_to_actual_surface':float(hit[3]) if hit[0] is not None else None,'platform_level':r['platform_level'],'worker_world_lowZ':low,'expected_worker_lowZ':r['platform_level']+.065,'worker_lowZ_error':low-(r['platform_level']+.065),'closest_support_vertical_gap':min(dist) if dist else None,'support_hits':len(dist),'support_lowZ':float(sp[:,2].min()),'note':'Scaffold/worker intentional COL attachment exempt from global zero-collision rule.'};scaffolds.append(row)
        if abs(height-2.4)>.01:scaffold_errors.append({'worker':r['worker'],'error':'worker height differs from2.4world','actual':height})
        if hit[0] is None or hit[3]>.005:scaffold_errors.append({'scaffold':r['scaffold'],'error':'facade point not on COL surface'})
        if abs(row['worker_lowZ_error'])>.015:scaffold_errors.append({'worker':r['worker'],'error':'worker sole not at intended platform height','actual':row['worker_lowZ_error']})
        if not dist:scaffold_errors.append({'worker':r['worker'],'error':'no platform support ray under sampled lowest soles'})
    abstract_names=[o.name for o in bpy.data.objects if o.name.startswith(('NB_lime_clast_specimen','NB_core4_sequence'))]
    abstract_hidden=all(bpy.data.objects[n].hide_render for n in abstract_names) and not any(n in bpy.data.objects for n in ['NB_detail_calcium_clast','NB_detail4_micro','NB_detail4_matrix','NB_detail4_crack','NB_detail4_crystal'])
    laboratory_errors=[]
    old=bpy.data.objects['S_lab_island'];lab=bpy.data.objects['V_grounded_research_building']
    counts=lambda ob:dict(Counter(ob.data.materials[p.material_index].get('semantic_role') for p in ob.data.polygons))
    before=counts(old);actual=counts(lab);expected={k:v for k,v in before.items() if k!='base'}
    if actual!=expected:laboratory_errors.append({'error':'copy must retain building labstone/roof/glass faces and remove only rock/base faces','original_role_counts':before,'expected':expected,'actual':actual})
    if not old.hide_render:laboratory_errors.append({'error':'original laboratory display-island should be hidden'})
    laboratory={'original_name':old.name,'original_hidden':old.hide_render,'target_name':lab.name,'original_role_counts':before,'expected_role_counts':expected,'actual_role_counts':actual,'NB_modern_lab_exists':'NB_modern_lab' in bpy.data.objects}
    return {'actual_primary_floors':floor_rows,'paving_patch_floors':patches,'floor_constraint_errors':floor_errors,'natural_unit_measurements':units,'unit_errors':unit_errors,'freestanding_col_surface_intersections':collisions,'attached_scaffolds':scaffolds,'scaffold_errors':scaffold_errors,'abstract_models_retired':abstract_hidden,'source_abstract_model_names':abstract_names,'laboratory':laboratory,'laboratory_errors':laboratory_errors,'method':'Fresh saved world geometry; actual low-band vertex convex hulls and ground-paving polygon raster masks intersect unchanged road/water/terrain projections. Exact world heights recomputed; independent COLBVH surface overlaps on freestanding groups only. Intentional scaffold facade/support contact assessed using COLsurface distance, worker sole level and support rays. Terrain-height under lowvertex samples reported; bbox projection not used as physical contact proof.'}
